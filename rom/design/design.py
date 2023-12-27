from chipflow_lib.platforms.sim import SimPlatform
from chipflow_lib.software.soft_gen import SoftwareGenerator

from amaranth import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone.bus import *

from math import ceil, log2
import random

# Simulated read-only memory module.
class ROM( Elaboratable, Interface ):
    def __init__( self, data ):
        # Record size.
        self.size = len( data )
        # Data storage.
        self.data = Memory( width = 8, depth = self.size, init = data )
        # Memory read port.
        self.r = self.data.read_port()

        # Initialize Wishbone bus interface.
        Interface.__init__( self,
                            data_width = 8,
                            addr_width = ceil( log2( self.size + 1 ) ) )
        self.memory_map = MemoryMap( data_width = self.data_width,
                                     addr_width = self.addr_width,
                                     alignment = 0 )
    def elaborate( self, platform ):
        m = Module()
        # Register the read port submodule.
        m.submodules.r = self.r

        # 'ack' signal should rest at 0.
        m.d.sync += self.ack.eq( 0 )
        # Simulated reads only take one cycle, but only acknowledge
        # them after 'cyc' and 'stb' are asserted.
        with m.If( self.cyc ):
            m.d.sync += self.ack.eq( self.stb )

        # Set 'dat_r' bus signal to the value in the
        # requested 'data' array index.
        m.d.comb += [
          self.r.addr.eq( self.adr ),
          self.dat_r.eq( self.r.data )
        ]
        # End of simulated memory module.
        return m

class MySoC(Elaboratable):
    design_name = "ROM"
    def __init__(self):
        super().__init__()
        self.data_width = 16
        self.data_size = 2*1024 + 512
        self.data = random.randbytes(self.data_size)
        self.addr_width = ceil(log2(self.data_size))

    def elaborate(self, platform):
        m = Module()

        m.submodules.clock_reset_provider = platform.providers.ClockResetProvider()
        #m.submodules.rom = rom = ROM(random.randbytes(256))
        self.mem = Memory(width = self.data_width, depth = self.data_size, init = self.data)
        m.submodules.rom = rom = self.mem.read_port()

        addr = Cat(*[platform.request(f"addr_{i}") for i in range(self.addr_width)])
        data_out = Cat(*[platform.request(f"data_{i}") for i in range(self.data_width)])

        m.d.comb += [
            # for output, pad <= sig
            # for input , sig <= pad
            rom.addr.eq(addr),
            data_out.eq(rom.data)
        ]

        return m

