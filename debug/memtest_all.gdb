set pagination off
set confirm off
set remotetimeout unlimited

set $ram_base = 0x80000000
set $length   = 0x400

target extended-remote:3333
monitor reset halt

define spot
  set $off = $arg0
  set $val = *((unsigned int *)($ram_base + $off))
  printf "  offset 0x%03x (addr 0x%lx) = 0x%08x\n", $off, $ram_base + $off, $val
end

define run_memtest
  printf "\n################ MemTestBlock%d (extra_delay=%d) ################\n", $arg0, $arg0

  shell python3 memtest_gen.py $arg0 1024

  printf "\n===== Zeroing %d bytes at 0x%lx =====\n", $length, $ram_base
  eval "restore /tmp/memtest%d.zero.bin binary 0x%lx", $arg0, $ram_base
  printf "Zero done.\n"

  printf "\n===== Restoring Intel Hex (reset_delays=%d) =====\n", $arg1
  monitor riscv reset_delays $arg1
  eval "restore /tmp/memtest%d.ihex 0x%lx", $arg0, $ram_base
  printf "Restore finished.\n"

  printf "\n===== Spot checks (informational -- see full verify below for pass/fail) =====\n"
  spot 0x000
  spot 0x04c
  spot 0x098
  spot 0x0e4
  spot 0x130
  spot 0x17c
  spot 0x1c8
  spot 0x214
  spot 0x260
  spot 0x2ac
  spot 0x2f8
  spot 0x344
  spot 0x390
  spot 0x3dc
  spot 0x3fc

  printf "\n===== Dumping S-record (reset_delays=%d) =====\n", $arg2
  monitor riscv reset_delays $arg2
  eval "dump srec memory /tmp/memtest%d.srec 0x%lx 0x%lx", $arg0, $ram_base, $ram_base + $length
  printf "Dump finished.\n"

  printf "\n===== Verifying full SREC content against what was written =====\n"
  shell python3 memtest_verify.py $arg0 0x80000000 1024

  printf "\n################ MemTestBlock%d done ################\n", $arg0
end

run_memtest 0 50 100
run_memtest 1 51 101
run_memtest 2 52 102

printf "\n========== All three MemTestBlock variants complete ==========\n"
printf "Check RESULT: PASS/FAIL lines above for each block.\n"