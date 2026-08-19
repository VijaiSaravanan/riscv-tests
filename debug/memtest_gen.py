#!/usr/bin/env python3
"""Generate LENGTH random bytes as both raw binary (ground truth for
verification) and Intel HEX (for gdb's `restore` command), plus a
zero-filled binary of the same length for fast RAM clearing.

Usage: memtest_gen.py <blocknum> <length>
Writes /tmp/memtest<blocknum>.bin, /tmp/memtest<blocknum>.ihex,
and /tmp/memtest<blocknum>.zero.bin
"""
import random
import sys

blocknum = sys.argv[1]
length = int(sys.argv[2])
line_length = 16

random.seed()
data = bytes(random.randrange(256) for _ in range(length))

with open(f"/tmp/memtest{blocknum}.bin", "wb") as f:
    f.write(data)

lines = []
for i in range(0, length, line_length):
    chunk = data[i:i + line_length]
    rec = [len(chunk), (i >> 8) & 0xff, i & 0xff, 0] + list(chunk)
    checksum = (-sum(rec)) & 0xff
    lines.append(":" + "".join(f"{b:02X}" for b in rec) + f"{checksum:02X}")
lines.append(":00000001FF")  # EOF record

with open(f"/tmp/memtest{blocknum}.ihex", "w") as f:
    f.write("\n".join(lines) + "\n")

with open(f"/tmp/memtest{blocknum}.zero.bin", "wb") as f:
    f.write(bytes(length))

print(f"Generated {length} bytes -> /tmp/memtest{blocknum}.bin / .ihex / .zero.bin")
