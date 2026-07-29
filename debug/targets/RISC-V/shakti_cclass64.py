import targets
import testlib
import time
class cclass64_hart(targets.Hart):
    xlen = 64
    ram = 0x80000000
    ram_size = 0x4000000
    bad_address = ram - 8
    instruction_hardware_breakpoint_count = 0
    reset_vectors = [0x1000]
    link_script_path = "shakti_cclass64.lds"
    misa = 0x800000000014112D

class cclass64(targets.Target):
    harts = [cclass64_hart()]
    openocd_config_path = "shakti_cclass_ocd.cfg"
    timeout_sec = 30
    implements_custom_test = False
    freertos_binary = "bin/RTOSDemo64.axf"
    support_memory_sampling = False

    def create(self):
        time.sleep(60)
        return testlib.Cclass(self, isa="RV64IMAFDC", progbufsize=0,
                abstract_rti=30000000000000, support_abstract_csr=False)
