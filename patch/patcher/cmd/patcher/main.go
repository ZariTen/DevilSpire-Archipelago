// devilspire_ap_patcher - patches Devil Spire's data.win in place for the (fan-made) Archipelago integration.
// Touches only data.win and data.win.orig (plus a short-lived data.win.ap-tmp that is always removed).
package main

import (
	"bufio"
	_ "embed"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"

	"devilspire-ap-patcher/delta"
)

//go:embed delta.bin
var deltaBin []byte

var version = "dev" // set with -ldflags "-X main.version=..."

const (
	exitOK          = 0
	exitUsage       = 1
	exitNoDataWin   = 2
	exitBadVersion  = 3
	exitAlready     = 4 // already patched / backup conflict
	exitIO          = 5
	exitBackupProbs = 6 // restore: backup missing or not the original
)

type fail struct {
	code int
	msg  string
}

func (f *fail) Error() string { return f.msg }
func failf(code int, format string, a ...any) *fail {
	return &fail{code, fmt.Sprintf(format, a...)}
}

func sha(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

func exists(p string) bool { _, err := os.Lstat(p); return err == nil }

func ioFail(what string, err error) *fail {
	hint := ""
	if errors.Is(err, os.ErrPermission) {
		hint = "\n  Permission denied. Make sure the game is closed and the game folder is writable (on Windows, try moving the game out of 'Program Files' or run as administrator)."
	}
	return failf(exitIO, "ERROR: %s: %v%s\n  Nothing was changed in data.win.", what, err, hint)
}

type ctx struct {
	dir, dataWin, backup, tmp string
	hdr                       delta.Header
	origHash, patchedHash     string
}

func main() {
	args := os.Args[1:]
	pause := runtime.GOOS == "windows" && len(args) == 0
	dir := ""
	var cmd string
	for i := 0; i < len(args); i++ {
		switch a := args[i]; a {
		case "--dir":
			if i+1 >= len(args) {
				finish(failf(exitUsage, "--dir needs a path"), false)
			}
			dir = args[i+1]
			i++
		case "--no-pause":
			pause = false
		case "-h", "--help", "help":
			cmd = "help"
		case "-v", "--version", "version":
			cmd = "version"
		case "patch", "status", "restore":
			cmd = a
		default:
			finish(failf(exitUsage, "unknown argument %q. Run with 'help' for usage.", a), false)
		}
	}
	if cmd == "" {
		cmd = "patch"
	}
	if cmd == "help" {
		usage()
		return
	}
	hdr, _, err := delta.ParseHeader(deltaBin)
	if err != nil {
		finish(failf(exitIO, "internal error: %v", err), pause)
	}
	if cmd == "version" {
		fmt.Printf("devilspire_ap_patcher %s\n  original data.win sha256: %x\n  patched  data.win sha256: %x\n", version, hdr.SrcSHA, hdr.DstSHA)
		return
	}
	if dir == "" {
		if exe, err := os.Executable(); err == nil {
			dir = filepath.Dir(exe)
		} else {
			dir, _ = os.Getwd()
		}
	}
	c := &ctx{dir: dir, hdr: hdr,
		origHash: hex.EncodeToString(hdr.SrcSHA[:]), patchedHash: hex.EncodeToString(hdr.DstSHA[:])}
	c.dataWin = filepath.Join(dir, "data.win")
	c.backup = c.dataWin + ".orig"
	c.tmp = c.dataWin + ".ap-tmp"
	fmt.Printf("Devil Spire Archipelago patcher %s (fan-made, unofficial)\nGame folder: %s\n\n", version, dir)
	var ferr *fail
	switch cmd {
	case "patch":
		ferr = c.patch()
	case "status":
		ferr = c.status()
	case "restore":
		ferr = c.restore()
	}
	finish(ferr, pause)
}

func finish(f *fail, pause bool) {
	code := 0
	if f != nil {
		fmt.Fprintln(os.Stderr, f.msg)
		code = f.code
	}
	if pause {
		fmt.Print("\nPress Enter to close this window...")
		bufio.NewReader(os.Stdin).ReadString('\n')
	}
	os.Exit(code)
}

func usage() {
	fmt.Print(`devilspire_ap_patcher - Archipelago patch for Devil Spire (fan-made, unofficial)

Put this file in your Devil Spire folder (next to data.win) and run it.

  devilspire_ap_patcher            patch data.win (same as 'patch')
  devilspire_ap_patcher patch      patch data.win; the original is saved as data.win.orig
  devilspire_ap_patcher status     show whether data.win is original, patched or unknown
  devilspire_ap_patcher restore    put the original data.win back (uninstall)
  devilspire_ap_patcher version    print version and the supported data.win checksums

Options: --dir PATH  use another game folder; --no-pause  do not wait for Enter at the end (Windows).
Exit codes: 0 ok, 1 usage, 2 data.win not found, 3 unsupported/unknown data.win, 4 already patched or backup
conflict, 5 file/permission error, 6 backup missing or invalid.
`)
}

type state int

const (
	stOriginal state = iota
	stPatched
	stUnknown
)

func (c *ctx) classify() (state, string, *fail) {
	if !exists(c.dataWin) {
		return 0, "", failf(exitNoDataWin, "ERROR: data.win not found in %s\n  Put this program in the Devil Spire game folder, next to data.win\n  (Steam: right-click Devil Spire > Manage > Browse local files).", c.dir)
	}
	h, err := sha(c.dataWin)
	if err != nil {
		return 0, "", ioFail("cannot read data.win", err)
	}
	switch h {
	case c.origHash:
		return stOriginal, h, nil
	case c.patchedHash:
		return stPatched, h, nil
	}
	return stUnknown, h, nil
}

func (c *ctx) backupState() (string, bool) { // description, isOriginal
	if !exists(c.backup) {
		return "missing", false
	}
	h, err := sha(c.backup)
	if err != nil {
		return "unreadable (" + err.Error() + ")", false
	}
	if h == c.origHash {
		return "present, valid original", true
	}
	return "present, but NOT the expected original", false
}

func (c *ctx) status() *fail {
	st, h, f := c.classify()
	if f != nil {
		return f
	}
	b, _ := c.backupState()
	fmt.Printf("data.win sha256: %s\n", h)
	switch st {
	case stOriginal:
		fmt.Println("Status:  NOT patched (original, supported version).")
	case stPatched:
		fmt.Println("Status:  PATCHED (Archipelago patch is installed).")
	default:
		fmt.Printf("Status:  UNKNOWN data.win (not the supported original, not patched by this tool).\n  Expected original: %s\n", c.origHash)
	}
	fmt.Printf("Backup:  data.win.orig is %s.\n", b)
	if st == stUnknown {
		return failf(exitBadVersion, "")
	}
	return nil
}

func (c *ctx) patch() *fail {
	st, h, f := c.classify()
	if f != nil {
		return f
	}
	switch st {
	case stPatched:
		return failf(exitAlready, "Already patched - nothing to do.\n  To go back to the original game files run:  devilspire_ap_patcher restore")
	case stUnknown:
		extra := ""
		if bs, ok := c.backupState(); ok {
			extra = "\n  A valid backup (data.win.orig) exists: run 'restore' first, then patch again."
		} else if bs != "missing" {
			extra = "\n  (data.win.orig exists but is not the original either.)"
		}
		return failf(exitBadVersion, "ERROR: this data.win is not the version this patch was made for. Nothing was changed.\n  Found:    %s\n  Expected: %s\n  Possible causes: a different/updated game build, or data.win was modified by something else.\n  Fix: in Steam use Properties > Installed Files > Verify integrity of game files, then run this again.%s", h, c.origHash, extra)
	}
	// data.win is the pristine original
	if exists(c.backup) {
		if _, ok := c.backupState(); !ok {
			return failf(exitAlready, "ERROR: data.win.orig already exists but is not the expected original data.win.\n  I will never overwrite an existing backup. Move or delete it yourself if you are sure, then run again.\n  Nothing was changed.")
		}
		fmt.Println("Backup data.win.orig already exists and is valid - keeping it.")
	} else {
		fmt.Println("Creating backup data.win.orig ...")
		if err := copyExcl(c.dataWin, c.backup); err != nil {
			os.Remove(c.backup)
			return ioFail("cannot create backup data.win.orig", err)
		}
		if bh, err := sha(c.backup); err != nil || bh != c.origHash {
			os.Remove(c.backup)
			return failf(exitIO, "ERROR: backup verification failed; backup removed. Nothing was changed in data.win.")
		}
	}
	fmt.Println("Patching data.win ...")
	if err := c.applyTo(c.dataWin, c.tmp, c.dataWin); err != nil {
		os.Remove(c.tmp)
		return ioFail("patching failed", err)
	}
	fmt.Println("\nSUCCESS: data.win is patched. The original is saved as data.win.orig.")
	fmt.Println("Next: start the 'Devil Spire Client' in Archipelago, connect, THEN start the game.")
	return nil
}

// applyTo applies the embedded delta to the file at srcPath, writing tmp and atomically renaming over dst.
func (c *ctx) applyTo(srcPath, tmp, dst string) error {
	src, err := os.Open(srcPath)
	if err != nil {
		return err
	}
	defer src.Close()
	fi, err := src.Stat()
	if err != nil {
		return err
	}
	out, err := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if err != nil {
		return err
	}
	bw := bufio.NewWriterSize(out, 1<<20)
	if err := delta.Apply(deltaBin, src, fi.Size(), bw); err != nil {
		out.Close()
		return err
	}
	if err := bw.Flush(); err != nil {
		out.Close()
		return err
	}
	if err := out.Sync(); err != nil {
		out.Close()
		return err
	}
	if err := out.Close(); err != nil {
		return err
	}
	src.Close()
	_ = os.Chmod(tmp, fi.Mode().Perm())
	return os.Rename(tmp, dst)
}

func copyExcl(from, to string) error {
	in, err := os.Open(from)
	if err != nil {
		return err
	}
	defer in.Close()
	fi, _ := in.Stat()
	out, err := os.OpenFile(to, os.O_WRONLY|os.O_CREATE|os.O_EXCL, fi.Mode().Perm())
	if err != nil {
		return err
	}
	if _, err := io.Copy(out, in); err != nil {
		out.Close()
		return err
	}
	if err := out.Sync(); err != nil {
		out.Close()
		return err
	}
	return out.Close()
}

func (c *ctx) restore() *fail {
	if !exists(c.backup) {
		return failf(exitBackupProbs, "ERROR: data.win.orig not found in %s - cannot restore.\n  Use Steam: Properties > Installed Files > Verify integrity of game files.", c.dir)
	}
	if bs, ok := c.backupState(); !ok {
		return failf(exitBackupProbs, "ERROR: data.win.orig is %s - refusing to restore it.\n  Use Steam: Properties > Installed Files > Verify integrity of game files.", bs)
	}
	if exists(c.dataWin) {
		if h, err := sha(c.dataWin); err == nil && h == c.origHash {
			fmt.Println("data.win is already the original. Removing the now-redundant backup.")
		}
	}
	fmt.Println("Restoring original data.win from data.win.orig ...")
	// rename is atomic; the backup file becomes data.win
	if err := os.Rename(c.backup, c.dataWin); err != nil {
		return ioFail("restore failed", err)
	}
	fmt.Println("\nSUCCESS: original data.win restored (data.win.orig was moved back to data.win).")
	fmt.Println("Game folder is back to its original state. You can delete this patcher.")
	return nil
}

