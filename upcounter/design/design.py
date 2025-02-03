from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, flipped, connect

__all__ = ["CounterSignature", "UpCounter"]

CounterSignature = wiring.Signature({
    "limit": In(8),
    "en": In(1),
    "ovf": Out(1),
    "count": Out(8)
})


class UpCounter(wiring.Component):
    design_name = "upcounter"

    def __init__(self):
        # define interfaces (for pads connections see test_socs_common/silicon.py)
        interfaces = {
            "pins": Out(CounterSignature),
        }
        super().__init__(interfaces)

    def elaborate(self, platform):
        m = Module()

        pins = self.pins

        m.d.comb += pins.ovf.eq(pins.count == pins.limit)

        with m.If(pins.en):
            with m.If(pins.ovf):
                m.d.sync += pins.count.eq(0)
            with m.Else():
                m.d.sync += pins.count.eq(pins.count + 1)

        return m


MySoC = UpCounter
