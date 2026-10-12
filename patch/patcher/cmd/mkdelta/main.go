// mkdelta <pristine data.win> <patched data.win> <out delta.bin>   (developer tool, used by patch/build_release.sh)
package main

import (
	"bytes"
	"fmt"
	"os"

	"devilspire-ap-patcher/delta"
)

func main() {
	if len(os.Args) != 4 {
		fmt.Fprintln(os.Stderr, "usage: mkdelta <pristine> <patched> <out>")
		os.Exit(1)
	}
	src, err1 := os.ReadFile(os.Args[1])
	dst, err2 := os.ReadFile(os.Args[2])
	if err1 != nil || err2 != nil {
		fmt.Fprintln(os.Stderr, "read error:", err1, err2)
		os.Exit(1)
	}
	d, err := delta.Create(src, dst, 24)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	// self-check
	var out bytes.Buffer
	if err := delta.Apply(d, bytes.NewReader(src), int64(len(src)), &out); err != nil || !bytes.Equal(out.Bytes(), dst) {
		fmt.Fprintln(os.Stderr, "self-check failed:", err)
		os.Exit(1)
	}
	if err := os.WriteFile(os.Args[3], d, 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("delta: %d bytes (source %d, result %d)\n", len(d), len(src), len(dst))
}
