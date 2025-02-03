import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from test_socs_common.silicon import *
from chipflow_lib.steps.silicon import SiliconStep
from ..design import MySoC


_pga144_pinout = {
    "sys_clk=@clock": 144,
    "sys_rst_n=@reset": 143,
    "en.i=pins.en": 142,
    "ovf.o=pins.ovf": 141,
    "count.o=pins.count": [46, 47, 48, 50, 51, 52, 53, 54],
    "limit.i=pins.limit": [37, 38, 39, 40, 42, 43, 44, 45],
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
        return self.platform.build(ChipflowTop(MySoC, _pga144_pinout), name=MySoC.design_name)
