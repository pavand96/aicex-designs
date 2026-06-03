"""
Folded-cascode SE OTA (PMOS input) with wide-swing R-offset bias.

Topology (TOP-PMOS-MIRROR variant, per user's hand drawing):

  BIAS                                       MAIN AMP
  ---------------------------------  ====================================
                                              tail                    
   col A    col B                      ┌── M_TL ──┐                   
   PMOS     NMOS                       │  V_tail  │                   
   bias     bias                       │          │                  
   chain    chain                  M_INP        M_INN                  
                                  Vinp│         │Vinn                  
                                      └── V_midn,V_midp (input drains)
                                                ↓ ↓                    
                                          (route across)               
                                                ↓ ↓                    
                                       LEFT leg   RIGHT leg            
                                       M_P0,L (D)  M_P0,R   ← top mirror
                                       M_P2,L      M_P2,R   ← PMOS casc
                                       V_outn      V_OUTP  ← outputs   
                                       M_N2,L      M_N2,R   ← NMOS casc
                                       V_midn   V_midp     ← FOLD nodes 
                                       M_N1,L      M_N1,R   ← N tail   
                                        GND        GND                 

Bias generates V_P1 (top PMOS), V_P2 (PMOS cascode), V_N2 (NMOS cascode),
V_N1 (NMOS bottom).  V_P0 is SELF-biased: M_P0,L diode-tied, drives M_P0,R.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch
from matplotlib.lines import Line2D

# ---------- canvas ----------
FIG_W, FIG_H = 30, 20
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(-4, 42); ax.set_ylim(-6, 21)
ax.set_aspect('equal'); ax.axis('off')

BLUE='#1f4fbf'; RED='#c0392b'; GREEN='#0a8a4a'; GREY='#888888'

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

# ---------- MOSFET symbol ----------
CH=0.75; GAP=0.20; GBH=0.55; GST=1.00; SD=0.55

def pmos(xc, yc, name, gate_side='left', name_side='right'):
    gs = -1 if gate_side=='left' else 1
    line((xc, yc-CH),(xc, yc+CH), lw=3.2)               # channel
    sd = -gs                                            # S/D pin direction
    # source pin (top, L-bent)
    line((xc, yc+CH),(xc+sd*SD, yc+CH))
    line((xc+sd*SD, yc+CH),(xc+sd*SD, yc+CH+0.40))
    # drain pin (bottom, L-bent)
    line((xc, yc-CH),(xc+sd*SD, yc-CH))
    line((xc+sd*SD, yc-CH),(xc+sd*SD, yc-CH-0.40))
    # gate bar (parallel to channel, offset toward gate side)
    gbx = xc + gs*GAP
    line((gbx, yc-GBH),(gbx, yc+GBH), lw=2.6)
    # gate stub out to pin
    line((gbx, yc),(xc + gs*(GAP+GST), yc))
    # PMOS arrow: at source pin, pointing AWAY from channel (outward)
    arr_x = xc + sd*0.05
    arr_y = yc + CH
    ax.add_patch(Polygon(
        [(arr_x, arr_y),
         (arr_x + sd*0.24, arr_y + 0.14),
         (arr_x + sd*0.24, arr_y - 0.14)],
        closed=True, facecolor='k'))
    # name label
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
    # NMOS arrow: at source pin, pointing INTO channel (inward)
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
    """gate is on LEFT side; tap further left, dot, optional label"""
    tap=(t['gate'][0]-0.6, t['gate'][1])
    line(t['gate'], tap); dot(tap)
    if lbl: text((tap[0]-0.18, tap[1]), lbl, ha='right', fs=11, color=color)
    return tap

def gate_tap_pmos_right(t, lbl=None, color=BLUE):
    tap=(t['gate'][0]+0.6, t['gate'][1])
    line(t['gate'], tap); dot(tap)
    if lbl: text((tap[0]+0.18, tap[1]), lbl, ha='left', fs=11, color=color)
    return tap

def gate_tap_nmos(t, lbl=None, color=BLUE):
    """NMOS gate is on RIGHT side"""
    tap=(t['gate'][0]+0.6, t['gate'][1])
    line(t['gate'], tap); dot(tap)
    if lbl: text((tap[0]+0.18, tap[1]), lbl, ha='left', fs=11, color=color)
    return tap

def diode_pmos(t, lbl, color=BLUE):
    """Tie PMOS gate (LEFT) to its own drain (BELOW), L-route on left side"""
    tap = gate_tap_pmos(t, lbl, color)
    yj = t['drain'][1] - 0.55
    line(tap, (tap[0], yj))
    line((tap[0], yj), (t['drain'][0], yj))
    line((t['drain'][0], yj), t['drain'])
    return tap

def diode_nmos(t, lbl, color=BLUE):
    """Tie NMOS gate (RIGHT) to drain (ABOVE)"""
    tap = gate_tap_nmos(t, lbl, color)
    yj = t['drain'][1] + 0.55
    line(tap, (tap[0], yj))
    line((tap[0], yj), (t['drain'][0], yj))
    line((t['drain'][0], yj), t['drain'])
    return tap

def dash(p1,p2,c=BLUE,lw=1.4): line(p1,p2,c=c,lw=lw,ls='--')
def solid_color(p1,p2,c,lw=1.6): line(p1,p2,c=c,lw=lw,ls='-')

# ============================================================
# LAYOUT
# ============================================================
# x positions
XA   = 2.0    # PMOS bias gen
XB   = 8.5    # NMOS bias gen
XTL  = 19.0   # tail centered
XIP_L= 16.0
XIP_R= 22.0
XL   = 30.0   # LEFT fold leg (mirror REF)
XR   = 37.0   # RIGHT fold leg (V_OUTP)

YVDD = 18.0
# Top-row PMOS centred:
YROW_TOP   = 16.0    # M_P1, M_PN, M_TL, M_P0,L, M_P0,R
# Second PMOS row (cascodes in bias col & fold legs):
YROW_PCASC = 13.0    # M_P2, M_P2,L, M_P2,R
# Input pair (centred lower than top PMOS but higher than cascode):
YROW_INP   = 13.0    # M_INP, M_INN (same y as cascode but in different x band)
# Output / fold-leg mid rail (V_outn, V_OUTP):
Y_OUT      = 11.0
# NMOS cascode row in fold legs:
YROW_NCASC = 9.0
# Fold nodes V_midn fold / V_midp fold:
Y_FOLD     = 7.0
# Bottom NMOS row:
YROW_NBOT  = 5.0
# GND y:
YGND       = 2.5
# Bus tracks in BOTTOM margin (well separated):
Y_BUS_VP2  = 1.4
Y_BUS_VN2  = 0.4
Y_BUS_VN1  = -0.8
# Red signal tracks:
Y_RED_TRACK = 8.0  # ROW for Vmidn/Vmidp drain-to-fold connections
# Top buses:
Y_BUS_VP1  = 17.2
Y_BUS_VP0  = 17.6   # actually we'll put VP0 INSIDE the top margin

# ============================================================
# TITLE + LEGEND
# ============================================================
text(((XA+XR)/2, 19.6),
     'Folded-cascode SE OTA  |  wide-swing R-offset bias  |  top-PMOS-mirror SE',
     ha='center', fs=18, weight='bold')
text(((XA+XR)/2, 19.0),
     r'sky130A LVT,   $V_{DD}=0.9$ V,   $I_{REF}=10$ µA',
     ha='center', fs=11, color=GREY)

# Region labels
text((XA+1.5, 20.5), 'BIAS GENERATORS', ha='center', fs=13, color=BLUE, weight='bold')
text(((XTL+XR)/2, 20.5), 'MAIN AMP', ha='center', fs=13, color='k', weight='bold')

# Vertical divider between bias and main amp
line((13.5, -1.5), (13.5, 18.5), c=GREY, lw=1.0, ls=':')

# ============================================================
# COL A : PMOS bias gen
# ============================================================
vdd_bar(XA, YVDD)
MP1 = pmos(XA, YROW_TOP, '$M_{P1}$', 'left', 'right')
line(MP1['source'], (MP1['source'][0], YVDD)); line((MP1['source'][0], YVDD), (XA, YVDD))
MP2 = pmos(XA, YROW_PCASC, '$M_{P2}$', 'left', 'right')
line(MP1['drain'], MP2['source'])

yRt = MP2['drain'][1]; yRb = yRt - 2.5
line(MP2['drain'], (MP2['drain'][0], yRt)); line((MP2['drain'][0], yRt), (XA, yRt))
resistor((XA, yRt), (XA, yRb), '$R_p$', 'right')
yIt = yRb - 0.4; yIb = yIt - 1.8
line((XA, yRb), (XA, yIt))
csrc((XA, yIt), (XA, yIb), r'$10\,\mu A$', 'right')
line((XA, yIb), (XA, YGND-0.5)); gnd((XA, YGND-0.5))

tapVP1_A = diode_pmos(MP1, '$V_{P1}$')
tapVP2_A = diode_pmos(MP2, '$V_{P2}$')

text((XA, -2.2), 'PMOS bias\n(col A)', ha='center', fs=11, color=BLUE)

# ============================================================
# COL B : NMOS bias gen
# ============================================================
vdd_bar(XB, YVDD)
MPN = pmos(XB, YROW_TOP, '$M_{PN}$', 'left', 'right')
line(MPN['source'], (MPN['source'][0], YVDD)); line((MPN['source'][0], YVDD), (XB, YVDD))
tapPN = gate_tap_pmos(MPN)

yRnT = MPN['drain'][1] - 0.6
line(MPN['drain'], (MPN['drain'][0], yRnT)); line((MPN['drain'][0], yRnT), (XB, yRnT))
yRnB = yRnT - 2.5
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

text((XB, -2.2), 'NMOS bias\n(col B)', ha='center', fs=11, color=BLUE)

# ============================================================
# INPUT STAGE
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

# MINP (left): gate on LEFT, name on RIGHT
MINP = pmos(XIP_L, YROW_INP, '$M_{INP}$', 'left', 'right')
line(MINP['source'], (XIP_L, yTail))
tapINP = (MINP['gate'][0]-0.8, MINP['gate'][1])
line(MINP['gate'], tapINP); dot(tapINP)
text((tapINP[0]-0.15, tapINP[1]), '$V_{inp}$', ha='right', fs=12)

# MINN (right): mirror image — gate on RIGHT, name on LEFT
MINN = pmos(XIP_R, YROW_INP, '$M_{INN}$', 'right', 'left')
line(MINN['source'], (XIP_R, yTail))
tapINN = (MINN['gate'][0]+0.8, MINN['gate'][1])
line(MINN['gate'], tapINN); dot(tapINN)
text((tapINN[0]+0.15, tapINN[1]), '$V_{inn}$', ha='left', fs=12)

text((XTL, -2.2), 'Input stage', ha='center', fs=11, color='k')

# Input pair drains: routed DOWN to a tap dot, labeled, then ACROSS to fold legs (red wires)
# MINP drain -> drop a short segment then dot named V_midn (the source node of red signal net)
ySrcN = MINP['drain'][1] - 0.7
line(MINP['drain'], (MINP['drain'][0], ySrcN)); dot((MINP['drain'][0], ySrcN))
text((MINP['drain'][0]-0.25, ySrcN-0.3), '$V_{midn}$',
     ha='right', fs=10, color=RED)

ySrcP = MINN['drain'][1] - 0.7
line(MINN['drain'], (MINN['drain'][0], ySrcP)); dot((MINN['drain'][0], ySrcP))
text((MINN['drain'][0]+0.25, ySrcP-0.3), '$V_{midp}$',
     ha='left', fs=10, color=RED)

# ============================================================
# LEFT FOLD LEG (XL)
# ============================================================
vdd_bar(XL, YVDD)
MP0L = pmos(XL, YROW_TOP, '$M_{P0,L}$', 'left', 'right')
line(MP0L['source'], (MP0L['source'][0], YVDD)); line((MP0L['source'][0], YVDD), (XL, YVDD))
MP2L = pmos(XL, YROW_PCASC, '$M_{P2,L}$', 'left', 'right')
line(MP0L['drain'], MP2L['source'])
tapP2L = gate_tap_pmos(MP2L)

# V_outn node (mirror reference)
line(MP2L['drain'], (MP2L['drain'][0], Y_OUT)); line((MP2L['drain'][0], Y_OUT), (XL, Y_OUT))
dot((XL, Y_OUT))
text((XL-0.5, Y_OUT+0.25), '$V_{outn}$', ha='right', fs=11, weight='bold')
text((XL-0.5, Y_OUT-0.30), '(mirror ref)', ha='right', fs=9, color=GREY)

# Self-bias: MP0L gate -> RIGHT-side detour up & over to V_outn (use RIGHT side so it doesn't hit nothing)
# Actually the cleanest: gate-left tap goes LEFT around to V_outn
tapP0L = gate_tap_pmos(MP0L, '$V_{P0}$', GREEN)
xself = XL - 2.6
solid_color(tapP0L, (xself, tapP0L[1]), GREEN)
solid_color((xself, tapP0L[1]), (xself, Y_OUT), GREEN)
solid_color((xself, Y_OUT), (XL, Y_OUT), GREEN)

MN2L = nmos(XL, YROW_NCASC, '$M_{N2,L}$', 'right', 'left')
line((XL, Y_OUT), MN2L['drain'])
tapN2L = gate_tap_nmos(MN2L)

# fold node V_midn (between MN2L source and MN1L drain)
line(MN2L['source'], (XL, Y_FOLD)); dot((XL, Y_FOLD))
text((XL-0.5, Y_FOLD+0.25), '$V_{midn}$', ha='right', fs=11, color=RED, weight='bold')
text((XL-0.5, Y_FOLD-0.30), '(fold node)', ha='right', fs=9, color=GREY)

MN1L = nmos(XL, YROW_NBOT, '$M_{N1,L}$', 'right', 'left')
line(MN1L['drain'], (XL, Y_FOLD))
tapN1L = gate_tap_nmos(MN1L)
line(MN1L['source'], (XL, YGND-0.5)); gnd((XL, YGND-0.5))

text((XL, -2.2), 'LEFT fold leg\n(mirror REF)', ha='center', fs=11, color='k')

# ============================================================
# RIGHT FOLD LEG (XR)
# ============================================================
vdd_bar(XR, YVDD)
MP0R = pmos(XR, YROW_TOP, '$M_{P0,R}$', 'left', 'right')
line(MP0R['source'], (MP0R['source'][0], YVDD)); line((MP0R['source'][0], YVDD), (XR, YVDD))
tapP0R = gate_tap_pmos(MP0R, '$V_{P0}$', GREEN)

MP2R = pmos(XR, YROW_PCASC, '$M_{P2,R}$', 'left', 'right')
line(MP0R['drain'], MP2R['source'])
tapP2R = gate_tap_pmos(MP2R)

# V_OUTP
line(MP2R['drain'], (MP2R['drain'][0], Y_OUT)); line((MP2R['drain'][0], Y_OUT), (XR, Y_OUT))
dot((XR, Y_OUT), r=0.15)
text((XR+0.55, Y_OUT), '$V_{OUTP}$', ha='left', fs=14, weight='bold')

MN2R = nmos(XR, YROW_NCASC, '$M_{N2,R}$', 'right', 'left')
line((XR, Y_OUT), MN2R['drain'])
tapN2R = gate_tap_nmos(MN2R)

line(MN2R['source'], (XR, Y_FOLD)); dot((XR, Y_FOLD))
text((XR+0.5, Y_FOLD+0.25), '$V_{midp}$', ha='left', fs=11, color=RED, weight='bold')
text((XR+0.5, Y_FOLD-0.30), '(fold node)', ha='left', fs=9, color=GREY)

MN1R = nmos(XR, YROW_NBOT, '$M_{N1,R}$', 'right', 'left')
line(MN1R['drain'], (XR, Y_FOLD))
tapN1R = gate_tap_nmos(MN1R)
line(MN1R['source'], (XR, YGND-0.5)); gnd((XR, YGND-0.5))

text((XR, -2.2), 'RIGHT fold leg\n(V_OUTP)', ha='center', fs=11, color='k')

# ============================================================
# V_P0 wire (green): tapP0L -> tapP0R routed ABOVE the top PMOS row
# ============================================================
yVP0 = 17.0
solid_color(tapP0L, (tapP0L[0], yVP0), GREEN)
solid_color((tapP0L[0], yVP0), (tapP0R[0], yVP0), GREEN)
solid_color((tapP0R[0], yVP0), tapP0R, GREEN)
text(((XL+XR)/2, yVP0+0.30),
     '$V_{P0}$  (self-bias on LEFT $\\to$ mirror to RIGHT)',
     ha='center', fs=11, color=GREEN, weight='bold')

# ============================================================
# BIAS BUSES — DASHED BLUE
# ============================================================
# VP1 bus across TOP, between bias cols and tail
for tap in (tapVP1_A, tapPN, tapTL):
    dash(tap, (tap[0], Y_BUS_VP1))
dash((tapVP1_A[0], Y_BUS_VP1), (tapTL[0], Y_BUS_VP1))
text(((XA+XB)/2, Y_BUS_VP1+0.3), '$V_{P1}$ bus', ha='center', fs=11, color=BLUE)

# VP2 bus: bias-col-A tapVP2_A -> tapP2L -> tapP2R, route through BOTTOM margin at Y_BUS_VP2
xLeftEdge = -3.2
dash(tapVP2_A, (xLeftEdge, tapVP2_A[1]))
dash((xLeftEdge, tapVP2_A[1]), (xLeftEdge, Y_BUS_VP2))
dash((xLeftEdge, Y_BUS_VP2), (tapP2R[0], Y_BUS_VP2))
dash((tapP2R[0], Y_BUS_VP2), tapP2R)
dash((tapP2L[0], Y_BUS_VP2), tapP2L)
text(((XB+XL)/2, Y_BUS_VP2+0.3), '$V_{P2}$ bus', ha='center', fs=11, color=BLUE)

# VN2 bus: tapVN2_B -> tapN2L -> tapN2R, route in bottom margin Y_BUS_VN2
xRightEdge = 41.0
dash(tapVN2_B, (xRightEdge, tapVN2_B[1]))
dash((xRightEdge, tapVN2_B[1]), (xRightEdge, Y_BUS_VN2))
dash((xRightEdge, Y_BUS_VN2), (tapN2L[0], Y_BUS_VN2))
dash((tapN2L[0], Y_BUS_VN2), tapN2L)
dash((tapN2R[0], Y_BUS_VN2), tapN2R)
text(((XL+XR)/2, Y_BUS_VN2+0.3), '$V_{N2}$ bus', ha='center', fs=11, color=BLUE)

# VN1 bus
xRightEdge2 = 41.6
dash(tapVN1_B, (xRightEdge2, tapVN1_B[1]))
dash((xRightEdge2, tapVN1_B[1]), (xRightEdge2, Y_BUS_VN1))
dash((xRightEdge2, Y_BUS_VN1), (tapN1L[0], Y_BUS_VN1))
dash((tapN1L[0], Y_BUS_VN1), tapN1L)
dash((tapN1R[0], Y_BUS_VN1), tapN1R)
text(((XL+XR)/2, Y_BUS_VN1+0.3), '$V_{N1}$ bus', ha='center', fs=11, color=BLUE)

# ============================================================
# RED SIGNAL NETS: V_midn / V_midp from input drains to fold nodes
# ============================================================
# V_midn: from (MINP.drain.x, ySrcN) -> across Y_RED_TRACK -> down to (XL, Y_FOLD)
line((MINP['drain'][0], ySrcN), (MINP['drain'][0], Y_RED_TRACK), c=RED, lw=1.8, ls='--')
line((MINP['drain'][0], Y_RED_TRACK), (XL, Y_RED_TRACK), c=RED, lw=1.8, ls='--')
line((XL, Y_RED_TRACK), (XL, Y_FOLD), c=RED, lw=1.8, ls='--')
text((((MINP['drain'][0]+XL)/2), Y_RED_TRACK+0.3),
     '$V_{midn}$  (signal: $M_{INP}$ drain  $\\to$  fold node)',
     ha='center', fs=10, color=RED)

# V_midp: from (MINN.drain.x, ySrcP) -> down further then across at Y_RED_TRACK - 1.5 -> up to (XR, Y_FOLD)
Y_RED_TRACK2 = Y_RED_TRACK - 1.2
line((MINN['drain'][0], ySrcP), (MINN['drain'][0], Y_RED_TRACK2), c=RED, lw=1.8, ls='--')
line((MINN['drain'][0], Y_RED_TRACK2), (XR, Y_RED_TRACK2), c=RED, lw=1.8, ls='--')
line((XR, Y_RED_TRACK2), (XR, Y_FOLD), c=RED, lw=1.8, ls='--')
text((((MINN['drain'][0]+XR)/2), Y_RED_TRACK2-0.4),
     '$V_{midp}$  (signal: $M_{INN}$ drain  $\\to$  fold node)',
     ha='center', fs=10, color=RED)

# ============================================================
# LEGEND BOX (top-right)
# ============================================================
lx0, ly0, lw_, lh_ = -3.8, 17.6, 6.0, 2.4
ax.add_patch(FancyBboxPatch((lx0, ly0), lw_, lh_,
                            boxstyle="round,pad=0.15", linewidth=0.8,
                            edgecolor='k', facecolor='#f7f7f7'))
text((lx0+0.3, ly0+lh_-0.4), 'Legend:', ha='left', fs=10, weight='bold')
line((lx0+0.3, ly0+1.55), (lx0+1.3, ly0+1.55), c=BLUE, lw=1.4, ls='--')
text((lx0+1.5, ly0+1.55), 'bias bus', ha='left', fs=9, color=BLUE)
line((lx0+0.3, ly0+1.05), (lx0+1.3, ly0+1.05), c=RED, lw=1.6, ls='--')
text((lx0+1.5, ly0+1.05), 'signal ($V_{mid}$)', ha='left', fs=9, color=RED)
line((lx0+0.3, ly0+0.55), (lx0+1.3, ly0+0.55), c=GREEN, lw=1.6)
text((lx0+1.5, ly0+0.55), 'self-bias ($V_{P0}$)', ha='left', fs=9, color=GREEN)
line((lx0+0.3, ly0+0.15), (lx0+1.3, ly0+0.15), c='k', lw=1.8)
text((lx0+1.5, ly0+0.15), 'circuit wire', ha='left', fs=9)

# ============================================================
# FOOTER NOTES
# ============================================================
text(((XA+XR)/2, -4.6),
     'BIAS: $V_{P1}\\!\\to\\!M_{TL},M_{PN}$;   '
     '$V_{P2}\\!\\to\\!M_{P2,L/R}$;   '
     '$V_{N2}\\!\\to\\!M_{N2,L/R}$;   '
     '$V_{N1}\\!\\to\\!M_{N1,L/R}$.',
     ha='center', fs=11)
text(((XA+XR)/2, -5.3),
     'SE conversion at TOP: $M_{P0,L}$ DIODE-TIED $\\Rightarrow V_{P0}$ drives $M_{P0,R}$.  '
     'Input-pair drain currents $\\to V_{midn},V_{midp}$ fold nodes $\\to$ NMOS-cascode $\\to$ mirror sums at $V_{OUTP}$.',
     ha='center', fs=11)

plt.tight_layout()
out = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
plt.savefig(out, dpi=130, bbox_inches='tight', facecolor='white')
print('OK', out)
