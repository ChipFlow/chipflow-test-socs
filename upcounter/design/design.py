from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, flipped, connect
from chipflow_lib.platforms import InputPinSignature, OutputPinSignature

__all__ = ["CounterSignature", "UpCounter"]

CounterSignature = wiring.Signature({
    "limit": Out(InputPinSignature(8)),
    "en": Out(InputPinSignature(1)),
    "ovf": Out(OutputPinSignature(1)),
    "count": Out(OutputPinSignature(8))
})


class UpCounter(wiring.Component):
    design_name = "upcounter"

    def __init__(self):
        # define interfaces (for pads connections see design/steps/silicon.py and test_socs_common/silicon.py)
        interfaces = {
            "pins": Out(CounterSignature),
        }
        super().__init__(interfaces)

    def elaborate(self, platform):
        m = Module()

        pins = self.pins

        m.d.comb += pins.ovf.o.eq(pins.count.o == pins.limit.i)

        with m.If(pins.en.i):
            with m.If(pins.ovf.o):
                m.d.sync += pins.count.o.eq(0)
            with m.Else():
                m.d.sync += pins.count.o.eq(pins.count.o + 1)

        return m


MySoC = UpCounter
