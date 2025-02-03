import os
import json
from test_socs_common.silicon import *
from chipflow_lib.steps.silicon import SiliconStep
from ..design import MySoC


BUILD_DIR = os.path.join(os.environ["CHIPFLOW_ROOT"], "build")

_pga144_pinout = {
    "sys_clk=@clock": 144,
    "sys_rst_n=@reset": 143,
    "addr.i=mem.addr": [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14],
    "data.io=mem.data_in,mem.data_out,mem.data_oe": [66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 80, 82, 83],
    "wr_en.i=mem.wr_en": 15,
    "dvss": [1, 33, 65, 97, 129],
    "dvdd": [9, 41, 73, 105, 137],
    "vss": [17, 49, 81, 113],
    "vdd": [25, 57, 89, 121],
    # "input_exmple_pad.i=interface.in_pin": pad_loc,
    # "output_exmple_pad.o=interface.out_pin": pad_loc,
    # "output_with_oe_exmple_pad.oe=interface.out_pin, interface.oe_pin": pad_loc,
    # "bidir_exmple_pad.io=interface.in_pin, interface.out_pin, interface.oe_pin": pad_loc,
    # "open_drain_exmple_pad.oe=False, interface.oe_pin": pad_loc,
    # "open_source_exmple_pad.oe=True, interface.oe_pin": pad_loc,
}


class MySiliconStep(SiliconStep):
    def __init__(self, config):
        config["chipflow"]["silicon"] = silicon_config("ihp_sg13g2", "pga144", _pga144_pinout)
        super().__init__(config)

    def prepare(self):
        os.makedirs(BUILD_DIR, exist_ok=True)
        with open(os.path.join(BUILD_DIR, "config.json"), "wt") as f:
            json.dump({"silicon": self.silicon_config}, f, indent=2)
        return self.platform.build(ChipflowTop(MySoC, _pga144_pinout), name=MySoC.design_name)
