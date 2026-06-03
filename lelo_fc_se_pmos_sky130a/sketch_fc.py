"""
PMOS-input folded/telescopic cascode opamp — signal-path schematic.
sky130A, VDD=1.2 V.

Layout rules:
  - Only VDD/VSS are horizontal rails.  All bias signals are shown as
    per-gate "tap" labels (open dot + name) so no rail crosses a device.
  - Every elm.Line() uses explicit .at(start).to(end).  No chained Lines.
  - Device labels are placed at >= 1.2 units away from the body.
"""
import schemdraw
import schemdraw.elements as elm


def L(d, p0, p1):
    # Use endpoints() to bypass any inherited theta from drawing state.
    line = elm.Line().endpoints(p0, p1)
    d += line
    return line


def pfet(d, pos, reverse=False):
    # Force PFet vertical (source on top, drain on bottom).
    # theta(0) overrides any inherited rotation from prior drawing state.
    e = elm.PFet(reverse=reverse).theta(0).at(pos)
    d += e
    return e


def nfet(d, pos, reverse=False):
    # Force NFet vertical (drain on top, source on bottom).
    e = elm.NFet(reverse=reverse).theta(0).at(pos)
    d += e
    return e


def dot(d, p, open_=False):
    d += elm.Dot(open=open_).at(p)


def tlabel(d, p, text, dx=0, dy=0, size=11):
    d += elm.Label().at((p[0] + dx, p[1] + dy)).label(text, fontsize=size)


def gate_tap(d, gate_pt, name, side='right', stub=0.7):
    """Draw a short stub off a FET gate ending in an open-dot tap labelled with the rail name."""
    sign = 1 if side == 'right' else -1
    end = (gate_pt[0] + sign * stub, gate_pt[1])
    L(d, gate_pt, end)
    dot(d, end, open_=True)
    tlabel(d, end, name, dx=sign * 0.5, dy=0, size=10)


with schemdraw.Drawing(show=False, fontsize=11) as d:
    d.config(unit=1.5)

    # ---- coordinate plan --------------------------------------------------
    Y_VDD = 16.5
    Y_VSS = 0.0
    X_OUTL = 4.0
    X_INL  = 12.0
    X_TAIL = 16.0
    X_INR  = 20.0
    X_OUTR = 28.0
    XL_RAIL = -1.5
    XR_RAIL = 33.0

    # ---- power rails ------------------------------------------------------
    L(d, (XL_RAIL, Y_VDD), (XR_RAIL, Y_VDD))
    L(d, (XL_RAIL, Y_VSS), (XR_RAIL, Y_VSS))
    tlabel(d, (XL_RAIL, Y_VDD), 'VDD', dx=-0.8, dy=0.35, size=13)
    tlabel(d, (XL_RAIL, Y_VSS), 'VSS', dx=-0.8, dy=-0.35, size=13)

    # ===================================================================
    # LEFT OUTPUT COLUMN: M3 (mirror) / M3A (PMOS cascode) / M1A (NMOS cascode) / M11 (sink)
    # ===================================================================
    M3  = pfet(d, (X_OUTL, Y_VDD - 0.5))
    L(d, M3.source, (M3.source[0], Y_VDD))
    dot(d, (M3.source[0], Y_VDD))
    tlabel(d, M3.source, 'M3', dx=-1.4, dy=-0.4)

    M3A = pfet(d, (X_OUTL, M3.drain[1]))
    tlabel(d, M3A.source, 'M3A', dx=-1.6, dy=-0.4)
    dot(d, M3.drain)
    tlabel(d, M3.drain, 'nP3d', dx=-1.6, dy=0.0)
    Y_FL = M3A.drain[1]            # y = 13.5

    M11 = nfet(d, (X_OUTL, Y_VSS + 1.5))
    L(d, M11.source, (M11.source[0], Y_VSS))
    tlabel(d, M11.source, 'M11', dx=-1.6, dy=0.4)

    M1A = nfet(d, (X_OUTL, 8.0))
    tlabel(d, M1A.source, 'M1A', dx=-1.6, dy=0.4)

    # nbL bus: M11.drain (1.5) -> M1A.source (6.5)
    L(d, M11.drain, M1A.source)
    dot(d, M11.drain); dot(d, M1A.source)
    tlabel(d, (X_OUTL, 4.0), 'nbL', dx=-1.0, dy=0)

    # fL bus: M1A.drain (8.0) -> M3A.drain (13.0)
    L(d, M1A.drain, M3A.drain)
    dot(d, M1A.drain); dot(d, M3A.drain)
    tlabel(d, (X_OUTL, (8.0 + Y_FL) / 2), 'fL', dx=-0.9, dy=0)

    # gate taps
    gate_tap(d, M3A.gate, 'VBIAS1', side='right')
    gate_tap(d, M1A.gate, 'VBIAS2', side='right')
    gate_tap(d, M11.gate, 'VBIAS3', side='right')

    # ===================================================================
    # RIGHT OUTPUT COLUMN: M4 / M4A / M2A / M12
    # ===================================================================
    M4  = pfet(d, (X_OUTR, Y_VDD - 0.5))
    L(d, M4.source, (M4.source[0], Y_VDD))
    dot(d, (M4.source[0], Y_VDD))
    tlabel(d, M4.source, 'M4', dx=1.4, dy=-0.4)

    M4A = pfet(d, (X_OUTR, M4.drain[1]))
    tlabel(d, M4A.source, 'M4A', dx=1.6, dy=-0.4)
    dot(d, M4.drain)
    tlabel(d, M4.drain, 'nP4d', dx=1.6, dy=0.0)

    M12 = nfet(d, (X_OUTR, Y_VSS + 1.5))
    L(d, M12.source, (M12.source[0], Y_VSS))
    tlabel(d, M12.source, 'M12', dx=1.6, dy=0.4)

    M2A = nfet(d, (X_OUTR, 8.0))
    tlabel(d, M2A.source, 'M2A', dx=1.6, dy=0.4)

    L(d, M12.drain, M2A.source)
    dot(d, M12.drain); dot(d, M2A.source)
    tlabel(d, (X_OUTR, 4.0), 'nbR', dx=1.0, dy=0)

    L(d, M2A.drain, M4A.drain)
    dot(d, M2A.drain); dot(d, M4A.drain)
    tlabel(d, (X_OUTR, (8.0 + M4A.drain[1]) / 2), 'VOUTP', dx=1.2, dy=0)

    # VOUTP output pin
    L(d, M4A.drain, (M4A.drain[0] + 2.5, M4A.drain[1]))
    dot(d, (M4A.drain[0] + 2.5, M4A.drain[1]), open_=True)
    tlabel(d, (M4A.drain[0] + 2.5, M4A.drain[1]), 'VOUTP', dx=0.7, dy=0, size=12)

    # gate taps on the LEFT side so they don't clash with the output pin
    gate_tap(d, M4A.gate, 'VBIAS1', side='right')
    gate_tap(d, M2A.gate, 'VBIAS2', side='right')
    gate_tap(d, M12.gate, 'VBIAS3', side='right')

    # ===================================================================
    # TAIL PFET + INPUT PAIR
    # ===================================================================
    MTL = pfet(d, (X_TAIL, Y_VDD - 0.5))
    L(d, MTL.source, (MTL.source[0], Y_VDD))
    dot(d, (MTL.source[0], Y_VDD))
    tlabel(d, MTL.source, 'MTL', dx=1.4, dy=-0.4)
    gate_tap(d, MTL.gate, 'VBP', side='right')

    Y_NTAIL = MTL.drain[1]  # = 15.0

    # input pair
    M1 = pfet(d, (X_INL, Y_NTAIL), reverse=True)
    M2 = pfet(d, (X_INR, Y_NTAIL))
    tlabel(d, M1.source, 'M1', dx=-1.2, dy=-0.4)
    tlabel(d, M2.source, 'M2', dx=1.2, dy=-0.4)

    # ntail bus
    L(d, M1.source, M2.source)
    dot(d, M1.source); dot(d, MTL.drain); dot(d, M2.source)
    tlabel(d, (MTL.drain[0], Y_NTAIL), 'ntail', dx=0, dy=0.45)

    # VINP / VINN
    L(d, M1.gate, (M1.gate[0] - 2.5, M1.gate[1]))
    dot(d, (M1.gate[0] - 2.5, M1.gate[1]), open_=True)
    tlabel(d, (M1.gate[0] - 2.5, M1.gate[1]), 'VINP', dx=-0.8, dy=0, size=12)

    L(d, M2.gate, (M2.gate[0] + 2.5, M2.gate[1]))
    dot(d, (M2.gate[0] + 2.5, M2.gate[1]), open_=True)
    tlabel(d, (M2.gate[0] + 2.5, M2.gate[1]), 'VINN', dx=0.8, dy=0, size=12)

    # ===================================================================
    # FOLD WIRES: M1.drain -> nbL ; M2.drain -> nbR
    # Drop vertically at input-pair x, then horizontal at nbL/nbR Y
    # (which is M1A.source[1] = 6.5).  Avoids crossing M1A/M2A drains (fL/VOUTP).
    # ===================================================================
    Y_FOLD = M1A.source[1]   # 6.5
    p = M1.drain
    L(d, p, (p[0], Y_FOLD))
    L(d, (p[0], Y_FOLD), (X_OUTL, Y_FOLD))
    dot(d, (X_OUTL, Y_FOLD))

    p = M2.drain
    L(d, p, (p[0], Y_FOLD))
    L(d, (p[0], Y_FOLD), (X_OUTR, Y_FOLD))
    dot(d, (X_OUTR, Y_FOLD))

    # ===================================================================
    # PMOS mirror diode tie: M3.gate = M4.gate = fL
    # M3.gate and M4.gate are on the right side of M3/M4 at y = 15.75.
    # Run a horizontal bus across the top, then drop down on the LEFT
    # side of M3 to reach the fL node at (X_OUTL, Y_FL).
    # ===================================================================
    Y_MIRR = M3.gate[1]  # 15.75
    L(d, M3.gate, (M4.gate[0], Y_MIRR))    # horizontal bus
    dot(d, M3.gate); dot(d, M4.gate)
    # tap from bus down to fL on the LEFT of M3 to avoid crossing devices
    X_DROP = X_OUTL - 1.0
    L(d, M3.gate, (X_DROP, Y_MIRR))
    L(d, (X_DROP, Y_MIRR), (X_DROP, Y_FL))
    L(d, (X_DROP, Y_FL), (X_OUTL, Y_FL))
    dot(d, (X_DROP, Y_FL))

    # ===================================================================
    # TITLE — placed well above VDD
    # ===================================================================
    d += elm.Label().at(((XL_RAIL + XR_RAIL) / 2, Y_VDD + 1.2)).label(
        'PMOS-input Folded/Telescopic Cascode Opamp  (sky130A, VDD = 1.2 V)',
        fontsize=14,
    )

    d.save('/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_fc_signal.png', dpi=180)

print('OK -> sketch_fc_signal.png')
