"""
PMOS-input folded cascode at VDD = 0.9 V with low-voltage (Sooch) cascode bias.

Bias generator (4 simple diode columns, NO stacked replicas):
  Col 1 : VBP     -- PMOS diode at IBIAS pin (XMP_REF + RBP)
  Col 2 : VBIAS3  -- PMOS source (XMP_VB3, g=VBP) -> NMOS diode (XMN_REF)
  Col 3 : VBIAS2  -- PMOS source (XMP_B2,  g=VBP) -> 1/4-aspect NMOS diode
                    (low-V cascode bias for NMOS-cascode gates;
                     XMN_B2 has L=2,W=4 so VGS = Vt + 2*Vov)
  Col 4 : VBIAS1  -- 1/4-aspect PMOS diode (XMP_B1, L=4,W=16) at VDD,
                    sunk by NMOS sink (XMN_B1, g=VBIAS3, 10 uA).
                    |VGS| = |Vt| + 2*|Vov|  (low-V PMOS cascode gate ref).

Signal path (re-budgeted for VDD=0.9 V, IDD ~ 80 uA at TT):
  PMOS tail        :  40 uA total
  PMOS input pair  :  20 uA each
  NMOS sinks       :  40 uA each
  NMOS cascodes    :  fold 20 uA each
  PMOS cascodes    :  20 uA each
  PMOS load diode  :  20 uA each   (L=1, wider to keep |VSG|<0.5V at SS)
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


def tlabel(d, p, text, dx=0, dy=0, size=10):
    d += elm.Label().at((p[0] + dx, p[1] + dy)).label(text, fontsize=size)


def tap_right(d, gate_pt, name, stub=0.8):
    end = (gate_pt[0] + stub, gate_pt[1])
    L(d, gate_pt, end)
    dot(d, end, open_=True)
    tlabel(d, end, name, dx=0.55, dy=0, size=9)


def tap_left(d, gate_pt, name, stub=0.8):
    end = (gate_pt[0] - stub, gate_pt[1])
    L(d, gate_pt, end)
    dot(d, end, open_=True)
    tlabel(d, end, name, dx=-0.55, dy=0, size=9)


# ============================================================
#  BIAS GENERATOR  (low-voltage cascode bias for VDD = 0.9 V)
# ============================================================
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

    # -------- Col 1 : VBP (PMOS diode at IBIAS pin) --------
    MP_REF = pfet(d, (X_C1, Y_VDD))
    dot(d, MP_REF.source)
    tlabel(d, MP_REF.source, 'MP_REF\nL=1 W=16 nf=4', dx=1.8, dy=-0.4, size=9)

    Y_DTIE1 = MP_REF.drain[1] - 0.3
    L(d, MP_REF.gate, (MP_REF.gate[0], Y_DTIE1))
    L(d, (MP_REF.gate[0], Y_DTIE1), (MP_REF.drain[0], Y_DTIE1))
    dot(d, (MP_REF.drain[0], Y_DTIE1))

    # IBIAS pin (external sink to VDD)
    Y_IBPIN = 4.0
    L(d, MP_REF.drain, (MP_REF.drain[0], Y_IBPIN))
    dot(d, (MP_REF.drain[0], Y_IBPIN), open_=True)
    tlabel(d, (MP_REF.drain[0], Y_IBPIN),
           'IBIAS pin\n10 uA sink to VDD', dx=0, dy=-0.6, size=9)

    # VBP tap on right (RBP = 1 ohm)
    Y_VBP_TAP = MP_REF.drain[1] - 0.15
    XR_TAP1 = X_C1 + 2.2
    L(d, (MP_REF.drain[0], Y_VBP_TAP), (XR_TAP1, Y_VBP_TAP))
    dot(d, (XR_TAP1, Y_VBP_TAP), open_=True)
    tlabel(d, (XR_TAP1, Y_VBP_TAP), 'VBP', dx=0.55, dy=0, size=11)

    tlabel(d, (X_C1, Y_VSS - 1.4), 'Col 1: VBP\nPMOS src ref', dx=0, dy=0, size=10)

    # -------- Col 2 : VBIAS3 (PMOS src -> NMOS diode) --------
    MP_VB3 = pfet(d, (X_C2, Y_VDD))
    dot(d, MP_VB3.source)
    tlabel(d, MP_VB3.source, 'MP_VB3\nL=1 W=16 nf=4', dx=1.6, dy=-0.4, size=9)

    MN_REF = nfet(d, (X_C2, 5.5))
    tlabel(d, MN_REF.source, 'MN_REF\nL=0.5 W=8 nf=4', dx=-2.2, dy=0.45, size=9)
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

    tlabel(d, (X_C2, Y_VSS - 1.4), 'Col 2: VBIAS3\nNMOS sink ref', dx=0, dy=0, size=10)

    # -------- Col 3 : VBIAS2 (low-V cascode, 1/4-aspect NMOS diode) --------
    MP_B2 = pfet(d, (X_C3, Y_VDD))
    dot(d, MP_B2.source)
    tlabel(d, MP_B2.source, 'MP_B2\nL=1 W=16 nf=4', dx=1.6, dy=-0.4, size=9)

    # 1/4-aspect NMOS diode -> VGS = Vt + 2*Vov
    MN_B2 = nfet(d, (X_C3, 5.5))
    tlabel(d, MN_B2.source, 'MN_B2\nL=4 W=8 nf=4\n(1/4 aspect)',
           dx=-2.2, dy=0.55, size=9)
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

    # -------- Col 4 : VBIAS1 (low-V cascode, 1/4-aspect PMOS diode) --------
    # PMOS diode (L=4, W=16) at VDD, sunk by NMOS sink at bottom.
    MP_B1 = pfet(d, (X_C4, Y_VDD))
    dot(d, MP_B1.source)
    tlabel(d, MP_B1.source, 'MP_B1\nL=4 W=16 nf=4\n(1/4 aspect)',
           dx=1.6, dy=-0.55, size=9)
    # PMOS diode tie
    Y_DTIE4 = MP_B1.drain[1] - 0.3
    L(d, MP_B1.gate, (MP_B1.gate[0], Y_DTIE4))
    L(d, (MP_B1.gate[0], Y_DTIE4), (MP_B1.drain[0], Y_DTIE4))
    dot(d, (MP_B1.drain[0], Y_DTIE4))

    MN_B1 = nfet(d, (X_C4, 5.5))
    tlabel(d, MN_B1.source, 'MN_B1\nL=0.5 W=8 nf=4', dx=-2.2, dy=0.45, size=9)
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

    d += elm.Label().at(((XL_RAIL + XR_RAIL) / 2, Y_VDD + 1.6)).label(
        'Bias Generator  (low-V Sooch cascode, IBIAS = 10 uA, VDD = 0.9 V)',
        fontsize=13)

    d.save('sketch_lowvdd_bias.png', dpi=150)


# ============================================================
#  SIGNAL PATH  (re-budgeted PMOS-input folded cascode, VDD = 0.9 V)
# ============================================================
with schemdraw.Drawing(show=False, fontsize=11) as d:
    d.config(unit=1.5)

    Y_VDD = 17.0
    Y_VSS = 0.0
    X_TAIL = 9.5
    X_INL  = 7.0
    X_INR  = 12.0
    X_L    = 2.5    # left fold leg (diode side, fL node)
    X_R    = 16.5   # right fold leg (VOUTP side)
    XL_RAIL, XR_RAIL = -1.5, 20.5

    L(d, (XL_RAIL, Y_VDD), (XR_RAIL, Y_VDD))
    L(d, (XL_RAIL, Y_VSS), (XR_RAIL, Y_VSS))
    tlabel(d, (XL_RAIL, Y_VDD), 'VDD = 0.9 V', dx=-1.2, dy=0.35, size=12)
    tlabel(d, (XL_RAIL, Y_VSS), 'VSS', dx=-0.8, dy=-0.35, size=12)

    # ---- PMOS tail (40 uA total) ----
    MTL = pfet(d, (X_TAIL, Y_VDD))
    dot(d, MTL.source)
    tlabel(d, MTL.source, 'MTL  m=4  (40 uA)', dx=1.4, dy=-0.3, size=9)
    tap_left(d, MTL.gate, 'VBP')

    # ntail node at MTL.drain (~15.5)
    Y_NTAIL = MTL.drain[1]
    dot(d, MTL.drain)
    tlabel(d, MTL.drain, 'ntail', dx=0.5, dy=0.45, size=10)

    # ---- PMOS input pair (20 uA each) ----
    Y_IN_TOP = Y_NTAIL - 0.8
    MIN1 = pfet(d, (X_INL, Y_IN_TOP), reverse=True)   # gate on right -> VINP
    MIN2 = pfet(d, (X_INR, Y_IN_TOP))                  # gate on right -> VINN
    tlabel(d, MIN1.source, 'M1 m=4', dx=-1.5, dy=-0.3, size=9)
    tlabel(d, MIN2.source, 'M2 m=4', dx=1.4, dy=-0.3, size=9)

    # ntail to both pair sources
    L(d, MTL.drain, (X_INL, Y_NTAIL))
    L(d, (X_INL, Y_NTAIL), MIN1.source)
    L(d, (X_TAIL, Y_NTAIL), (X_INR, Y_NTAIL))
    L(d, (X_INR, Y_NTAIL), MIN2.source)
    dot(d, MIN1.source); dot(d, MIN2.source)

    # Input gates
    tap_left(d, MIN1.gate, 'VINP', stub=1.0)
    tap_right(d, MIN2.gate, 'VINN', stub=1.0)

    # ---- fold nodes nbL, nbR ----
    Y_NB = MIN1.drain[1] - 0.4
    dot(d, MIN1.drain); dot(d, MIN2.drain)
    L(d, MIN1.drain, (X_INL, Y_NB))
    L(d, MIN2.drain, (X_INR, Y_NB))
    # carry across to fold legs
    L(d, (X_INL, Y_NB), (X_L, Y_NB))
    L(d, (X_INR, Y_NB), (X_R, Y_NB))
    dot(d, (X_L, Y_NB))
    dot(d, (X_R, Y_NB))
    tlabel(d, (X_L, Y_NB), 'nbL', dx=-0.55, dy=0.3, size=10)
    tlabel(d, (X_R, Y_NB), 'nbR', dx=0.55, dy=0.3, size=10)

    # ---- NMOS bottom sinks M11, M12 (40 uA each) ----
    M11 = nfet(d, (X_L, 4.5))
    M12 = nfet(d, (X_R, 4.5))
    tlabel(d, M11.source, 'M11 m=4\nW=8 nf=4', dx=-1.9, dy=0.55, size=9)
    tlabel(d, M12.source, 'M12 m=4\nW=8 nf=4', dx=1.4, dy=0.55, size=9)
    L(d, M11.source, (X_L, Y_VSS)); dot(d, (X_L, Y_VSS))
    L(d, M12.source, (X_R, Y_VSS)); dot(d, (X_R, Y_VSS))
    tap_left(d, M11.gate, 'VBIAS3')
    tap_right(d, M12.gate, 'VBIAS3')

    # M11/M12 drain to fold node
    L(d, M11.drain, (X_L, Y_NB))
    L(d, M12.drain, (X_R, Y_NB))

    # ---- NMOS cascodes M1A, M2A (20 uA each) ----
    M1A = nfet(d, (X_L, 8.5))
    M2A = nfet(d, (X_R, 8.5))
    tlabel(d, M1A.source, 'M1A', dx=-1.4, dy=0.4, size=9)
    tlabel(d, M2A.source, 'M2A', dx=1.2, dy=0.4, size=9)
    L(d, M1A.source, (X_L, Y_NB)); 
    L(d, M2A.source, (X_R, Y_NB))
    tap_left(d, M1A.gate, 'VBIAS2')
    tap_right(d, M2A.gate, 'VBIAS2')

    # fL node (M1A.drain) and VOUTP node (M2A.drain)
    Y_FL = 11.5
    dot(d, M1A.drain); dot(d, M2A.drain)
    L(d, M1A.drain, (X_L, Y_FL))
    L(d, M2A.drain, (X_R, Y_FL))
    dot(d, (X_L, Y_FL))
    dot(d, (X_R, Y_FL))
    tlabel(d, (X_L, Y_FL), 'fL', dx=-0.5, dy=0.3, size=10)
    # VOUTP tap right
    XR_OUT = X_R + 2.5
    L(d, (X_R, Y_FL), (XR_OUT, Y_FL))
    dot(d, (XR_OUT, Y_FL), open_=True)
    tlabel(d, (XR_OUT, Y_FL), 'VOUTP', dx=0.7, dy=0, size=11)

    # ---- PMOS cascodes M3A, M4A (20 uA each) ----
    M3A = pfet(d, (X_L, 13.2))
    M4A = pfet(d, (X_R, 13.2))
    tlabel(d, M3A.source, 'M3A', dx=-1.4, dy=0.0, size=9)
    tlabel(d, M4A.source, 'M4A', dx=1.2, dy=0.0, size=9)
    L(d, M3A.drain, (X_L, Y_FL))
    L(d, M4A.drain, (X_R, Y_FL))
    tap_left(d, M3A.gate, 'VBIAS1')
    tap_right(d, M4A.gate, 'VBIAS1')

    # nP3d, nP4d nodes (between PMOS load & PMOS cascode)
    dot(d, M3A.source); dot(d, M4A.source)
    Y_NP = 15.0
    L(d, M3A.source, (X_L, Y_NP)); dot(d, (X_L, Y_NP))
    L(d, M4A.source, (X_R, Y_NP)); dot(d, (X_R, Y_NP))
    tlabel(d, (X_L, Y_NP), 'nP3d', dx=-0.7, dy=0.0, size=9)
    tlabel(d, (X_R, Y_NP), 'nP4d', dx=0.7, dy=0.0, size=9)

    # ---- PMOS load mirror M3 (diode @ fL), M4 (20 uA each, L=1 W=32) ----
    M3 = pfet(d, (X_L, Y_VDD))
    M4 = pfet(d, (X_R, Y_VDD), reverse=True)   # gate on left for M4
    dot(d, M3.source); dot(d, M4.source)
    tlabel(d, M3.source, 'M3 m=6 L=1 W=32', dx=1.4, dy=-0.3, size=9)
    tlabel(d, M4.source, 'M4 m=6 L=1 W=32', dx=-1.8, dy=-0.3, size=9)
    L(d, M3.drain, (X_L, Y_NP))
    L(d, M4.drain, (X_R, Y_NP))

    # M3 diode tie: gate (right of M3) -> down -> across to fL node
    Y_GTIE = Y_FL
    L(d, M3.gate, (M3.gate[0], Y_GTIE))
    L(d, (M3.gate[0], Y_GTIE), (X_L, Y_GTIE))
    dot(d, (X_L, Y_GTIE))
    # mirror wire to M4.gate (M4 reversed -> gate on left), routed just below VDD rail
    Y_MIR = Y_VDD - 0.55
    L(d, M3.gate, (M3.gate[0], Y_MIR))
    L(d, (M3.gate[0], Y_MIR), (M4.gate[0], Y_MIR))
    L(d, (M4.gate[0], Y_MIR), M4.gate)
    dot(d, M3.gate); dot(d, M4.gate)

    d += elm.Label().at(((XL_RAIL + XR_RAIL) / 2, Y_VDD + 1.6)).label(
        'Signal Path  (PMOS folded cascode, VDD=0.9V, IDD~85uA TT, v2: enlarged matched devices)',
        fontsize=13)

    d.save('sketch_lowvdd_signal.png', dpi=150)


# ============================================================
#  COMBINED side-by-side PNG
# ============================================================
from PIL import Image
bias = Image.open('sketch_lowvdd_bias.png')
sig  = Image.open('sketch_lowvdd_signal.png')
H = max(bias.height, sig.height)
W = bias.width + sig.width + 40
combo = Image.new('RGB', (W, H), 'white')
combo.paste(bias, (0, (H - bias.height) // 2))
combo.paste(sig,  (bias.width + 40, (H - sig.height) // 2))
combo.save('sketch_lowvdd_combined.png')
print('Wrote sketch_lowvdd_bias.png, sketch_lowvdd_signal.png, sketch_lowvdd_combined.png')
