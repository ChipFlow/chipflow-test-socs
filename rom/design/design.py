from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, flipped, connect

from math import ceil, log2
import random


__all__ = ["ROMSignature", "ROM"]

ROMSignature = wiring.Signature({
    "addr": In(12),
    "data_out": Out(16),
})


class ROM(wiring.Component):
    design_name = "ROM"

    def __init__(self):
        # define interfaces (for pads connections see test_socs_common/silicon.py)
        interfaces = {
            "mem": Out(ROMSignature),
        }
        super().__init__(interfaces)

        self.addr_width = self.mem.addr.width
        self.data_width = self.mem.data_out.width
        self.data_size = 2**self.addr_width
        self.data = random.randbytes(self.data_size)

    def elaborate(self, platform):
        m = Module()

        self._mem = Memory(width=self.data_width, depth=self.data_size, init=self.data)
        m.submodules.rom = rom = self._mem.read_port()

        m.d.comb += [
            rom.addr.eq(self.mem.addr),
            self.mem.data_out.eq(rom.data)
        ]

        return m

MySoC = ROM