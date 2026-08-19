#!/usr/bin/env python3
"""
Standalone reproduction of DownloadTest.setup()'s data/source generation,
for manual (3-window) test runs outside gdbserver.py.

Usage:
    python3 gen_download.py <ram_size_bytes> [output.c]

Example (cclass64: ram_size = 0x4000000):
    python3 gen_download.py 0x4000000 download_test.c

Writes the C source to <output.c> (default: download_test.c) and prints
the expected CRC (the value you must see in `print status` in gdb).
"""
import sys
import random
import struct
import binascii


def generate(ram_size: int, out_path: str) -> int:
    # Same formula as DownloadTest.setup()
    length = min(2**18, max(2**10, ram_size - 2048))
    assert length % 16 == 0, "length must be a multiple of 16"

    crc = 0
    with open(out_path, "wb") as f:
        f.write(b"#include <stdint.h>\n")
        f.write(b"unsigned int crc32a(uint8_t *message, unsigned int size);\n")
        f.write(b"const uint32_t length = %d;\n" % length)
        f.write(b"const uint8_t d[%d] = {\n" % length)
        for i in range(length // 16):
            f.write(f"  /* 0x{i * 16:04x} */ ".encode())
            for _ in range(16):
                value = random.randrange(1 << 8)
                f.write(f"0x{value:02x}, ".encode())
                crc = binascii.crc32(struct.pack("B", value), crc)
            f.write(b"\n")
        f.write(b"};\n")
        f.write(b"uint8_t *data = &d[0];\n")
        f.write(b"uint32_t main() { return crc32a(data, length); }\n")

    # Kept for parity with the original (dead code on Python 3, since
    # binascii.crc32 is unsigned there already).
    if crc < 0:
        crc += 2**32

    return length, crc


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ram_size = int(sys.argv[1], 0)  # accepts 0x... or decimal
    out_path = sys.argv[2] if len(sys.argv) > 2 else "download_test.c"

    length, crc = generate(ram_size, out_path)

    print(f"wrote:    {out_path}")
    print(f"length:   {length} bytes (0x{length:x})")
    print(f"expected status (crc): {crc}  (0x{crc:08x})")

    with open("expected_crc.txt", "w", encoding="utf-8") as f:
        f.write(f"{crc}\n0x{crc:08x}\n")


if __name__ == "__main__":
    main()
