from amaranth import *
from amaranth.lib.cdc import FFSynchronizer

__all__ = ["ChipflowTop", "silicon_config", "silicon_connect_pins"]


def silicon_config(process, pad_ring, pinout):
    cfg = {
        "process": process,
        "pad_ring": pad_ring,
    }

    pads = cfg["pads"] = {}
    pwr_pads = cfg["power"] = {}
    _locs = set()

    def _set_power_pad(name, loc):
        assert(isinstance(loc, (int, str))), f"Wrong power pad '{name}' location '{loc}'"
        assert(loc not in _locs), f"Pad '{name}' location '{loc}' already used"
        assert(name not in pads), f"Power pad '{name}' duplicates IO pad"
        assert(name not in pwr_pads), f"Duplicate power pad '{name}'"
        pwr_pads[name] = {"loc": str(loc)}
        _locs.add(loc)

    def _set_pad(name, loc, _type):
        assert(isinstance(loc, (int, str))), f"Wrong IO pad '{name}' location '{loc}'"
        assert(name not in pads), f"Duplicate IO pad '{name}'"
        assert(name not in pwr_pads), f"IO pad '{name}' duplicates power pad"
        assert _type in {"o", "i", "io", "clk"}, f"Pad '{name}' type '{_type}' is wrong"
        pads[name] = {"loc": str(loc), "type": _type}
        _locs.add(loc)

    for name, loc in pinout.items():
        _ns = name.split('=', 2) # split to name and source (interface pin)
        name = _ns[0].strip()
        _nt = name.rsplit('.', 2) # split to pad name and pad type (i, o, io)
        if len(_ns) == 1: # no source
            assert(len(_nt) == 1), f"Pad '{name}' has type but no source pin specified"
            # power pins
            if isinstance(loc, (int, str)):
                _set_power_pad(name, loc)
            else:
                for i, _loc in enumerate(loc):
                    _set_power_pad(f"{name}{i}", _loc)
            continue
        else:
            _src = _ns[1].strip()
            if _src.startswith('@'):
                assert(len(_nt) == 1), f"Pad '{name}' specified with type for special signal"
                # special signal
                if _src == "@clock":
                    _nt.append("clk")
                elif _src == "@reset":
                    _nt.append("i")
                else:
                    assert(False), f"Pad '{name}' connects to unknown special signal '{_src[1:]}'"
        # IO pins
        _name, _type = map(str.strip, _nt)
        assert _type in {"o", "i", "io", "clk"}, f"Pad '{_name}' type '{_type}' is wrong"
        if isinstance(loc, (int, str)):
            _set_pad(_name, loc, _type)
        else:
            for i, _loc in enumerate(loc):
                _set_pad(f"{_name}_{i}", _loc, _type)

    return cfg


def silicon_connect_pins(platform, m, soc, pinout):
    for info in pinout.items():
        _ns = info[0].split('=', 2)
        if len(_ns) == 1:
            continue
        _nt = list(map(str.strip, _ns[0].rsplit('.', 2)))
        _src = _ns[1].strip()
        if _src.startswith('@'):
            if _src == "@clock":
                clk = platform.request(_ns[0])
                m.d.comb += ClockSignal().eq(clk.i)
            elif _src == "@reset":
                m.submodules.rst_sync = FFSynchronizer(~platform.request(_ns[0]).i, ResetSignal())
            continue

        def _get_src_pin(src):
            if not src or src.lower() == "none":
                return None
            elif src.lower() == "true":
                return True
            elif src.lower() == "false":
                return False
            obj = soc
            for name in map(str.strip, src.split('.')):
                assert(hasattr(obj, name)), f"Pin '{src}' not found (fail at '{name}')"
                obj = getattr(obj, name)
            assert(isinstance(obj, Signal)), f"Invalid pin '{src}' specified (not Signal)"
            return obj

        def _connect_pad(pad, _type, pins):
            if _type == 'i':
                assert(len(pins) == 1), f"Multiple pins specified for input pad '{pad.i.name}'"
                pins = [pins[0], None, None]
            elif _type == 'o':
                assert(len(pins) == 1), f"Multiple pins specified for output pad '{pad.o.name}'"
                pins = [None, pins[0], None]
            elif _type == 'oe':
                assert(len(pins) < 3), f"Input pin specified for output pad '{pad.o.name}'"
                pins = [None, pins[0], True if len(pins) == 1 else pins[1]]
            elif _type == 'io':
                assert(len(pins) >= 2), f"Output pin not specified for pad '{pad.o.name}'"
                assert(pins[2] is not None), f"Output enable pin not specified for pad '{pad.oe.name}'"
            if pins[0] is not None:
                m.d.comb += pins[0].eq(pad.i)
            if pins[1] is not None:
                m.d.comb += pad.o.eq(pins[1])
            if pins[2] is not None:
                m.d.comb += pad.oe.eq(pins[2])

        _pins = list(map(str.strip, _src.split(',')))
        assert(len(_nt) == 2)
        _name, _type = _nt
        if isinstance(info[1], (int, str)):
            pad = platform.request(_name)
            _connect_pad(pad, _type, list(map(_get_src_pin, _pins)))
        else:
            for i in range(len(info[1])):
                pad = platform.request(f"{_name}_{i}")
                i_src = [None if np is None else _get_src_pin(np)[i] for np in _pins]
                _connect_pad(pad, _type, i_src)


class ChipflowTop(Elaboratable):
    def __init__(self, soc_class, pinout):
        super().__init__()
        self._pinout = pinout
        self._soc_class = soc_class

    def elaborate(self, platform):
        m = Module()

        # Clock generation
        m.domains.sync = ClockDomain()

        m.submodules.soc = soc = self._soc_class()

        silicon_connect_pins(platform, m, soc, self._pinout)

        return m
