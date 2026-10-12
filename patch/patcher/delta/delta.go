// Package delta implements a tiny copy/add binary delta format (no external deps).
//
// File layout:
//
//	magic    "DSAPDLT1"            8 bytes
//	srcSize  uint64 LE
//	srcSHA   sha256 of the source  32 bytes
//	dstSize  uint64 LE
//	dstSHA   sha256 of the result  32 bytes
//	ops      zlib stream of:  0x00 <uvarint srcOff> <uvarint len>   COPY from source
//	                          0x01 <uvarint len> <len bytes>        ADD literal bytes
package delta

import (
	"bufio"
	"bytes"
	"compress/zlib"
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"fmt"
	"hash"
	"index/suffixarray"
	"io"
)

const Magic = "DSAPDLT1"

type Header struct {
	SrcSize uint64
	SrcSHA  [32]byte
	DstSize uint64
	DstSHA  [32]byte
}

const headerLen = 8 + 8 + 32 + 8 + 32

func ParseHeader(b []byte) (Header, []byte, error) {
	var h Header
	if len(b) < headerLen || string(b[:8]) != Magic {
		return h, nil, errors.New("not a valid delta (bad magic)")
	}
	h.SrcSize = binary.LittleEndian.Uint64(b[8:])
	copy(h.SrcSHA[:], b[16:48])
	h.DstSize = binary.LittleEndian.Uint64(b[48:])
	copy(h.DstSHA[:], b[56:88])
	return h, b[headerLen:], nil
}

// Create builds a delta turning src into dst.
func Create(src, dst []byte, minMatch int) ([]byte, error) {
	var out bytes.Buffer
	out.WriteString(Magic)
	var h Header
	h.SrcSize, h.DstSize = uint64(len(src)), uint64(len(dst))
	h.SrcSHA, h.DstSHA = sha256.Sum256(src), sha256.Sum256(dst)
	var tmp [8]byte
	binary.LittleEndian.PutUint64(tmp[:], h.SrcSize)
	out.Write(tmp[:])
	out.Write(h.SrcSHA[:])
	binary.LittleEndian.PutUint64(tmp[:], h.DstSize)
	out.Write(tmp[:])
	out.Write(h.DstSHA[:])

	zw, _ := zlib.NewWriterLevel(&out, zlib.BestCompression)
	idx := suffixarray.New(src)
	var vb [binary.MaxVarintLen64]byte
	putU := func(v uint64) { n := binary.PutUvarint(vb[:], v); zw.Write(vb[:n]) }

	litStart := 0
	flushLit := func(end int) {
		if end > litStart {
			zw.Write([]byte{1})
			putU(uint64(end - litStart))
			zw.Write(dst[litStart:end])
		}
	}
	emitCopy := func(so, l int) { zw.Write([]byte{0}); putU(uint64(so)); putU(uint64(l)) }

	ext := func(so, p int) int { // forward match length
		n := 0
		for so+n < len(src) && p+n < len(dst) && src[so+n] == dst[p+n] {
			n++
		}
		return n
	}
	p, lastEnd := 0, -1
	for p < len(dst) {
		bestSrc, bestLen := -1, 0
		if lastEnd >= 0 && lastEnd < len(src) { // try to continue previous copy
			if l := ext(lastEnd, p); l >= 8 {
				bestSrc, bestLen = lastEnd, l
			}
		}
		if bestLen < minMatch && p+minMatch <= len(dst) {
			for _, c := range idx.Lookup(dst[p:p+minMatch], 16) {
				if l := ext(c, p); l > bestLen {
					bestSrc, bestLen = c, l
				}
			}
		}
		if bestLen >= minMatch || (bestLen >= 8 && bestSrc == lastEnd) {
			// extend backwards into pending literals
			for litStart < p && bestSrc > 0 && src[bestSrc-1] == dst[p-1] {
				bestSrc--
				p--
				bestLen++
			}
			flushLit(p)
			emitCopy(bestSrc, bestLen)
			p += bestLen
			litStart = p
			lastEnd = bestSrc + bestLen
		} else {
			p++
		}
	}
	flushLit(len(dst))
	zw.Close()
	return out.Bytes(), nil
}

// Apply reads source from src (random access) and writes the result to w,
// returning an error unless the output matches the sizes/hashes in the header.
func Apply(deltaBytes []byte, src io.ReaderAt, srcSize int64, w io.Writer) error {
	h, rest, err := ParseHeader(deltaBytes)
	if err != nil {
		return err
	}
	if uint64(srcSize) != h.SrcSize {
		return fmt.Errorf("source size %d does not match expected %d", srcSize, h.SrcSize)
	}
	zr, err := zlib.NewReader(bytes.NewReader(rest))
	if err != nil {
		return err
	}
	br := bufio.NewReaderSize(zr, 1<<20)
	var hs hash.Hash = sha256.New()
	mw := io.MultiWriter(w, hs)
	var written uint64
	buf := make([]byte, 1<<20)
	for {
		op, err := br.ReadByte()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}
		switch op {
		case 0:
			so, e1 := binary.ReadUvarint(br)
			l, e2 := binary.ReadUvarint(br)
			if e1 != nil || e2 != nil || so+l > h.SrcSize {
				return errors.New("corrupt delta (bad copy)")
			}
			for l > 0 {
				n := uint64(len(buf))
				if l < n {
					n = l
				}
				if _, err := src.ReadAt(buf[:n], int64(so)); err != nil {
					return fmt.Errorf("reading source: %w", err)
				}
				if _, err := mw.Write(buf[:n]); err != nil {
					return err
				}
				so += n
				l -= n
				written += n
			}
		case 1:
			l, e := binary.ReadUvarint(br)
			if e != nil {
				return errors.New("corrupt delta (bad add)")
			}
			if _, err := io.CopyN(mw, br, int64(l)); err != nil {
				return fmt.Errorf("corrupt delta (short add): %w", err)
			}
			written += l
		default:
			return errors.New("corrupt delta (bad opcode)")
		}
	}
	if written != h.DstSize {
		return fmt.Errorf("result size %d != expected %d", written, h.DstSize)
	}
	var got [32]byte
	copy(got[:], hs.Sum(nil))
	if got != h.DstSHA {
		return errors.New("result checksum mismatch")
	}
	return nil
}
