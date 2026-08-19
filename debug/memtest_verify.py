#!/usr/bin/env python3
"""Verify a dumped SREC file matches what was actually written, and
covers every byte -- the same checks MemTestBlock.test_block() makes
(the original grok-generated script never did this; it only printed
the SREC for a human to eyeball).

Usage: memtest_verify.py <blocknum> <ram_base_hex> <length>
Reads /tmp/memtest<blocknum>.bin (ground truth) and
/tmp/memtest<blocknum>.srec (what the target reported), prints any
mismatch, and ends with RESULT: PASS or RESULT: FAIL.
"""
import sys


def srec_parse(line):
    line = line.strip()
    rtype = int(line[1])
    count = int(line[2:4], 16)
    if rtype in (1, 2, 3):
        addr_len = {1: 2, 2: 3, 3: 4}[rtype]
        addr = int(line[4:4 + addr_len * 2], 16)
        data_hex = line[4 + addr_len * 2: 4 + count * 2 - 2]
        return rtype, addr, bytes.fromhex(data_hex)
    return rtype, None, None


blocknum = sys.argv[1]
ram_base = int(sys.argv[2], 16)
length = int(sys.argv[3])

with open(f"/tmp/memtest{blocknum}.bin", "rb") as f:
    data = f.read()

highest_seen = 0
ok = True

with open(f"/tmp/memtest{blocknum}.srec") as f:
    for line in f:
        if not line.startswith("S"):
            continue
        rtype, addr, ldata = srec_parse(line)
        if rtype in (1, 2, 3):
            offset = addr - ram_base
            written = data[offset:offset + len(ldata)]
            highest_seen += len(ldata)
            if ldata != written:
                print(f"MISMATCH at 0x{ram_base + offset:x} "
                      f"(offset 0x{offset:x}): "
                      f"wrote {written.hex()} but read {ldata.hex()}")
                ok = False

if highest_seen != length:
    print(f"COVERAGE FAIL: highest_seen={highest_seen} != length={length} "
          f"-- some bytes were never reported back")
    ok = False

print("RESULT: PASS" if ok else "RESULT: FAIL")
