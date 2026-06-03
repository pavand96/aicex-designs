"""
Folded-cascode SE OTA + wide-swing R-offset bias.
Hand-drawn 4-column schematic using pure matplotlib for full control.
Matches user's hand-drawn diagram.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon, Circle
from matplotlib.lines import Line2D

# ============================ canvas ============================
FIG_W, FIG_H = 22, 17
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(-3, 27)
ax.set_ylim(-4, 17)
ax.set_aspect('equal')
ax.axis('off')

BLUE = '#1f4fbf'
RED  = '#c0392b'
WIRE = 'black'

# ============================ primitives ============================
LW = 1.8

def line(p1, p2, color=WIRE, lw=LW, ls='-'):
    ax.add_line(Line2D([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, linestyle=ls))

def dot(p, r=0.08, color=WIRE):
    ax.add_patch(Circle(p, r, facecolor=color, edgecolor=color, zorder=5))

def text(p, s, ha='center', va='center', fs=12, color='black'):
    ax.text(p[0], p[1], s, ha=ha, va=va, fontsize=fs, color=color)

def gnd(p):
    """Ground triangle at p (pointing down from p)."""
    x, y = p
    line((x, y), (x, y-0.15))
    line((x-0.35, y-0.15), (x+0.35, y-0.15), lw=2.5)
    line((x-0.22, y-0.30), (x+0.22, y-0.30), lw=2.0)
    line((x-0.10, y-0.45), (x+0.10, y-0.45), lw=1.5)

def vdd_bar(x, y, w=2.0):
    line((x-w/2, y), (x+w/2, y), lw=3)
    text((x-w/2-0.25, y), '$V_{DD}$', ha='right', va='center', fs=12)

# ---------- transistor symbols ----------
# Each transistor is a square "channel" with three pins:
#   source, drain, gate (gate on chosen side).
# PMOS: small open circle on gate; arrow points OUT of source (away from channel).
# NMOS: arrow points INTO source (toward channel).

FET_H = 1.4    # vertical extent of channel
FET_W = 1.0    # gate stub length from device centre to gate pin
CH_W  = 0.55   # half-width of channel rectangle

def pmos(xc, yc, name, gate_side='left', name_side='right'):
    """
    PMOS oriented vertically: source on TOP, drain on BOTTOM.
    xc, yc = centre of channel.
    Returns dict with anchors: source, drain, gate.
    """
    # channel bar (vertical thick line)
    line((xc, yc-FET_H/2), (xc, yc+FET_H/2), lw=3.5)
    # gate vertical bar (parallel to channel, offset toward gate_side)
    gx_sign = -1 if gate_side == 'left' else 1
    gate_bar_x = xc + gx_sign * 0.30
    line((gate_bar_x, yc-FET_H/2*0.7), (gate_bar_x, yc+FET_H/2*0.7), lw=2.0)
    # gate stub (horizontal) with small open circle marker for PMOS
    gate_pin_x = xc + gx_sign * FET_W
    line((gate_bar_x, yc), (gate_pin_x - gx_sign*0.10, yc))
    ax.add_patch(Circle((gate_pin_x - gx_sign*0.05, yc), 0.07,
                        facecolor='white', edgecolor='black', lw=1.5, zorder=4))
    # source pin (top)
    src = (xc, yc + FET_H/2 + 0.0)
    # drain pin (bottom)
    drn = (xc, yc - FET_H/2 - 0.0)
    # arrow on source: PMOS arrow points OUT of channel (toward gate side at source)
    # standard sky130 symbol: PMOS arrow OUT of source (upward + slight to the side optional)
    # We'll put a small triangle on the source pin pointing UP-and-OUTWARD
    arr_x = xc
    arr_y = yc + FET_H/2 * 0.6
    side = gx_sign * 0.18
    poly = Polygon([(arr_x, arr_y), (arr_x + side, arr_y + 0.18),
                    (arr_x + side*0.4, arr_y + 0.02)],
                   closed=True, facecolor='black')
    ax.add_patch(poly)
    # Name label
    nlbl_x = xc + (0.55 if name_side == 'right' else -0.55)
    ha = 'left' if name_side == 'right' else 'right'
    text((nlbl_x, yc), name, ha=ha, va='center', fs=12)
    return {'source': src, 'drain': drn,
            'gate': (gate_pin_x, yc), 'center': (xc, yc)}

def nmos(xc, yc, name, gate_side='right', name_side='left'):
    """NMOS vertical: drain on TOP, source on BOTTOM."""
    line((xc, yc-FET_H/2), (xc, yc+FET_H/2), lw=3.5)
    gx_sign = -1 if gate_side == 'left' else 1
    gate_bar_x = xc + gx_sign * 0.30
    line((gate_bar_x, yc-FET_H/2*0.7), (gate_bar_x, yc+FET_H/2*0.7), lw=2.0)
    gate_pin_x = xc + gx_sign * FET_W
    line((gate_bar_x, yc), (gate_pin_x, yc))
    # source pin (bottom)
    src = (xc, yc - FET_H/2)
    drn = (xc, yc + FET_H/2)
    # NMOS arrow INTO source — pointing inward (upward) at source pin
    arr_x = xc
    arr_y = yc - FET_H/2 * 0.6
    side = gx_sign * 0.18
    # arrow head pointing toward channel centre (upward) starting outward
    poly = Polygon([(arr_x + side, arr_y), (arr_x, arr_y + 0.18),
                    (arr_x + side*0.4, arr_y + 0.02)],
                   closed=True, facecolor='black')
    ax.add_patch(poly)
    nlbl_x = xc + (0.55 if name_side == 'right' else -0.55)
    ha = 'left' if name_side == 'right' else 'right'
    text((nlbl_x, yc), name, ha=ha, va='center', fs=12)
    return {'source': src, 'drain': drn,
            'gate': (gate_pin_x, yc), 'center': (xc, yc)}

def resistor(p_top, p_bot, label, label_side='right'):
    """Vertical resistor zigzag between two points."""
    x = p_top[0]
    y0, y1 = p_top[1], p_bot[1]
    n = 6
    h = (y0 - y1)
    ws = 0.25
    # zigzag
    pts = [(x, y0)]
    for i in range(n):
        yi = y0 - h * (i + 0.5) / n
        xi = x + (ws if i % 2 == 0 else -ws)
        pts.append((xi, yi))
    pts.append((x, y1))
    for a, b in zip(pts[:-1], pts[1:]):
        line(a, b)
    lbl_x = x + (0.6 if label_side == 'right' else -0.6)
    ha = 'left' if label_side == 'right' else 'right'
    text((lbl_x, (y0 + y1) / 2), label, ha=ha, va='center', fs=12)

def current_src(p_top, p_bot, label, label_side='right'):
    """Current source: circle with arrow inside, between two points."""
    x = p_top[0]
    yc = (p_top[1] + p_bot[1]) / 2
    r = 0.45
    line(p_top, (x, yc + r))
    line((x, yc - r), p_bot)
    ax.add_patch(Circle((x, yc), r, facecolor='white', edgecolor='black', lw=1.8))
    # arrow inside pointing DOWN (sink)
    line((x, yc + r*0.55), (x, yc - r*0.55))
    poly = Polygon([(x - 0.15, yc - r*0.25), (x + 0.15, yc - r*0.25), (x, yc - r*0.55)],
                   closed=True, facecolor='black')
    ax.add_patch(poly)
    lbl_x = x + (0.7 if label_side == 'right' else -0.7)
    ha = 'left' if label_side == 'right' else 'right'
    text((lbl_x, yc), label, ha=ha, va='center', fs=12)

# ============================ layout coords ============================
XA, XB, XC, XD = 1.5, 8.0, 15.0, 22.0
YVDD = 13.5

# ============================ Title ============================
text(((XA+XD)/2, 16.0),
     'Folded-cascode SE OTA   |   wide-swing R-offset bias',
     ha='center', fs=18)
text(((XA+XD)/2, 15.3),
     r'sky130A LVT,  $V_{DD}=0.9$ V,  $I_{REF}=10$ µA',
     ha='center', fs=12)

# ============================ COL A : PMOS bias gen ============================
vdd_bar(XA, YVDD)
# MP1
MP1 = pmos(XA, 12.0, '$M_{P1}$', gate_side='left', name_side='right')
line(MP1['source'], (XA, YVDD))
# MP2 (just below MP1)
MP2 = pmos(XA, 10.0, '$M_{P2}$', gate_side='left', name_side='right')
line(MP1['drain'], MP2['source'])
# Rp
yRt = MP2['drain'][1]
yRb = yRt - 1.8
resistor((XA, yRt), (XA, yRb), '$R_p$', label_side='right')
# 10 uA sink
yIt = yRb - 0.4
yIb = yIt - 1.4
line((XA, yRb), (XA, yIt))
current_src((XA, yIt), (XA, yIb), r'$10\,\mu A$', label_side='right')
line((XA, yIb), (XA, -0.3))
gnd((XA, -0.3))

# diode-tie M_P1: gate tap LEFT -> labeled VP1 -> down to drain on far left
tapP1 = (XA - 1.8, MP1['gate'][1])
line(MP1['gate'], tapP1)
dot(tapP1)
text((tapP1[0] - 0.2, tapP1[1]), '$V_{P1}$', ha='right', fs=12, color=BLUE)
# tie: go down on the outside-left to drain level then in to drain
yj1 = MP1['drain'][1] - 0.0
line(tapP1, (tapP1[0], yj1 - 0.4))
line((tapP1[0], yj1 - 0.4), (XA - 0.5, yj1 - 0.4))
line((XA - 0.5, yj1 - 0.4), (XA - 0.5, MP1['drain'][1]))
line((XA - 0.5, MP1['drain'][1]), MP1['drain'])

# diode-tie M_P2
tapP2 = (XA - 1.8, MP2['gate'][1])
line(MP2['gate'], tapP2)
dot(tapP2)
text((tapP2[0] - 0.2, tapP2[1]), '$V_{P2}$', ha='right', fs=12, color=BLUE)
yj2 = MP2['drain'][1]
line(tapP2, (tapP2[0], yj2 - 0.4))
line((tapP2[0], yj2 - 0.4), (XA - 0.5, yj2 - 0.4))
line((XA - 0.5, yj2 - 0.4), (XA - 0.5, MP2['drain'][1]))
line((XA - 0.5, MP2['drain'][1]), MP2['drain'])

text((XA, -1.2), 'PMOS bias gen', ha='center', fs=12, color=BLUE)

# ============================ COL B : NMOS bias gen ============================
vdd_bar(XB, YVDD)
MPN = pmos(XB, 12.0, '$M_{PN}$', gate_side='left', name_side='right')
line(MPN['source'], (XB, YVDD))
# Rn between MPN.drain and MN2.drain
yRnT = MPN['drain'][1] - 0.4
line(MPN['drain'], (XB, yRnT))
yRnB = yRnT - 1.8
resistor((XB, yRnT), (XB, yRnB), '$R_n$', label_side='right')
# MN2 (drain at yRnB)
MN2 = nmos(XB, yRnB - FET_H/2, '$M_{N2}$', gate_side='right', name_side='left')
line(MN2['drain'], (XB, yRnB))
# MN1 below MN2
MN1 = nmos(XB, MN2['source'][1] - FET_H/2, '$M_{N1}$', gate_side='right', name_side='left')
line(MN1['drain'], MN2['source'])
line(MN1['source'], (XB, -0.3))
gnd((XB, -0.3))

# MPN gate tap LEFT (no diode tie — driven by VP1 bus)
tapPN = (XB - 1.8, MPN['gate'][1])
line(MPN['gate'], tapPN)
dot(tapPN)

# diode-tie MN2 (right side)
tapN2 = (XB + 1.8, MN2['gate'][1])
line(MN2['gate'], tapN2)
dot(tapN2)
text((tapN2[0] + 0.2, tapN2[1]), '$V_{N2}$', ha='left', fs=12, color=BLUE)
yjn2 = MN2['drain'][1] + 0.4
line(tapN2, (tapN2[0], yjn2))
line((tapN2[0], yjn2), (XB + 0.5, yjn2))
line((XB + 0.5, yjn2), (XB + 0.5, MN2['drain'][1]))
line((XB + 0.5, MN2['drain'][1]), MN2['drain'])

# diode-tie MN1
tapN1 = (XB + 1.8, MN1['gate'][1])
line(MN1['gate'], tapN1)
dot(tapN1)
text((tapN1[0] + 0.2, tapN1[1]), '$V_{N1}$', ha='left', fs=12, color=BLUE)
yjn1 = MN1['drain'][1] + 0.4
line(tapN1, (tapN1[0], yjn1))
line((tapN1[0], yjn1), (XB + 0.5, yjn1))
line((XB + 0.5, yjn1), (XB + 0.5, MN1['drain'][1]))
line((XB + 0.5, MN1['drain'][1]), MN1['drain'])

text((XB, -1.2), 'NMOS bias gen', ha='center', fs=12, color=BLUE)

# ============================ COL C : Tail + input pair ============================
vdd_bar(XC, YVDD)
MTL = pmos(XC, 12.0, '$M_{TL}$', gate_side='left', name_side='right')
line(MTL['source'], (XC, YVDD))
tapTL = (XC - 1.8, MTL['gate'][1])
line(MTL['gate'], tapTL)
dot(tapTL)

yTail = MTL['drain'][1] - 0.5
line(MTL['drain'], (XC, yTail))
dot((XC, yTail))
text((XC + 0.3, yTail + 0.25), '$V_{tail}$', ha='left', fs=11)

# input pair MIP and MIN
xL_in = XC - 2.4
xR_in = XC + 2.4
line((xL_in, yTail), (xR_in, yTail))

# place MIP and MIN with source at yTail
# Want source up (we're using PMOS pmos() which places source at top of channel)
# so set channel centre = yTail - FET_H/2
MIP = pmos(xL_in, yTail - FET_H/2, '$M_{INP}$', gate_side='left', name_side='right')
line(MIP['source'], (xL_in, yTail))
tapINP = (MIP['gate'][0] - 0.9, MIP['gate'][1])
line(MIP['gate'], tapINP)
dot(tapINP)
text((tapINP[0] - 0.2, tapINP[1]), '$V_{inp}$', ha='right', fs=12)

MIN = pmos(xR_in, yTail - FET_H/2, '$M_{INN}$', gate_side='right', name_side='left')
line(MIN['source'], (xR_in, yTail))
tapINN = (MIN['gate'][0] + 0.9, MIN['gate'][1])
line(MIN['gate'], tapINN)
dot(tapINN)
text((tapINN[0] + 0.2, tapINN[1]), '$V_{inn}$', ha='left', fs=12)

# Drains drop down to Vmidn/Vmidp nodes
yMid = MIP['drain'][1] - 1.0
line(MIP['drain'], (xL_in, yMid))
dot((xL_in, yMid))
text((xL_in - 0.2, yMid - 0.4), '$V_{midn}$', ha='center', fs=11, color=RED)
line(MIN['drain'], (xR_in, yMid))
dot((xR_in, yMid))
text((xR_in + 0.2, yMid - 0.4), '$V_{midp}$', ha='center', fs=11)

text((XC, -1.2), 'Tail + PMOS input pair', ha='center', fs=12, color=BLUE)

# ============================ COL D : SE output cascode ============================
vdd_bar(XD, YVDD)
MP0  = pmos(XD, 12.0, '$M_{P0}$',  gate_side='left', name_side='right')
line(MP0['source'], (XD, YVDD))
tapP0 = (XD - 1.8, MP0['gate'][1])
line(MP0['gate'], tapP0); dot(tapP0)

MP2o = pmos(XD, 10.0, '$M_{P2,o}$', gate_side='left', name_side='right')
line(MP0['drain'], MP2o['source'])
tapP2o = (XD - 1.8, MP2o['gate'][1])
line(MP2o['gate'], tapP2o); dot(tapP2o)

# V_OUTP node
yOut = MP2o['drain'][1] - 0.9
line(MP2o['drain'], (XD, yOut))
dot((XD, yOut), r=0.13)
text((XD + 0.45, yOut + 0.1), '$V_{OUTP}$', ha='left', fs=13)

MN2o = nmos(XD, yOut - FET_H/2 - 0.0, '$M_{N2,o}$', gate_side='right', name_side='left')
line(MN2o['drain'], (XD, yOut))
tapN2o = (XD + 1.8, MN2o['gate'][1])
line(MN2o['gate'], tapN2o); dot(tapN2o)

MN1o = nmos(XD, MN2o['source'][1] - FET_H/2, '$M_{N1,o}$', gate_side='right', name_side='left')
line(MN1o['drain'], MN2o['source'])
tapN1o = (XD + 1.8, MN1o['gate'][1])
line(MN1o['gate'], tapN1o); dot(tapN1o)

line(MN1o['source'], (XD, -0.3))
gnd((XD, -0.3))

text((XD, -1.2), 'SE output cascode', ha='center', fs=12, color=BLUE)

# ============================ BIAS BUSES ============================
# V_P1 bus across top (taps at tapP1, tapPN, tapTL, tapP0)
yVP1 = 13.0   # below VDD bars
# vertical taps from each gate tap up to bus
for tap in (tapP1, tapPN, tapTL, tapP0):
    line(tap, (tap[0], yVP1), color=BLUE, ls='--', lw=1.4)
# horizontal bus
line((tapP1[0], yVP1), (tapP0[0], yVP1), color=BLUE, ls='--', lw=1.4)
text(((tapP1[0]+tapPN[0])/2, yVP1 + 0.25), '$V_{P1}$ bus', ha='center', fs=11, color=BLUE)

# V_P2 bus: tapP2 (col A) -> tapP2o (col D), routed in lower-LEFT margin at y=1.8
yVP2bus = 1.8
xLeftEdge = -2.4
line(tapP2, (xLeftEdge, tapP2[1]), color=BLUE, ls='--', lw=1.4)
line((xLeftEdge, tapP2[1]), (xLeftEdge, yVP2bus), color=BLUE, ls='--', lw=1.4)
line((xLeftEdge, yVP2bus), (tapP2o[0], yVP2bus), color=BLUE, ls='--', lw=1.4)
line((tapP2o[0], yVP2bus), tapP2o, color=BLUE, ls='--', lw=1.4)
text((XA + 3.5, yVP2bus + 0.30), '$V_{P2}$ bus', ha='center', fs=11, color=BLUE)

# V_N2 bus: tapN2 (col B right) -> tapN2o (col D right), routed in lower-RIGHT margin at y=3.2
yVN2bus = 3.2
xRightEdge2 = XD + 3.0
line(tapN2, (xRightEdge2, tapN2[1]), color=BLUE, ls='--', lw=1.4)
line((xRightEdge2, tapN2[1]), (xRightEdge2, yVN2bus), color=BLUE, ls='--', lw=1.4)
line((xRightEdge2, yVN2bus), (tapN2o[0], yVN2bus), color=BLUE, ls='--', lw=1.4)
line((tapN2o[0], yVN2bus), tapN2o, color=BLUE, ls='--', lw=1.4)
text((XC + 1.5, yVN2bus + 0.30), '$V_{N2}$ bus', ha='center', fs=11, color=BLUE)

# V_midn signal (red) from (xL_in, yMid) col C to tapN1o col D (route at y=5.0)
yVm = 5.0
xRedge = XD + 4.5
line((xL_in, yMid), (xL_in, yVm), color=RED, ls='--', lw=1.6)
line((xL_in, yVm), (xRedge, yVm), color=RED, ls='--', lw=1.6)
line((xRedge, yVm), (xRedge, tapN1o[1]), color=RED, ls='--', lw=1.6)
line((xRedge, tapN1o[1]), tapN1o, color=RED, ls='--', lw=1.6)
text((XC + 2.0, yVm + 0.30), '$V_{midn}$  (signal)', ha='center', fs=11, color=RED)

# ============================ Footer ============================
text(((XA+XD)/2, -2.4),
     'Buses (blue dashed):  $V_{P1}$ sets top PMOS;  $V_{P2}$ cascodes top PMOS;  '
     '$V_{N2}$ cascodes bottom NMOS;  $V_{N1}$ sets bottom NMOS.',
     ha='center', fs=10)
text(((XA+XD)/2, -3.0),
     r'R-offset trick:  $R_p$ drops $V_{ov}$ so cascode $V_{DS}=V_{ov}$  '
     r'(maximises output swing at $V_{DD}=0.9$ V).',
     ha='center', fs=10)

# ============================ save ============================
plt.tight_layout()
out = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
print('OK', out)
