"""
Bias-only m=8 fix diagram (uses working schemdraw helpers from sketch_lowvdd.py).
Reflects the actual contents of sim/dut.spi after the fix:
  - All four reference branches now use m=8 (4 parallel unit cells)
  - W and L unchanged from baseline (mirror ratios preserved)
  - MC: 250/250 PASS, A0 >= 39.7 dB, PM >= 74 deg.
"""
import schemdraw
import schemdraw.elements as elm


def L(d, p0, p1):
    d += elm.Line().endpoints(p0, p1)
def pfet(d, pos, reverse=False):
    e = elm.PFet(reverse=reverse).theta(0).at(pos); d += e; return e
def nfet(d, pos, reverse=False):
    e = elm.NFet(reverse=reverse).theta(0).at(pos); d += e; return e
def dot(d, p, open_=False):
    d += elm.Dot(open=open_).at(p)
def tlabel(d, p, text, dx=0, dy=0, size=10):
    d += elm.Label().at((p[0]+dx, p[1]+dy)).label(text, fontsize=size)
def tap_right(d, gate_pt, name, stub=0.8):
    end = (gate_pt[0]+stub, gate_pt[1])
    L(d, gate_pt, end); dot(d, end, open_=True)
    tlabel(d, end, name, dx=0.55, dy=0, size=9)
def tap_left(d, gate_pt, name, stub=0.8):
    end = (gate_pt[0]-stub, gate_pt[1])
    L(d, gate_pt, end); dot(d, end, open_=True)
    tlabel(d, end, name, dx=-0.55, dy=0, size=9)


with schemdraw.Drawing(show=False, fontsize=11) as d:
    d.config(unit=1.5)

    Y_VDD = 14.0
    Y_VSS = 0.0
    X_C1, X_C2, X_C3, X_C4 = 3.0, 9.0, 15.0, 21.0
    XL_RAIL, XR_RAIL = -1.0, 25.0

    L(d, (XL_RAIL, Y_VDD), (XR_RAIL, Y_VDD))
    L(d, (XL_RAIL, Y_VSS), (XR_RAIL, Y_VSS))
    tlabel(d, (XL_RAIL, Y_VDD), 'VDD = 0.9 V', dx=-1.2, dy=0.35, size=12)
    tlabel(d, (XL_RAIL, Y_VSS), 'VSS', dx=-0.8, dy=-0.35, size=12)

    # ---------- Col 1 : VBP (master PMOS diode at IBIAS pin) ----------
    MP_REF = pfet(d, (X_C1, Y_VDD))
    dot(d, MP_REF.source)
    tlabel(d, MP_REF.source, 'XMP_REF\nL=1 W=16 nf=4\nm=8  (NEW)',
           dx=1.6, dy=-0.55, size=9)
    Y_DTIE1 = MP_REF.drain[1] - 0.3
    L(d, MP_REF.gate, (MP_REF.gate[0], Y_DTIE1))
    L(d, (MP_REF.gate[0], Y_DTIE1), (MP_REF.drain[0], Y_DTIE1))
    dot(d, (MP_REF.drain[0], Y_DTIE1))
    Y_IBPIN = 4.0
    L(d, MP_REF.drain, (MP_REF.drain[0], Y_IBPIN))
    dot(d, (MP_REF.drain[0], Y_IBPIN), open_=True)
    tlabel(d, (MP_REF.drain[0], Y_IBPIN),
           'IBIAS pin\n10 uA sink to VDD', dx=0, dy=-0.6, size=9)
    Y_VBP_TAP = MP_REF.drain[1] - 0.15
    XR_TAP1 = X_C1 + 2.2
    L(d, (MP_REF.drain[0], Y_VBP_TAP), (XR_TAP1, Y_VBP_TAP))
    dot(d, (XR_TAP1, Y_VBP_TAP), open_=True)
    tlabel(d, (XR_TAP1, Y_VBP_TAP), 'VBP', dx=0.55, dy=0, size=11)
    tlabel(d, (X_C1, Y_VSS - 1.4), 'Col 1: VBP\nmaster PMOS ref\n40 uA total',
           dx=0, dy=0, size=10)

    # ---------- Col 2 : VBIAS3 (PMOS src -> NMOS diode) ----------
    MP_VB3 = pfet(d, (X_C2, Y_VDD))
    dot(d, MP_VB3.source)
    tlabel(d, MP_VB3.source, 'XMP_VB3\nL=1 W=16 nf=4\nm=8  (NEW)',
           dx=1.6, dy=-0.55, size=9)
    MN_REF = nfet(d, (X_C2, 5.5))
    tlabel(d, MN_REF.source, 'XMN_REF\nL=0.5 W=4 nf=2\nm=8  (NEW)',
           dx=-2.2, dy=0.55, size=9)
    L(d, MN_REF.source, (MN_REF.source[0], Y_VSS))
    dot(d, (MN_REF.source[0], Y_VSS))
    L(d, MP_VB3.drain, MN_REF.drain)
    dot(d, MP_VB3.drain); dot(d, MN_REF.drain)
    Y_TIE2 = MN_REF.drain[1] + 0.3
    L(d, MN_REF.gate, (MN_REF.gate[0], Y_TIE2))
    L(d, (MN_REF.gate[0], Y_TIE2), (MN_REF.drain[0], Y_TIE2))
    dot(d, (MN_REF.drain[0], Y_TIE2))
    tap_right(d, MP_VB3.gate, 'VBP')
    Y_VB3_TAP = 9.0
    XL_TAP2 = X_C2 - 1.6
    L(d, (X_C2, Y_VB3_TAP), (XL_TAP2, Y_VB3_TAP))
    dot(d, (X_C2, Y_VB3_TAP))
    dot(d, (XL_TAP2, Y_VB3_TAP), open_=True)
    tlabel(d, (XL_TAP2, Y_VB3_TAP), 'VBIAS3', dx=-0.65, dy=0, size=11)
    tlabel(d, (X_C2, Y_VSS - 1.4), 'Col 2: VBIAS3\nNMOS sink ref',
           dx=0, dy=0, size=10)

    # ---------- Col 3 : VBIAS2 (low-V NMOS cascode bias) ----------
    MP_B2 = pfet(d, (X_C3, Y_VDD))
    dot(d, MP_B2.source)
    tlabel(d, MP_B2.source, 'XMP_B2\nL=1 W=16 nf=4\nm=8  (NEW)',
           dx=1.6, dy=-0.55, size=9)
    MN_B2 = nfet(d, (X_C3, 5.5))
    tlabel(d, MN_B2.source, 'XMN_B2\nL=2 W=4 nf=2\nm=8  (NEW)\n(1/4 aspect)',
           dx=-2.2, dy=0.7, size=9)
    L(d, MN_B2.source, (MN_B2.source[0], Y_VSS))
    dot(d, (MN_B2.source[0], Y_VSS))
    L(d, MP_B2.drain, MN_B2.drain)
    dot(d, MP_B2.drain); dot(d, MN_B2.drain)
    Y_TIE3 = MN_B2.drain[1] + 0.3
    L(d, MN_B2.gate, (MN_B2.gate[0], Y_TIE3))
    L(d, (MN_B2.gate[0], Y_TIE3), (MN_B2.drain[0], Y_TIE3))
    dot(d, (MN_B2.drain[0], Y_TIE3))
    tap_right(d, MP_B2.gate, 'VBP')
    Y_VB2_TAP = 9.5
    XR_TAP3 = X_C3 + 2.0
    L(d, (X_C3, Y_VB2_TAP), (XR_TAP3, Y_VB2_TAP))
    dot(d, (X_C3, Y_VB2_TAP))
    dot(d, (XR_TAP3, Y_VB2_TAP), open_=True)
    tlabel(d, (XR_TAP3, Y_VB2_TAP), 'VBIAS2', dx=0.65, dy=0, size=11)
    tlabel(d, (X_C3, Y_VSS - 1.4),
           'Col 3: VBIAS2\nlow-V NMOS\ncascode ref', dx=0, dy=0, size=10)

    # ---------- Col 4 : VBIAS1 (low-V PMOS cascode bias) ----------
    MP_B1 = pfet(d, (X_C4, Y_VDD))
    dot(d, MP_B1.source)
    tlabel(d, MP_B1.source, 'XMP_B1\nL=4 W=16 nf=4\nm=8  (NEW)\n(1/4 aspect)',
           dx=1.6, dy=-0.7, size=9)
    Y_DTIE4 = MP_B1.drain[1] - 0.3
    L(d, MP_B1.gate, (MP_B1.gate[0], Y_DTIE4))
    L(d, (MP_B1.gate[0], Y_DTIE4), (MP_B1.drain[0], Y_DTIE4))
    dot(d, (MP_B1.drain[0], Y_DTIE4))
    MN_B1 = nfet(d, (X_C4, 5.5))
    tlabel(d, MN_B1.source, 'XMN_B1\nL=0.5 W=4 nf=2\nm=8  (NEW)',
           dx=-2.2, dy=0.55, size=9)
    L(d, MN_B1.source, (MN_B1.source[0], Y_VSS))
    dot(d, (MN_B1.source[0], Y_VSS))
    L(d, MP_B1.drain, MN_B1.drain)
    dot(d, MP_B1.drain); dot(d, MN_B1.drain)
    tap_left(d, MN_B1.gate, 'VBIAS3')
    Y_VB1_TAP = 9.0
    XR_TAP4 = X_C4 + 2.0
    L(d, (X_C4, Y_VB1_TAP), (XR_TAP4, Y_VB1_TAP))
    dot(d, (X_C4, Y_VB1_TAP))
    dot(d, (XR_TAP4, Y_VB1_TAP), open_=True)
    tlabel(d, (XR_TAP4, Y_VB1_TAP), 'VBIAS1', dx=0.65, dy=0, size=11)
    tlabel(d, (X_C4, Y_VSS - 1.4),
           'Col 4: VBIAS1\nlow-V PMOS\ncascode ref', dx=0, dy=0, size=10)

    # ---------- title / caption ----------
    d += elm.Label().at(((XL_RAIL + XR_RAIL) / 2, Y_VDD + 1.8)).label(
        'Bias-only m=8 fix  (signal path UNTOUCHED)  --  VDD = 0.9 V',
        fontsize=13)
    d += elm.Label().at(((XL_RAIL + XR_RAIL) / 2, Y_VSS - 3.2)).label(
        'Every reference device gets m=8 (4 parallel unit cells, same W/L).  '
        'sigma(deltaVt) ~ 1/sqrt(m*W*L)  -->  2x tighter Vt under MC.\n'
        'DC OP unchanged per corner.  Monte Carlo: 250/250 PASS,  '
        'A0_min = 39.7 dB,  PM_min = 74 deg,  IDD ~ 44 uA.',
        fontsize=10)

    d.save('/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_bias_m8_fix.png', dpi=150)
    d.save('/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_bias_m8_fix.svg')

print('wrote sketch_bias_m8_fix.{png,svg}')
