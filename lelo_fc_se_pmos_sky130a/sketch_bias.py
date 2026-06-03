"""
Bias-generator schematic for fc_se_pmos opamp (sky130A, VDD=1.2 V).

Four sub-mirrors, all referenced to the external 10 uA IBIAS sink-to-VDD:
  Col 1: VBP       -- PMOS diode at IBIAS pin (XMP_REF + RBP)
  Col 2: VBIAS3    -- PMOS source (XMP_VB3, gate=VBP) into NMOS diode (XMN_REF)
  Col 3: VBIAS2    -- Wide-swing replica: PMOS source -> NMOS diode -> NMOS sink
  Col 4: VBIAS1    -- Wide-swing replica: PMOS source -> PMOS diode -> NMOS sink

Layout rules same as sketch_fc.py:
  - Only VDD/VSS are horizontal rails.
  - Every FET uses .theta(0) to defeat schemdraw's cumulative-theta bug.
  - Every Line uses .endpoints(p0,p1).
"""
import schemdraw
import schemdraw.elements as elm


def L(d, p0, p1):
    d += elm.Line().endpoints(p0, p1)


def pfet(d, pos, reverse=False):
    e = elm.PFet(reverse=reverse).theta(0).at(pos)
    d += e
    return e


def nfet(d, pos, reverse=False):
    e = elm.NFet(reverse=reverse).theta(0).at(pos)
    d += e
    return e


def dot(d, p, open_=False):
    d += elm.Dot(open=open_).at(p)


def tlabel(d, p, text, dx=0, dy=0, size=11):
    d += elm.Label().at((p[0] + dx, p[1] + dy)).label(text, fontsize=size)


def in_tap(d, gate_pt, name, stub=0.9):
    """Incoming-bias tap on LEFT of gate (gate is on right side of body)."""
    end = (gate_pt[0] + stub, gate_pt[1])  # gate already on right of body; extend rightward
    L(d, gate_pt, end)
    dot(d, end, open_=True)
    tlabel(d, end, name, dx=0.6, dy=0, size=10)


def in_tap_left(d, gate_pt, name, stub=0.9):
    """Incoming-bias tap on LEFT side (used for reversed PFet whose gate is on left of body)."""
    end = (gate_pt[0] - stub, gate_pt[1])
    L(d, gate_pt, end)
    dot(d, end, open_=True)
    tlabel(d, end, name, dx=-0.6, dy=0, size=10)


with schemdraw.Drawing(show=False, fontsize=11) as d:
    d.config(unit=1.5)

    # ---- coordinate plan --------------------------------------------------
    Y_VDD   = 14.0
    Y_VSS   = 0.0
    X_C1    = 3.0    # VBIAS3 column
    X_C2    = 9.0    # VBP column
    X_C3    = 16.0   # VBIAS2 column
    X_C4    = 23.0   # VBIAS1 column
    XL_RAIL = -1.0
    XR_RAIL = 27.0

    # ---- power rails ------------------------------------------------------
    L(d, (XL_RAIL, Y_VDD), (XR_RAIL, Y_VDD))
    L(d, (XL_RAIL, Y_VSS), (XR_RAIL, Y_VSS))
    tlabel(d, (XL_RAIL, Y_VDD), 'VDD', dx=-0.8, dy=0.35, size=13)
    tlabel(d, (XL_RAIL, Y_VSS), 'VSS', dx=-0.8, dy=-0.35, size=13)

    # =====================================================================
    # COLUMN 1 : VBP   (PMOS diode at IBIAS pin, sourcing 10 uA from VDD)
    #   XMP_REF :  D=IBIAS  G=IBIAS  S=VDD     (diode-tied to VDD)
    #   IBIAS pin -> external 10 uA sink to VDD (open dot DOWN)
    #   RBP -> tiny series R between IBIAS and VBP (drawn as wire)
    # =====================================================================
    MP_REF = pfet(d, (X_C1, Y_VDD - 0.0))    # source on VDD rail (y=14)
    dot(d, MP_REF.source)
    tlabel(d, MP_REF.source, 'MP_REF', dx=1.7, dy=-0.3)
    # PMOS diode tie: gate (right) -> drain (below source) via bend underneath
    Y_DTIE1 = MP_REF.drain[1] - 0.3
    L(d, MP_REF.gate, (MP_REF.gate[0], Y_DTIE1))
    L(d, (MP_REF.gate[0], Y_DTIE1), (MP_REF.drain[0], Y_DTIE1))
    dot(d, MP_REF.drain)
    L(d, MP_REF.drain, (MP_REF.drain[0], Y_DTIE1))
    # IBIAS pin: drop drain down to an open dot near VSS
    Y_IBPIN = 4.0
    L(d, MP_REF.drain, (MP_REF.drain[0], Y_IBPIN))
    dot(d, (MP_REF.drain[0], Y_IBPIN), open_=True)
    tlabel(d, (MP_REF.drain[0], Y_IBPIN), 'IBIAS pin\n(10 uA sink to VDD)', dx=0, dy=-0.55, size=9)
    # VBP output tap from drain (RBP = 1 ohm ~ wire) - tap on RIGHT
    Y_VBP_TAP = MP_REF.drain[1] - 0.2
    XR_TAP1 = X_C1 + 2.2
    L(d, (MP_REF.drain[0], Y_VBP_TAP), (XR_TAP1, Y_VBP_TAP))
    dot(d, (XR_TAP1, Y_VBP_TAP), open_=True)
    tlabel(d, (XR_TAP1, Y_VBP_TAP), 'VBP', dx=0.7, dy=0, size=11)

    tlabel(d, (X_C1, Y_VSS - 1.2), 'Col 1: VBP\nPMOS source ref', dx=0, dy=0, size=10)

    # =====================================================================
    # COLUMN 2 : VBIAS3   (PMOS source mirror -> NMOS diode)
    #   XMP_VB3 :  S=VDD    G=VBP     D=VBIAS3  (PMOS source, 10 uA)
    #   XMN_REF :  D=VBIAS3 G=VBIAS3  S=VSS     (NMOS diode at bottom)
    # =====================================================================
    MP_VB3 = pfet(d, (X_C2, Y_VDD - 0.0))
    dot(d, MP_VB3.source)
    tlabel(d, MP_VB3.source, 'MP_VB3', dx=1.7, dy=-0.3)

    MN_REF = nfet(d, (X_C2, 5.5))
    tlabel(d, MN_REF.source, 'MN_REF', dx=-1.9, dy=0.4)
    L(d, MN_REF.source, (MN_REF.source[0], Y_VSS))
    dot(d, (MN_REF.source[0], Y_VSS))

    # VBIAS3 node: MP_VB3.drain (12.5) -> MN_REF.drain (5.5)
    L(d, MP_VB3.drain, MN_REF.drain)
    dot(d, MP_VB3.drain); dot(d, MN_REF.drain)
    # NMOS diode tie: gate -> drain via bend ABOVE drain
    Y_TIE2 = MN_REF.drain[1] + 0.3
    L(d, MN_REF.gate, (MN_REF.gate[0], Y_TIE2))
    L(d, (MN_REF.gate[0], Y_TIE2), (MN_REF.drain[0], Y_TIE2))
    dot(d, (MN_REF.drain[0], Y_TIE2))

    # VBP input tap on MP_VB3.gate
    in_tap(d, MP_VB3.gate, 'VBP')
    # VBIAS3 output tap on LEFT side mid-wire
    Y_VB3_TAP = 9.0
    XL_TAP2 = X_C2 - 1.5
    L(d, (X_C2, Y_VB3_TAP), (XL_TAP2, Y_VB3_TAP))
    dot(d, (X_C2, Y_VB3_TAP))
    dot(d, (XL_TAP2, Y_VB3_TAP), open_=True)
    tlabel(d, (XL_TAP2, Y_VB3_TAP), 'VBIAS3', dx=-0.7, dy=0, size=11)

    tlabel(d, (X_C2, Y_VSS - 1.2), 'Col 2: VBIAS3\nNMOS sink ref', dx=0, dy=0, size=10)

    # =====================================================================
    # COLUMN 3 : VBIAS2   wide-swing replica
    #   XMP_B2  :  S=VDD   G=VBP    D=VBIAS2
    #   XMN20R  :  D=VBIAS2 G=VBIAS2 S=VX_R   (NMOS diode, replicates M1A/M2A)
    #   XMN12R  :  D=VX_R  G=VBIAS3 S=VSS    (NMOS sink, replicates M11/M12)
    # =====================================================================
    MP_B2 = pfet(d, (X_C3, Y_VDD - 0.0))
    dot(d, MP_B2.source)
    tlabel(d, MP_B2.source, 'MP_B2', dx=1.5, dy=-0.3)

    # NMOS diode (replica of M1A) -- place mid
    MN20R = nfet(d, (X_C3, 9.0))
    tlabel(d, MN20R.source, 'MN20R', dx=-1.9, dy=0.4)
    # NMOS sink (replica of M11) -- place low
    MN12R = nfet(d, (X_C3, 4.0))
    tlabel(d, MN12R.source, 'MN12R', dx=-1.9, dy=0.4)
    L(d, MN12R.source, (MN12R.source[0], Y_VSS))
    dot(d, (MN12R.source[0], Y_VSS))

    # VBIAS2 node: MP_B2.drain (12.5) -> MN20R.drain (9.0)
    L(d, MP_B2.drain, MN20R.drain)
    dot(d, MP_B2.drain); dot(d, MN20R.drain)
    # NMOS diode tie: MN20R.gate -> MN20R.drain
    Y_TIE2 = MN20R.drain[1] + 0.3
    L(d, MN20R.gate, (MN20R.gate[0], Y_TIE2))
    L(d, (MN20R.gate[0], Y_TIE2), (MN20R.drain[0], Y_TIE2))
    dot(d, (MN20R.drain[0], Y_TIE2))

    # VX_R node: MN20R.source (7.5) -> MN12R.drain (4.0)
    L(d, MN20R.source, MN12R.drain)
    dot(d, MN20R.source); dot(d, MN12R.drain)
    tlabel(d, (X_C3, 5.7), 'VX_R', dx=-0.7, dy=0, size=9)

    # input taps
    in_tap(d, MP_B2.gate, 'VBP')
    in_tap(d, MN12R.gate, 'VBIAS3')
    # VBIAS2 output tap (right side from VBIAS2 wire)
    Y_VB2_TAP = 11.0
    XR_TAP3 = X_C3 + 2.0
    L(d, (X_C3, Y_VB2_TAP), (XR_TAP3, Y_VB2_TAP))
    dot(d, (X_C3, Y_VB2_TAP))
    dot(d, (XR_TAP3, Y_VB2_TAP), open_=True)
    tlabel(d, (XR_TAP3, Y_VB2_TAP), 'VBIAS2', dx=0.7, dy=0, size=11)

    tlabel(d, (X_C3, Y_VSS - 1.2), 'Col 3: VBIAS2\nNMOS-cascode replica', dx=0, dy=0, size=10)

    # =====================================================================
    # COLUMN 4 : VBIAS1   wide-swing replica
    #   XMP_B1A :  S=VDD   G=VBP    D=VY_R   (PMOS source replica of MTL/M3/M4)
    #   XMP_B1B :  S=VY_R  G=VBIAS1 D=VBIAS1 (PMOS diode, replica of M3A/M4A)
    #   XMN_B1  :  D=VBIAS1 G=VBIAS3 S=VSS   (NMOS sink, replica of M11/M12)
    # =====================================================================
    MP_B1A = pfet(d, (X_C4, Y_VDD - 0.0))
    dot(d, MP_B1A.source)
    tlabel(d, MP_B1A.source, 'MP_B1A', dx=1.7, dy=-0.3)

    # PMOS diode mid
    MP_B1B = pfet(d, (X_C4, MP_B1A.drain[1] - 1.5))   # source at 11.0, drain at 9.5
    tlabel(d, MP_B1B.source, 'MP_B1B', dx=1.7, dy=-0.3)

    # NMOS sink low
    MN_B1 = nfet(d, (X_C4, 5.5))
    tlabel(d, MN_B1.source, 'MN_B1', dx=-1.7, dy=0.4)
    L(d, MN_B1.source, (MN_B1.source[0], Y_VSS))
    dot(d, (MN_B1.source[0], Y_VSS))

    # VY_R node: MP_B1A.drain (12.5) -> MP_B1B.source (11.0)
    L(d, MP_B1A.drain, MP_B1B.source)
    dot(d, MP_B1A.drain); dot(d, MP_B1B.source)
    tlabel(d, (X_C4, 11.75), 'VY_R', dx=-0.7, dy=0, size=9)

    # VBIAS1 node: MP_B1B.drain (9.5) -> MN_B1.drain (5.5)
    L(d, MP_B1B.drain, MN_B1.drain)
    dot(d, MP_B1B.drain); dot(d, MN_B1.drain)
    # PMOS diode tie on MP_B1B
    Y_DTIE4 = MP_B1B.drain[1] - 0.4
    L(d, MP_B1B.gate, (MP_B1B.gate[0], Y_DTIE4))
    L(d, (MP_B1B.gate[0], Y_DTIE4), (MP_B1B.drain[0], Y_DTIE4))
    dot(d, (MP_B1B.drain[0], Y_DTIE4))

    # input taps
    in_tap(d, MP_B1A.gate, 'VBP')
    in_tap(d, MN_B1.gate, 'VBIAS3')
    # VBIAS1 output tap (right of VBIAS1 wire)
    Y_VB1_TAP = 7.5
    XR_TAP4 = X_C4 + 2.0
    L(d, (X_C4, Y_VB1_TAP), (XR_TAP4, Y_VB1_TAP))
    dot(d, (X_C4, Y_VB1_TAP))
    dot(d, (XR_TAP4, Y_VB1_TAP), open_=True)
    tlabel(d, (XR_TAP4, Y_VB1_TAP), 'VBIAS1', dx=0.7, dy=0, size=11)

    tlabel(d, (X_C4, Y_VSS - 1.2), 'Col 4: VBIAS1\nPMOS-cascode replica', dx=0, dy=0, size=10)

    # =====================================================================
    # Title
    # =====================================================================
    d += elm.Label().at(((XL_RAIL + XR_RAIL) / 2, Y_VDD + 1.5)).label(
        'Bias Generator  (10 uA master IBIAS)  -  sky130A, VDD = 1.2 V',
        fontsize=14,
    )

    d.save('/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_fc_bias.png', dpi=180)
    print('OK -> sketch_fc_bias.png')
