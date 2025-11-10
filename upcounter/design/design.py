from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import Out
from chipflow_lib.platforms import InputIOSignature, OutputIOSignature

__all__ = ["UpCounter"]


class UpCounter(wiring.Component):
    design_name = "upcounter"

    limit: Out(InputIOSignature(8))
    en: Out(InputIOSignature(1))
    ovf: Out(OutputIOSignature(1))
    count: Out(OutputIOSignature(8))

    def elaborate(self, platform):
        m = Module()

        limit = self.limit
        en = self.en
        ovf = self.ovf
        count = self.count

        m.d.comb += ovf.o.eq(count.o == limit.i)

        with m.If(en.i):
            with m.If(ovf.o):
                m.d.sync += count.o.eq(0)
            with m.Else():
                m.d.sync += count.o.eq(count.o + 1)

        return m


MySoC = UpCounter
