from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import Out
from chipflow_lib.platforms import InputPinSignature, OutputPinSignature

__all__ = ["UpCounter"]


class UpCounter(wiring.Component):
    design_name = "upcounter"

    limit: Out(InputPinSignature(8))
    en: Out(InputPinSignature(1))
    ovf: Out(OutputPinSignature(1))
    count: Out(OutputPinSignature(8))

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
