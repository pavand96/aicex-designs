"""
Folded-cascode SE OTA (PMOS input) — REPLICA-BIASED.

Per user's clarifying notes:

  BIAS                                            MAIN AMP
  ---------------------------------------  ==================================
   col A : PMOS replica            VDD       VDD       VDD       VDD
     VDD                            |         |         |         |
      |                           M_P1,L    M_TL      M_P1,R
     M_P1b (diode)  → V_P1        gate=VP1  gate=VP1  gate=VP1
      |                              |       V_tail     |
     M_P2b (diode)  → V_P2        M_P2,L   /     \    M_P2,R
      |                            gate=VP2 MINP MINN  gate=VP2
     R_p                             |     gate    gate  |
      |                              |     =Vinp =Vinn   |
     I_BIAS (10µA pin)         (int. node)              V_OUTP
                                     |                    |
   col B : NMOS replica            M_N2,L  drain=Vmidn  M_N2,R
     VDD                            gate=VN2 ↘   ↙ Vmidp gate=VN2
      |                              |    (fold nodes)    |
     R_n                            Vmidn               Vmidp
      |                              |                    |
     M_N2b (diode) → V_N2          M_N1,L              M_N1,R
      |                            gate=VN1            gate=VN1
     M_N1b (diode) → V_N1            |                    |
      |                             GND                  GND
     GND

No self-biased V_P0.  No top-PMOS mirror.  Single-ended output = V_OUTP only.
The LEFT fold leg carries static fold current; its top-mid node is internal
(unlabeled). Input pair drains Vmidn / Vmidp are fold nodes between the
NMOS cascode source and the NMOS sink drain in each leg.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch
from matplotlib.lines import Line2D

FIG_W, FIG_H = 30, 20
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(-4, 42); ax.set_ylim(-6, 21)
ax.set_aspect('equal'); ax.axis('off')

BLUE='#1f4fbf'; RED='#c0392b'; GREY='#888888'; GREEN='#0a8a4a'

# ---------- primitives ----------
def line(p1,p2,c='k',lw=1.8,ls='-'):
    ax.add_line(Line2D([p1[0],p2[0]],[p1[1],p2[1]],color=c,lw=lw,linestyle=ls))
def dot(p,r=0.10,c='k'):
    ax.add_patch(Circle(p,r,facecolor=c,edgecolor=c,zorder=5))
def text(p,s,ha='center',va='center',fs=12,color='k',weight='normal'):
    ax.text(p[0],p[1],s,ha=ha,va=va,fontsize=fs,color=color,weight=weight)
def gnd(p):
    x,y=p
    line((x,y),(x,y-0.18))
    line((x-0.42,y-0.18),(x+0.42,y-0.18),lw=2.6)
    line((x-0.28,y-0.34),(x+0.28,y-0.34),lw=2.0)
    line((x-0.14,y-0.50),(x+0.14,y-0.50),lw=1.5)
def vdd_bar(x,y,w=2.4):
    line((x-w/2,y),(x+w/2,y),lw=3.2)
    text((x-w/2-0.25,y),'$V_{DD}$',ha='right',va='center',fs=12)

# ---------- MOSFET symbols ----------
CH=0.75; GAP=0.20; GBH=0.55; GST=1.00; SD=0.55

def pmos(xc, yc, name, gate_side='left', name_side='right'):
    gs = -1 if gate_side=='left' else 1
    line((xc, yc-CH),(xc, yc+CH), lw=3.2)
    sd = -gs
    line((xc, yc+CH),(xc+sd*SD, yc+CH))
    line((xc+sd*SD, yc+CH),(xc+sd*SD, yc+CH+0.40))
    line((xc, yc-CH),(xc+sd*SD, yc-CH))
    line((xc+sd*SD, yc-CH),(xc+sd*SD, yc-CH-0.40))
    gbx = xc + gs*GAP
    line((gbx, yc-GBH),(gbx, yc+GBH), lw=2.6)
    line((gbx, yc),(xc + gs*(GAP+GST), yc))
    arr_x = xc + sd*0.05
    arr_y = yc + CH
    ax.add_patch(Polygon(
        [(arr_x, arr_y),
         (arr_x + sd*0.24, arr_y + 0.14),
         (arr_x + sd*0.24, arr_y - 0.14)],
        closed=True, facecolor='k'))
    nx = xc + (1.10 if name_side=='right' else -1.10)
    text((nx, yc), name, ha='left' if name_side=='right' else 'right', fs=12)
    return {'source':(xc+sd*SD, yc+CH+0.40),
            'drain':(xc+sd*SD, yc-CH-0.40),
            'gate':(xc+gs*(GAP+GST), yc),
            'xc':xc,'yc':yc}

def nmos(xc, yc, name, gate_side='right', name_side='left'):
    gs = -1 if gate_side=='left' else 1
    line((xc, yc-CH),(xc, yc+CH), lw=3.2)
    sd = -gs
    line((xc, yc+CH),(xc+sd*SD, yc+CH))
    line((xc+sd*SD, yc+CH),(xc+sd*SD, yc+CH+0.40))
    line((xc, yc-CH),(xc+sd*SD, yc-CH))
    line((xc+sd*SD, yc-CH),(xc+sd*SD, yc-CH-0.40))
    gbx = xc + gs*GAP
    line((gbx, yc-GBH),(gbx, yc+GBH), lw=2.6)
    line((gbx, yc),(xc + gs*(GAP+GST), yc))
    arr_x = xc + sd*0.29
    arr_y = yc - CH
    ax.add_patch(Polygon(
        [(arr_x, arr_y),
         (arr_x - sd*0.24, arr_y + 0.14),
         (arr_x - sd*0.24, arr_y - 0.14)],
        closed=True, facecolor='k'))
    nx = xc + (1.10 if name_side=='right' else -1.10)
    text((nx, yc), name, ha='left' if name_side=='right' else 'right', fs=12)
    return {'source':(xc+sd*SD, yc-CH-0.40),
            'drain':(xc+sd*SD, yc+CH+0.40),
            'gate':(xc+gs*(GAP+GST), yc),
            'xc':xc,'yc':yc}

def resistor(pt, pb, label, side='right'):
    x=pt[0]; y0=pt[1]; y1=pb[1]; n=6; h=y0-y1; ws=0.28
    pts=[(x,y0)]
    for i in range(n):
        yi=y0-h*(i+0.5)/n
        xi=x+(ws if i%2==0 else -ws)
        pts.append((xi,yi))
    pts.append((x,y1))
    for a,b in zip(pts[:-1],pts[1:]): line(a,b)
    lx=x+(0.6 if side=='right' else -0.6)
    text((lx,(y0+y1)/2), label, ha='left' if side=='right' else 'right', fs=12)

def csrc(pt, pb, label, side='right'):
    x=pt[0]; yc=(pt[1]+pb[1])/2; r=0.46
    line(pt,(x,yc+r)); line((x,yc-r),pb)
    ax.add_patch(Circle((x,yc),r,facecolor='white',edgecolor='k',lw=1.8))
    line((x,yc+r*0.55),(x,yc-r*0.55))
    ax.add_patch(Polygon([(x-0.16,yc-r*0.25),(x+0.16,yc-r*0.25),(x,yc-r*0.55)],
                         closed=True, facecolor='k'))
    lx=x+(0.7 if side=='right' else -0.7)
    text((lx,yc), label, ha='left' if side=='right' else 'right', fs=11)

def gate_tap_pmos(t, lbl=None, color=BLUE):
    tap=(t['gate'][0]-0.6, t['gate'][1])
    line(t['gate'], tap); dot(tap)
    if lbl: text((tap[0]-0.18, tap[1]), lbl, ha='right', fs=11, color=color)
    return tap

def gate_tap_nmos(t, lbl=None, color=BLUE):
    tap=(t['gate'][0]+0.6, t['gate'][1])
    line(t['gate'], tap); dot(tap)
    if lbl: text((tap[0]+0.18, tap[1]), lbl, ha='left', fs=11, color=color)
    return tap

def diode_pmos(t, lbl, color=BLUE):
    """Tie PMOS gate (LEFT) down to its own drain."""
    tap = gate_tap_pmos(t, lbl, color)
    yj = t['drain'][1] - 0.55
    line(tap, (tap[0], yj))
    line((tap[0], yj), (t['drain'][0], yj))
    line((t['drain'][0], yj), t['drain'])
    return tap

def diode_nmos(t, lbl, color=BLUE):
    """Tie NMOS gate (RIGHT) up to its own drain."""
    tap = gate_tap_nmos(t, lbl, color)
    yj = t['drain'][1] + 0.55
    line(tap, (tap[0], yj))
    line((tap[0], yj), (t['drain'][0], yj))
    line((t['drain'][0], yj), t['drain'])
    return tap

def dash(p1,p2,c=BLUE,lw=1.4): line(p1,p2,c=c,lw=lw,ls='--')

# ============================================================
# LAYOUT CONSTANTS
# ============================================================
XA   = 2.0     # PMOS bias gen
XB   = 8.5     # NMOS bias gen
XTL  = 19.0
XIP_L= 16.0
XIP_R= 22.0
XL   = 30.0   # LEFT fold leg
XR   = 37.0   # RIGHT fold leg

YVDD       = 18.0
YROW_TOP   = 16.0   # top PMOS row (M_P1b, M_TL, M_P1L, M_P1R)
YROW_PCASC = 13.0   # PMOS cascode row (M_P2b, M_P2L, M_P2R)  &  input pair
YROW_INP   = 13.0
Y_INT      = 11.0   # internal node between PMOS cascode and NMOS cascode
YROW_NCASC = 9.0    # NMOS cascode row (M_N2b, M_N2L, M_N2R)
Y_FOLD     = 7.0    # fold nodes Vmidn / Vmidp
YROW_NBOT  = 5.0    # bottom NMOS row (M_N1b, M_N1L, M_N1R)
YGND       = 2.5

# bus tracks
Y_BUS_VP1  = 17.2   # top
Y_BUS_VP2  = 1.4    # bottom margin
Y_BUS_VN2  = 0.4
Y_BUS_VN1  = -0.8

# red signal tracks
Y_RED_N    = 8.0    # Vmidn signal route
Y_RED_P    = 6.8    # Vmidp signal route (we'll redo placement)

# ============================================================
# TITLE & REGION LABELS
# ============================================================
text(((XA+XR)/2, 19.6),
     'Folded-cascode SE OTA  (PMOS input, replica-biased)',
     ha='center', fs=18, weight='bold')
text(((XA+XR)/2, 19.0),
     r'sky130A LVT,  $V_{DD}=0.9$ V,  $I_{REF}=10$ µA',
     ha='center', fs=11, color=GREY)

text(((XA+XB)/2, 20.5), 'BIAS GENERATORS', ha='center', fs=13, color=BLUE, weight='bold')
text(((XTL+XR)/2, 20.5), 'MAIN AMP', ha='center', fs=13, color='k', weight='bold')
line((13.5, -1.5), (13.5, 18.5), c=GREY, lw=1.0, ls=':')

# ============================================================
# COL A : PMOS bias replica
# ============================================================
vdd_bar(XA, YVDD)
MP1b = pmos(XA, YROW_TOP,   '$M_{P1b}$', 'left', 'right')
line(MP1b['source'], (MP1b['source'][0], YVDD)); line((MP1b['source'][0], YVDD), (XA, YVDD))
MP2b = pmos(XA, YROW_PCASC, '$M_{P2b}$', 'left', 'right')
line(MP1b['drain'], MP2b['source'])

# R_p below MP2b
yRpT = MP2b['drain'][1]
yRpB = yRpT - 2.5
line(MP2b['drain'], (MP2b['drain'][0], yRpT)); line((MP2b['drain'][0], yRpT), (XA, yRpT))
resistor((XA, yRpT), (XA, yRpB), '$R_p$', 'right')

# IBIAS pin: 10µA sink to GND (current source symbol pulling DOWN)
yIt = yRpB - 0.4; yIb = yIt - 1.8
line((XA, yRpB), (XA, yIt))
csrc((XA, yIt), (XA, yIb), r'$I_{BIAS}=10\,\mu A$', 'right')
line((XA, yIb), (XA, YGND-0.5)); gnd((XA, YGND-0.5))

# bias taps -- diode-tied
tapVP1_A = diode_pmos(MP1b, '$V_{P1}$')
tapVP2_A = diode_pmos(MP2b, '$V_{P2}$')

text((XA, -2.4), 'PMOS replica\n(col A)', ha='center', fs=11, color=BLUE)

# ============================================================
# COL B : NMOS bias replica  (per attached image)
#   VDD -> R_n -> M_N2b diode -> M_N1b diode -> GND
# ============================================================
vdd_bar(XB, YVDD)

# R_n at top, just below VDD bar
yRnT = YVDD - 0.8
yRnB = yRnT - 2.5
line((XB, YVDD), (XB, yRnT))
resistor((XB, yRnT), (XB, yRnB), '$R_n$', 'right')

MN2b = nmos(XB, YROW_NCASC, '$M_{N2b}$', 'right', 'left')
line((XB, yRnB), (XB, MN2b['drain'][1]))
line(MN2b['drain'], (XB, MN2b['drain'][1]))

MN1b = nmos(XB, YROW_NBOT, '$M_{N1b}$', 'right', 'left')
line(MN2b['source'], (XB, MN1b['drain'][1]))
line(MN1b['drain'], (XB, MN1b['drain'][1]))
line(MN1b['source'], (XB, YGND-0.5)); gnd((XB, YGND-0.5))

tapVN2_B = diode_nmos(MN2b, '$V_{N2}$')
tapVN1_B = diode_nmos(MN1b, '$V_{N1}$')

text((XB, -2.4), 'NMOS replica\n(col B)', ha='center', fs=11, color=BLUE)

# ============================================================
# MAIN AMP — Input stage
# ============================================================
vdd_bar(XTL, YVDD)
MTL = pmos(XTL, YROW_TOP, '$M_{TL}$', 'left', 'right')
line(MTL['source'], (MTL['source'][0], YVDD)); line((MTL['source'][0], YVDD), (XTL, YVDD))
tapTL = gate_tap_pmos(MTL)

yTail = MTL['drain'][1] - 0.7
line(MTL['drain'], (MTL['drain'][0], yTail)); line((MTL['drain'][0], yTail), (XTL, yTail))
dot((XTL, yTail))
text((XTL+0.25, yTail+0.30), '$V_{tail}$', ha='left', fs=10, color=GREY)

# tail rail
line((XIP_L, yTail), (XIP_R, yTail))

# MINP (left): gate LEFT, name RIGHT
MINP = pmos(XIP_L, YROW_INP, '$M_{INP}$', 'left', 'right')
line(MINP['source'], (XIP_L, yTail))
tapINP = (MINP['gate'][0]-0.8, MINP['gate'][1])
line(MINP['gate'], tapINP); dot(tapINP)
text((tapINP[0]-0.15, tapINP[1]), '$V_{inp}$', ha='right', fs=12)

# MINN (right): gate RIGHT, name LEFT (mirror image)
MINN = pmos(XIP_R, YROW_INP, '$M_{INN}$', 'right', 'left')
line(MINN['source'], (XIP_R, yTail))
tapINN = (MINN['gate'][0]+0.8, MINN['gate'][1])
line(MINN['gate'], tapINN); dot(tapINN)
text((tapINN[0]+0.15, tapINN[1]), '$V_{inn}$', ha='left', fs=12)

text((XTL, -2.4), 'Input pair\n(PMOS, $V_{CM}=0.3$ V)', ha='center', fs=11)

# Input-pair drains: short stub down to a labeled dot — these are the signal sources
ySrcN = MINP['drain'][1] - 0.7
line(MINP['drain'], (MINP['drain'][0], ySrcN)); dot((MINP['drain'][0], ySrcN))
text((MINP['drain'][0]-0.25, ySrcN-0.35), '$V_{midn}$',
     ha='right', fs=10, color=RED)

ySrcP = MINN['drain'][1] - 0.7
line(MINN['drain'], (MINN['drain'][0], ySrcP)); dot((MINN['drain'][0], ySrcP))
text((MINN['drain'][0]+0.25, ySrcP-0.35), '$V_{midp}$',
     ha='left', fs=10, color=RED)

# ============================================================
# LEFT FOLD LEG (XL) — wide-swing PMOS cascode MIRROR REFERENCE
#   MP0,L gate is tied to MP2,L DRAIN (= V_outn = V_P0 node)
# ============================================================
vdd_bar(XL, YVDD)
MP0L = pmos(XL, YROW_TOP,   '$M_{P0,L}$', 'left', 'right')
line(MP0L['source'], (MP0L['source'][0], YVDD)); line((MP0L['source'][0], YVDD), (XL, YVDD))

MP2L = pmos(XL, YROW_PCASC, '$M_{P2,L}$', 'left', 'right')
line(MP0L['drain'], MP2L['source'])
tapP2L = gate_tap_pmos(MP2L)

# V_outn (= V_P0) at MP2L drain
line(MP2L['drain'], (MP2L['drain'][0], Y_INT)); line((MP2L['drain'][0], Y_INT), (XL, Y_INT))
dot((XL, Y_INT))
text((XL-0.5, Y_INT+0.25), '$V_{outn}\,(=V_{P0})$', ha='right', fs=11, weight='bold', color=GREEN)

# Wide-swing tie: MP0L gate → left, DOWN to V_outn level, across to MP2L drain
tapP0L = gate_tap_pmos(MP0L, None, GREEN)
xbend = tapP0L[0] - 0.8
line(tapP0L, (xbend, tapP0L[1]), c=GREEN, lw=1.8)
line((xbend, tapP0L[1]), (xbend, Y_INT), c=GREEN, lw=1.8)
line((xbend, Y_INT), (XL, Y_INT), c=GREEN, lw=1.8)

MN2L = nmos(XL, YROW_NCASC, '$M_{N2,L}$', 'right', 'left')
line((XL, Y_INT), MN2L['drain'])
tapN2L = gate_tap_nmos(MN2L)

# fold node Vmidn (between MN2L source and MN1L drain)
line(MN2L['source'], (XL, Y_FOLD)); dot((XL, Y_FOLD))
text((XL-0.5, Y_FOLD+0.25), '$V_{midn}$', ha='right', fs=11, color=RED, weight='bold')
text((XL-0.5, Y_FOLD-0.30), '(fold node)', ha='right', fs=9, color=GREY)

MN1L = nmos(XL, YROW_NBOT, '$M_{N1,L}$', 'right', 'left')
line(MN1L['drain'], (XL, Y_FOLD))
tapN1L = gate_tap_nmos(MN1L)
line(MN1L['source'], (XL, YGND-0.5)); gnd((XL, YGND-0.5))

text((XL, -2.4), 'LEFT fold leg', ha='center', fs=11)

# ============================================================
# RIGHT FOLD LEG (XR) — mirror leg, MP0,R gate driven by shared V_P0
# ============================================================
vdd_bar(XR, YVDD)
MP0R = pmos(XR, YROW_TOP,   '$M_{P0,R}$', 'left', 'right')
line(MP0R['source'], (MP0R['source'][0], YVDD)); line((MP0R['source'][0], YVDD), (XR, YVDD))
tapP0R = gate_tap_pmos(MP0R, None, GREEN)

MP2R = pmos(XR, YROW_PCASC, '$M_{P2,R}$', 'left', 'right')
line(MP0R['drain'], MP2R['source'])
tapP2R = gate_tap_pmos(MP2R)

# V_OUTP — high-Z node between MP2R drain and MN2R drain
line(MP2R['drain'], (MP2R['drain'][0], Y_INT)); line((MP2R['drain'][0], Y_INT), (XR, Y_INT))
dot((XR, Y_INT), r=0.15)
text((XR+0.55, Y_INT), '$V_{OUTP}$', ha='left', fs=14, weight='bold')

MN2R = nmos(XR, YROW_NCASC, '$M_{N2,R}$', 'right', 'left')
line((XR, Y_INT), MN2R['drain'])
tapN2R = gate_tap_nmos(MN2R)

line(MN2R['source'], (XR, Y_FOLD)); dot((XR, Y_FOLD))
text((XR+0.5, Y_FOLD+0.25), '$V_{midp}$', ha='left', fs=11, color=RED, weight='bold')
text((XR+0.5, Y_FOLD-0.30), '(fold node)', ha='left', fs=9, color=GREY)

MN1R = nmos(XR, YROW_NBOT, '$M_{N1,R}$', 'right', 'left')
line(MN1R['drain'], (XR, Y_FOLD))
tapN1R = gate_tap_nmos(MN1R)
line(MN1R['source'], (XR, YGND-0.5)); gnd((XR, YGND-0.5))

text((XR, -2.4), 'RIGHT fold leg\n($V_{OUTP}$)', ha='center', fs=11)

# ============================================================
# V_P0 wire (green): shared mirror gate, from tapP0L over the top to tapP0R
# ============================================================
yVP0 = 17.0
line(tapP0L, (tapP0L[0], yVP0), c=GREEN, lw=1.8)
line((tapP0L[0], yVP0), (tapP0R[0], yVP0), c=GREEN, lw=1.8)
line((tapP0R[0], yVP0), tapP0R, c=GREEN, lw=1.8)
text(((XL+XR)/2, yVP0+0.30),
     '$V_{P0}$  shared mirror gate (LEFT leg is wide-swing diode-tied ref)',
     ha='center', fs=11, color=GREEN, weight='bold')

# ============================================================
# BIAS BUSES (dashed blue)
# ============================================================
# V_P1 bus across the TOP: tapVP1_A and tapTL ONLY
# (fold legs do NOT use V_P1 — their upper PMOS is locally diode-tied)
for tap in (tapVP1_A, tapTL):
    dash(tap, (tap[0], Y_BUS_VP1))
dash((tapVP1_A[0], Y_BUS_VP1), (tapTL[0], Y_BUS_VP1))
text(((tapVP1_A[0]+tapTL[0])/2, Y_BUS_VP1+0.3),
     '$V_{P1}$ bus  (only to $M_{TL}$)', ha='center', fs=11, color=BLUE)

# V_P2 bus along BOTTOM at Y_BUS_VP2: tapVP2_A, tapP2L, tapP2R
xLeftEdge = -3.2
dash(tapVP2_A, (xLeftEdge, tapVP2_A[1]))
dash((xLeftEdge, tapVP2_A[1]), (xLeftEdge, Y_BUS_VP2))
dash((xLeftEdge, Y_BUS_VP2), (tapP2R[0], Y_BUS_VP2))
dash((tapP2R[0], Y_BUS_VP2), tapP2R)
dash((tapP2L[0], Y_BUS_VP2), tapP2L)
text(((tapP2L[0]+tapP2R[0])/2, Y_BUS_VP2+0.3),
     '$V_{P2}$ bus', ha='center', fs=11, color=BLUE)

# V_N2 bus at Y_BUS_VN2: tapVN2_B, tapN2L, tapN2R
xRightEdge = 41.0
dash(tapVN2_B, (xRightEdge, tapVN2_B[1]))
dash((xRightEdge, tapVN2_B[1]), (xRightEdge, Y_BUS_VN2))
dash((xRightEdge, Y_BUS_VN2), (tapN2L[0], Y_BUS_VN2))
dash((tapN2L[0], Y_BUS_VN2), tapN2L)
dash((tapN2R[0], Y_BUS_VN2), tapN2R)
text(((tapN2L[0]+tapN2R[0])/2, Y_BUS_VN2+0.3),
     '$V_{N2}$ bus', ha='center', fs=11, color=BLUE)

# V_N1 bus at Y_BUS_VN1
xRightEdge2 = 41.6
dash(tapVN1_B, (xRightEdge2, tapVN1_B[1]))
dash((xRightEdge2, tapVN1_B[1]), (xRightEdge2, Y_BUS_VN1))
dash((xRightEdge2, Y_BUS_VN1), (tapN1L[0], Y_BUS_VN1))
dash((tapN1L[0], Y_BUS_VN1), tapN1L)
dash((tapN1R[0], Y_BUS_VN1), tapN1R)
text(((tapN1L[0]+tapN1R[0])/2, Y_BUS_VN1+0.3),
     '$V_{N1}$ bus', ha='center', fs=11, color=BLUE)

# ============================================================
# SIGNAL ROUTING : Vmidn (LEFT input drain → LEFT fold node)
#                  Vmidp (RIGHT input drain → RIGHT fold node)
# ============================================================
# Vmidn: from (MINP.drain.x, ySrcN) down to Y_RED_N, across LEFT to XL, up to Y_FOLD
line((MINP['drain'][0], ySrcN), (MINP['drain'][0], Y_RED_N), c=RED, lw=1.8, ls='--')
line((MINP['drain'][0], Y_RED_N), (XL, Y_RED_N),               c=RED, lw=1.8, ls='--')
line((XL, Y_RED_N), (XL, Y_FOLD),                              c=RED, lw=1.8, ls='--')
text(((MINP['drain'][0]+XL)/2, Y_RED_N+0.3),
     '$V_{midn}$  (M_INP drain $\\to$ LEFT fold node)',
     ha='center', fs=10, color=RED)

# Vmidp: down to Y_RED_P, across to XR, up to Y_FOLD
line((MINN['drain'][0], ySrcP), (MINN['drain'][0], Y_RED_P), c=RED, lw=1.8, ls='--')
line((MINN['drain'][0], Y_RED_P), (XR, Y_RED_P),               c=RED, lw=1.8, ls='--')
line((XR, Y_RED_P), (XR, Y_FOLD),                              c=RED, lw=1.8, ls='--')
text(((MINN['drain'][0]+XR)/2, Y_RED_P-0.4),
     '$V_{midp}$  (M_INN drain $\\to$ RIGHT fold node)',
     ha='center', fs=10, color=RED)

# ============================================================
# LEGEND BOX (top-left)
# ============================================================
lx0, ly0, lw_, lh_ = -3.8, 17.6, 6.0, 2.0
ax.add_patch(FancyBboxPatch((lx0, ly0), lw_, lh_,
                            boxstyle="round,pad=0.15", linewidth=0.8,
                            edgecolor='k', facecolor='#f7f7f7'))
text((lx0+0.3, ly0+lh_-0.4), 'Legend:', ha='left', fs=10, weight='bold')
line((lx0+0.3, ly0+1.10), (lx0+1.3, ly0+1.10), c=BLUE, lw=1.4, ls='--')
text((lx0+1.5, ly0+1.10), 'bias bus', ha='left', fs=9, color=BLUE)
line((lx0+0.3, ly0+0.60), (lx0+1.3, ly0+0.60), c=RED, lw=1.6, ls='--')
text((lx0+1.5, ly0+0.60), 'signal ($V_{mid}$)', ha='left', fs=9, color=RED)
line((lx0+0.3, ly0+0.15), (lx0+1.3, ly0+0.15), c='k', lw=1.8)
text((lx0+1.5, ly0+0.15), 'circuit wire', ha='left', fs=9)

# ============================================================
# FOOTER
# ============================================================
text(((XA+XR)/2, -4.5),
     'BIAS MAP:   $V_{P1}\\!\\to\\!M_{TL}$ only   '
     '$V_{P2}\\!\\to\\!M_{P2,L},M_{P2,R}$   '
     '$V_{N2}\\!\\to\\!M_{N2,L},M_{N2,R}$   '
     '$V_{N1}\\!\\to\\!M_{N1,L},M_{N1,R}$',
     ha='center', fs=11)
text(((XA+XR)/2, -5.3),
     '$V_{P0}$: LEFT leg WIDE-SWING diode-tie ($M_{P0,L}$ gate $\\to$ $M_{P2,L}$ drain).  '
     'Shared to $M_{P0,R}$ gate (PMOS cascode mirror).  Output: $V_{OUTP}$ only.',
     ha='center', fs=10, color=GREY)

# Legend update for V_P0
text((-3.7, 16.6), 'green = $V_{P0}$ mirror', ha='left', fs=9, color=GREEN)

plt.tight_layout()
out = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
plt.savefig(out, dpi=130, bbox_inches='tight', facecolor='white')
print('OK', out)
