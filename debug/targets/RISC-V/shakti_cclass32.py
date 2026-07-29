import targets
import testlib
import time
class cclass32_hart(targets.Hart):
    xlen = 32
    ram = 0x80000000
    ram_size = 0x20000
    bad_address = ram - 8
    instruction_hardware_breakpoint_count = 0
    reset_vectors = [0x80000000]
    link_script_path = "shakti_cclass32.lds"
    misa = 0x40001125

class cclass32(targets.Target):
    harts = [cclass32_hart()]
    openocd_config_path = "shakti_cclass_ocd.cfg"
    timeout_sec = 30
    implements_custom_test = False
    freertos_binary = "bin/RTOSDemo32.axf"
    support_memory_sampling = False

    def create(self):
        time.sleep(60)
        return testlib.Cclass(self, isa="RV32IMAFC", progbufsize=0,
                abstract_rti=30000000000000, support_abstract_csr=False)
