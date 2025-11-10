from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, flipped, connect
from chipflow_lib.platforms import InputIOSignature, OutputIOSignature


__all__ = ["SRAMSignature", "SRAM"]

SRAMSignature = wiring.Signature({
    "addr": Out(InputIOSignature(12)),
    "data_out": Out(OutputIOSignature(8)),
    "data_in": Out(InputIOSignature(8)),
    "wr_en": Out(InputIOSignature(1))
})


class SRAM(wiring.Component):
    design_name = "SRAM"

    def __init__(self):
        # define interfaces (for pads connections see design/steps/silicon.py and test_socs_common/silicon.py)
        interfaces = {
            "mem": Out(SRAMSignature),
        }
        super().__init__(interfaces)

        self.addr_width = self.mem.addr.i.width - 1
        self.data_width = self.mem.data_out.o.width
        self.data_size = 2**self.addr_width

    def elaborate(self, platform):
        m = Module()

        self._mem = Memory(width=self.data_width, depth=self.data_size)
        m.submodules.sram_w = sram_w = self._mem.write_port()
        m.submodules.sram_r = sram_r = self._mem.read_port()

        m.d.comb += sram_r.addr.eq(self.mem.addr.i)
        m.d.comb += sram_w.addr.eq(self.mem.addr.i)
        m.d.comb += sram_w.en.eq(self.mem.wr_en.i)
        m.d.comb += sram_r.en.eq(~self.mem.wr_en.i)

        with m.If(self.mem.wr_en.i):
            m.d.sync += sram_w.data.eq(self.mem.data_in.i)
        with m.Else():
            m.d.sync += self.mem.data_out.o.eq(sram_r.data)

        return m


MySoC = SRAM
