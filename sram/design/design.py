from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, flipped, connect

from math import ceil, log2
import random


__all__ = ["SRAMSignature", "SRAM"]

SRAMSignature = wiring.Signature({
    "addr": In(12),
    "data_out": Out(16),
    "data_oe": Out(16),
    "data_in": In(16),
    "wr_en": In(1)
})


class SRAM(wiring.Component):
    design_name = "SRAM"

    def __init__(self):
        # define interfaces (for pads connections see test_socs_common/silicon.py)
        interfaces = {
            "mem": Out(SRAMSignature),
        }
        super().__init__(interfaces)

        self.addr_width = self.mem.addr.width
        self.data_width = self.mem.data_out.width
        self.data_size = 2**self.addr_width

    def elaborate(self, platform):
        m = Module()

        self._mem = Memory(width=self.data_width, depth=self.data_size)
        m.submodules.sram_r = sram_r = self._mem.read_port()
        m.submodules.sram_w = sram_w = self._mem.write_port()

        m.d.comb += sram_r.addr.eq(self.mem.addr)
        m.d.comb += sram_w.addr.eq(self.mem.addr)

        with m.If(self.mem.wr_en):
            m.d.sync += sram_w.data.eq(self.mem.data_in)
        with m.Else():
            m.d.sync += self.mem.data_out.eq(sram_r.data)

        for i in range(self.data_width):
            m.d.comb += self.mem.data_oe[i].eq(self.mem.wr_en)

        return m


MySoC = SRAM
