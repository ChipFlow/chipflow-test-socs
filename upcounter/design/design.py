from chipflow_lib.platforms.sim import SimPlatform
from chipflow_lib.software.soft_gen import SoftwareGenerator

from amaranth import *

class UpCounter(Elaboratable):
    def __init__(self):
        self.limit = Signal(8)
        self.en  = Signal()
        self.ovf = Signal()
        self.count = Signal(8)

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.ovf.eq(self.count == self.limit)
        with m.If(self.en):
            with m.If(self.ovf):
                m.d.sync += self.count.eq(0)
            with m.Else():
                m.d.sync += self.count.eq(self.count + 1)
        return m

class MySoC(Elaboratable):
    design_name = "upcounter"
    def __init__(self):
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.submodules.clock_reset_provider = platform.providers.ClockResetProvider()
        m.submodules.counter = counter = UpCounter()

        m.d.comb += [
            # for output, pad <= sig
            # for input , sig <= pad
            counter.en.eq(platform.request("en")),
            platform.request("ovf").eq(counter.ovf),
            counter.limit.eq(Cat(*[platform.request(f"limit_{i}") for i in range(8)])),
            Cat(*[platform.request(f"count_{i}") for i in range(8)]).eq(counter.count),
        ]

        return m

