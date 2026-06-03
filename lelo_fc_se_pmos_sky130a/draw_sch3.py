"""
Folded-cascode SE OTA + wide-swing R-offset bias.
Proper MOS symbols, TWO folding legs, NMOS current mirror SE output.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(26, 18))
ax.set_xlim(-3.5, 32)
ax.set_ylim(-4.5, 18)
ax.set_aspect('equal'); ax.axis('off')

BLUE='#1f4fbf'; RED='#c0392b'

def line(p1,p2,c='k',lw=1.8,ls='-'):
    ax.add_line(Line2D([p1[0],p2[0]],[p1[1],p2[1]],color=c,lw=lw,linestyle=ls))
def dot(p,r=0.09,c='k'):
    ax.add_patch(Circle(p,r,facecolor=c,edgecolor=c,zorder=5))
def text(p,s,ha='center',va='center',fs=12,color='k'):
    ax.text(p[0],p[1],s,ha=ha,va=va,fontsize=fs,color=color)

def gnd(p):
    x,y=p
    line((x,y),(x,y-0.15))
    line((x-0.35,y-0.15),(x+0.35,y-0.15),lw=2.4)
    line((x-0.22,y-0.30),(x+0.22,y-0.30),lw=1.8)
    line((x-0.10,y-0.45),(x+0.10,y-0.45),lw=1.3)
def vdd_bar(x,y,w=2.0):
    line((x-w/2,y),(x+w/2,y),lw=3)
    text((x-w/2-0.25,y),'$V_{DD}$',ha='right',va='center',fs=11)

# ---- Proper MOSFET symbols ----
# Channel: vertical line. Gate bar: separated by GAP.
# S/D pins: L-bent OUT from channel ends.
# Arrow on source (PMOS: out of channel; NMOS: into channel).
CH_HALF = 0.7    # half-length of channel bar
GAP     = 0.18   # gap between gate bar and channel
GB_HALF = 0.5    # half-length of gate bar
GSTUB   = 0.9    # gate stub length (from gate bar to gate pin)
SD_OUT  = 0.45   # L-bend horizontal distance for S/D pin

def pmos(xc, yc, name, gate_side='left', name_side='right'):
    """PMOS: source TOP, drain BOTTOM."""
    gsign = -1 if gate_side=='left' else 1
    # Channel bar (vertical thick)
    line((xc, yc-CH_HALF), (xc, yc+CH_HALF), lw=3)
    # Source L-bend (top): from (xc, yc+CH_HALF) horizontal AWAY from gate, then up
    sd_dir = -gsign   # S/D pins go opposite to gate side
    line((xc, yc+CH_HALF), (xc + sd_dir*SD_OUT, yc+CH_HALF))
    line((xc + sd_dir*SD_OUT, yc+CH_HALF), (xc + sd_dir*SD_OUT, yc+CH_HALF+0.35))
    # Drain L-bend (bottom)
    line((xc, yc-CH_HALF), (xc + sd_dir*SD_OUT, yc-CH_HALF))
    line((xc + sd_dir*SD_OUT, yc-CH_HALF), (xc + sd_dir*SD_OUT, yc-CH_HALF-0.35))
    # Gate bar (vertical, offset by GAP toward gate side)
    gbx = xc + gsign*GAP
    line((gbx, yc-GB_HALF), (gbx, yc+GB_HALF), lw=2.4)
    # Gate stub (horizontal from gate bar centre out to gate pin)
    line((gbx, yc), (xc + gsign*(GAP+GSTUB), yc))
    # Arrow on source: PMOS arrow points OUT of channel (away from channel) at source pin
    # source pin is at (xc+sd_dir*SD_OUT, yc+CH_HALF+0.35); arrow head ON the channel-end
    # Place arrow on the source L-bend horizontal segment, pointing AWAY from channel
    ax_arr = xc + sd_dir*0.05
    ay_arr = yc + CH_HALF
    poly = Polygon([(ax_arr, ay_arr),
                    (ax_arr + sd_dir*0.22, ay_arr + 0.13),
                    (ax_arr + sd_dir*0.22, ay_arr - 0.13)],
                   closed=True, facecolor='k')
    ax.add_patch(poly)
    # Name
    nx = xc + (0.95 if name_side=='right' else -0.95)
    text((nx, yc), name, ha='left' if name_side=='right' else 'right', fs=12)
    return {'source': (xc + sd_dir*SD_OUT, yc+CH_HALF+0.35),
            'drain':  (xc + sd_dir*SD_OUT, yc-CH_HALF-0.35),
            'gate':   (xc + gsign*(GAP+GSTUB), yc),
            'src_inner': (xc, yc+CH_HALF),
            'drn_inner': (xc, yc-CH_HALF)}

def nmos(xc, yc, name, gate_side='right', name_side='left'):
    """NMOS: drain TOP, source BOTTOM."""
    gsign = -1 if gate_side=='left' else 1
    line((xc, yc-CH_HALF), (xc, yc+CH_HALF), lw=3)
    sd_dir = -gsign
    # drain L-bend (top)
    line((xc, yc+CH_HALF), (xc + sd_dir*SD_OUT, yc+CH_HALF))
    line((xc + sd_dir*SD_OUT, yc+CH_HALF), (xc + sd_dir*SD_OUT, yc+CH_HALF+0.35))
    # source L-bend (bottom)
    line((xc, yc-CH_HALF), (xc + sd_dir*SD_OUT, yc-CH_HALF))
    line((xc + sd_dir*SD_OUT, yc-CH_HALF), (xc + sd_dir*SD_OUT, yc-CH_HALF-0.35))
    gbx = xc + gsign*GAP
    line((gbx, yc-GB_HALF), (gbx, yc+GB_HALF), lw=2.4)
    line((gbx, yc), (xc + gsign*(GAP+GSTUB), yc))
    # NMOS arrow: points INTO channel at source pin
    ax_arr = xc + sd_dir*0.27
    ay_arr = yc - CH_HALF
    poly = Polygon([(ax_arr, ay_arr),
                    (ax_arr - sd_dir*0.22, ay_arr + 0.13),
                    (ax_arr - sd_dir*0.22, ay_arr - 0.13)],
                   closed=True, facecolor='k')
    ax.add_patch(poly)
    nx = xc + (0.95 if name_side=='right' else -0.95)
    text((nx, yc), name, ha='left' if name_side=='right' else 'right', fs=12)
    return {'source': (xc + sd_dir*SD_OUT, yc-CH_HALF-0.35),
            'drain':  (xc + sd_dir*SD_OUT, yc+CH_HALF+0.35),
            'gate':   (xc + gsign*(GAP+GSTUB), yc),
            'src_inner': (xc, yc-CH_HALF),
            'drn_inner': (xc, yc+CH_HALF)}

def resistor(pt, pb, label, side='right'):
    x=pt[0]; y0=pt[1]; y1=pb[1]; n=6; h=y0-y1; ws=0.22
    pts=[(x,y0)]
    for i in range(n):
        yi=y0-h*(i+0.5)/n
        xi=x+(ws if i%2==0 else -ws)
        pts.append((xi,yi))
    pts.append((x,y1))
    for a,b in zip(pts[:-1],pts[1:]):
        line(a,b)
    lx=x+(0.55 if side=='right' else -0.55)
    text((lx,(y0+y1)/2), label, ha='left' if side=='right' else 'right', fs=12)

def csrc(pt, pb, label, side='right'):
    x=pt[0]; yc=(pt[1]+pb[1])/2; r=0.42
    line(pt,(x,yc+r)); line((x,yc-r),pb)
    ax.add_patch(Circle((x,yc),r,facecolor='white',edgecolor='k',lw=1.6))
    line((x,yc+r*0.55),(x,yc-r*0.55))
    poly=Polygon([(x-0.15,yc-r*0.25),(x+0.15,yc-r*0.25),(x,yc-r*0.55)],
                 closed=True, facecolor='k')
    ax.add_patch(poly)
    lx=x+(0.65 if side=='right' else -0.65)
    text((lx,yc), label, ha='left' if side=='right' else 'right', fs=12)

# ============================================================
# COLUMN POSITIONS
# ============================================================
XA = 1.5     # PMOS bias gen
XB = 7.5     # NMOS bias gen
XL = 14.0    # LEFT fold leg
XR = 22.0    # RIGHT fold leg (VOUT side)
# Input pair lives between XL and XR
XIP_L = XL + 2.0   # MINP at (XIP_L, ytail_branch)
XIP_R = XR - 2.0   # MINN at (XIP_R, ytail_branch)
XTL   = (XIP_L + XIP_R)/2   # MTL centered

YVDD = 14.5

# ============================================================
# TITLE
# ============================================================
text(((XA+XR)/2, 16.7),
     'Folded-cascode SE OTA   |   wide-swing R-offset bias   |   TWO folding legs',
     ha='center', fs=17)
text(((XA+XR)/2, 16.0),
     r'sky130A LVT,  $V_{DD}=0.9$ V,  $I_{REF}=10$ µA  |  NMOS current mirror at bottom => SE output at right',
     ha='center', fs=11)

# ============================================================
# COL A : PMOS bias gen
# ============================================================
vdd_bar(XA, YVDD)
MP1 = pmos(XA, 13.0, '$M_{P1}$', gate_side='left', name_side='right')
line(MP1['source'], (MP1['source'][0], YVDD)); line((MP1['source'][0],YVDD),(XA,YVDD))
MP2 = pmos(XA, 11.0, '$M_{P2}$', gate_side='left', name_side='right')
line(MP1['drain'], MP2['source'])
yRt=MP2['drain'][1]; yRb=yRt-2.0
line(MP2['drain'],(MP2['drain'][0], yRt)); line((MP2['drain'][0],yRt),(XA,yRt))
resistor((XA,yRt),(XA,yRb),'$R_p$','right')
yIt=yRb-0.4; yIb=yIt-1.5
line((XA,yRb),(XA,yIt))
csrc((XA,yIt),(XA,yIb), r'$10\,\mu A$','right')
line((XA,yIb),(XA,-0.3)); gnd((XA,-0.3))

# diode-tie MP1 (gate -> drain on left)
tapP1 = (XA-2.2, MP1['gate'][1])
line(MP1['gate'], tapP1); dot(tapP1)
text((tapP1[0]-0.2, tapP1[1]), '$V_{P1}$', ha='right', fs=12, color=BLUE)
yj=MP1['drain'][1]
line(tapP1, (tapP1[0], yj-0.5))
line((tapP1[0], yj-0.5), (MP1['drain'][0], yj-0.5))
line((MP1['drain'][0], yj-0.5), MP1['drain'])

# diode-tie MP2
tapP2 = (XA-2.2, MP2['gate'][1])
line(MP2['gate'], tapP2); dot(tapP2)
text((tapP2[0]-0.2, tapP2[1]), '$V_{P2}$', ha='right', fs=12, color=BLUE)
yj=MP2['drain'][1]
line(tapP2, (tapP2[0], yj-0.5))
line((tapP2[0], yj-0.5), (MP2['drain'][0], yj-0.5))
line((MP2['drain'][0], yj-0.5), MP2['drain'])

text((XA,-1.3),'PMOS bias gen',ha='center',fs=12,color=BLUE)

# ============================================================
# COL B : NMOS bias gen
# ============================================================
vdd_bar(XB,YVDD)
MPN = pmos(XB, 13.0, '$M_{PN}$', gate_side='left', name_side='right')
line(MPN['source'], (MPN['source'][0], YVDD)); line((MPN['source'][0],YVDD),(XB,YVDD))
tapPN=(XB-2.2, MPN['gate'][1]); line(MPN['gate'], tapPN); dot(tapPN)

yRnT=MPN['drain'][1]-0.6
line(MPN['drain'],(MPN['drain'][0], yRnT)); line((MPN['drain'][0], yRnT),(XB,yRnT))
yRnB=yRnT-2.0
resistor((XB,yRnT),(XB,yRnB),'$R_n$','right')

MN2 = nmos(XB, yRnB-CH_HALF-0.35, '$M_{N2}$', gate_side='right', name_side='left')
line((XB,yRnB), MN2['drain'])
MN1 = nmos(XB, MN2['source'][1]-CH_HALF-0.35, '$M_{N1}$', gate_side='right', name_side='left')
line(MN1['drain'], MN2['source'])
line(MN1['source'],(XB,-0.3)); gnd((XB,-0.3))

tapN2=(XB+2.2, MN2['gate'][1]); line(MN2['gate'], tapN2); dot(tapN2)
text((tapN2[0]+0.2, tapN2[1]), '$V_{N2}$', ha='left', fs=12, color=BLUE)
yj=MN2['drain'][1]
line(tapN2,(tapN2[0], yj+0.5))
line((tapN2[0], yj+0.5),(MN2['drain'][0], yj+0.5))
line((MN2['drain'][0], yj+0.5), MN2['drain'])

tapN1=(XB+2.2, MN1['gate'][1]); line(MN1['gate'], tapN1); dot(tapN1)
text((tapN1[0]+0.2, tapN1[1]), '$V_{N1}$', ha='left', fs=12, color=BLUE)
yj=MN1['drain'][1]
line(tapN1,(tapN1[0], yj+0.5))
line((tapN1[0], yj+0.5),(MN1['drain'][0], yj+0.5))
line((MN1['drain'][0], yj+0.5), MN1['drain'])

text((XB,-1.3),'NMOS bias gen',ha='center',fs=12,color=BLUE)

# ============================================================
# TAIL + INPUT PAIR (centered between XL and XR)
# ============================================================
vdd_bar(XTL, YVDD)
MTL = pmos(XTL, 13.0, '$M_{TL}$', gate_side='left', name_side='right')
line(MTL['source'], (MTL['source'][0], YVDD)); line((MTL['source'][0],YVDD),(XTL,YVDD))
tapTL = (XTL-2.2, MTL['gate'][1]); line(MTL['gate'], tapTL); dot(tapTL)

yTail = MTL['drain'][1] - 0.6
line(MTL['drain'], (MTL['drain'][0], yTail)); line((MTL['drain'][0],yTail),(XTL,yTail))
dot((XTL,yTail))
text((XTL+0.2, yTail+0.3), '$V_{tail}$', ha='left', fs=11)

# rail from XIP_L to XIP_R at yTail
line((XIP_L, yTail),(XIP_R, yTail))

# MINP (gate left=Vinp) and MINN (gate right=Vinn)
MINP = pmos(XIP_L, yTail - CH_HALF - 0.35, '$M_{INP}$', gate_side='left', name_side='right')
line(MINP['source'],(XIP_L, yTail))
tapINP=(MINP['gate'][0]-1.0, MINP['gate'][1])
line(MINP['gate'], tapINP); dot(tapINP)
text((tapINP[0]-0.2, tapINP[1]),'$V_{inp}$',ha='right',fs=12)

MINN = pmos(XIP_R, yTail - CH_HALF - 0.35, '$M_{INN}$', gate_side='right', name_side='left')
line(MINN['source'],(XIP_R, yTail))
tapINN=(MINN['gate'][0]+1.0, MINN['gate'][1])
line(MINN['gate'], tapINN); dot(tapINN)
text((tapINN[0]+0.2, tapINN[1]),'$V_{inn}$',ha='left',fs=12)

text((XTL,-1.3),'Tail + PMOS input pair', ha='center', fs=12, color=BLUE)

# Input pair drains go DOWN to fold nodes V_X (left) and V_Y (right)
# Fold nodes sit BELOW the input pair and AT XL (left leg) and XR (right leg)
yFold = yTail - 4.5   # well below input pair drains
# horizontal then down from MINP drain to (XL, yFold)
line(MINP['drain'], (MINP['drain'][0], MINP['drain'][1]-0.4))
line((MINP['drain'][0], MINP['drain'][1]-0.4), (XL, MINP['drain'][1]-0.4))
line((XL, MINP['drain'][1]-0.4), (XL, yFold))
dot((XL,yFold))
text((XL-0.4, yFold+0.3),'$V_X$',ha='right',fs=12,color=RED)

line(MINN['drain'], (MINN['drain'][0], MINN['drain'][1]-0.4))
line((MINN['drain'][0], MINN['drain'][1]-0.4), (XR, MINN['drain'][1]-0.4))
line((XR, MINN['drain'][1]-0.4), (XR, yFold))
dot((XR,yFold))
text((XR+0.4, yFold+0.3),'$V_Y\\,=\\,V_{OUT}$',ha='left',fs=12,color=RED)

# ============================================================
# LEFT FOLD LEG (col XL)
# ============================================================
vdd_bar(XL, YVDD)
MP0L = pmos(XL, 13.0, '$M_{P0,L}$', gate_side='left', name_side='right')
line(MP0L['source'],(MP0L['source'][0], YVDD)); line((MP0L['source'][0],YVDD),(XL,YVDD))
tapP0L=(XL-2.2, MP0L['gate'][1]); line(MP0L['gate'], tapP0L); dot(tapP0L)

MP2L = pmos(XL, 11.0, '$M_{P2,L}$', gate_side='left', name_side='right')
line(MP0L['drain'], MP2L['source'])
tapP2L=(XL-2.2, MP2L['gate'][1]); line(MP2L['gate'], tapP2L); dot(tapP2L)

# MP2L.drain -> V_X (yFold)
line(MP2L['drain'], (MP2L['drain'][0], yFold))
line((MP2L['drain'][0], yFold),(XL, yFold))

# NMOS cascode MN2L below V_X
MN2L = nmos(XL, yFold - CH_HALF - 0.8, '$M_{N2,L}$', gate_side='right', name_side='left')
line((XL,yFold), MN2L['drain'])
tapN2L=(XL+2.2, MN2L['gate'][1]); line(MN2L['gate'], tapN2L); dot(tapN2L)

# Bottom NMOS mirror — LEFT side is DIODE-TIED (sums folded current, forms mirror ref)
MN1L = nmos(XL, MN2L['source'][1] - CH_HALF - 0.35, '$M_{N1,L}$', gate_side='right', name_side='left')
line(MN1L['drain'], MN2L['source'])
line(MN1L['source'],(XL,-0.3)); gnd((XL,-0.3))
# diode-tie: gate -> drain on RIGHT side
tapMRR=(XL+2.2, MN1L['gate'][1]); line(MN1L['gate'], tapMRR); dot(tapMRR)
text((tapMRR[0]+0.2, tapMRR[1]),'$V_{mir}$',ha='left',fs=11,color=RED)
yj=MN1L['drain'][1]
line(tapMRR,(tapMRR[0], yj+0.5))
line((tapMRR[0], yj+0.5),(MN1L['drain'][0], yj+0.5))
line((MN1L['drain'][0], yj+0.5), MN1L['drain'])

text((XL,-1.3),'LEFT fold leg\n(mirror reference)', ha='center', fs=11, color=BLUE)

# ============================================================
# RIGHT FOLD LEG (col XR) — VOUT side
# ============================================================
vdd_bar(XR, YVDD)
MP0R = pmos(XR, 13.0, '$M_{P0,R}$', gate_side='left', name_side='right')
line(MP0R['source'],(MP0R['source'][0], YVDD)); line((MP0R['source'][0],YVDD),(XR,YVDD))
tapP0R=(XR-2.2, MP0R['gate'][1]); line(MP0R['gate'], tapP0R); dot(tapP0R)

MP2R = pmos(XR, 11.0, '$M_{P2,R}$', gate_side='left', name_side='right')
line(MP0R['drain'], MP2R['source'])
tapP2R=(XR-2.2, MP2R['gate'][1]); line(MP2R['gate'], tapP2R); dot(tapP2R)

line(MP2R['drain'], (MP2R['drain'][0], yFold))
line((MP2R['drain'][0], yFold),(XR, yFold))

# VOUT label at V_Y node
dot((XR, yFold), r=0.13)
text((XR+0.4, yFold-0.5), '(SE output)', ha='left', fs=10, color=RED)

MN2R = nmos(XR, yFold - CH_HALF - 0.8, '$M_{N2,R}$', gate_side='right', name_side='left')
line((XR,yFold), MN2R['drain'])
tapN2R=(XR+2.2, MN2R['gate'][1]); line(MN2R['gate'], tapN2R); dot(tapN2R)

# Bottom NMOS mirror RIGHT — gate driven by V_mir (mirror output, NOT diode-tied)
MN1R = nmos(XR, MN2R['source'][1] - CH_HALF - 0.35, '$M_{N1,R}$', gate_side='right', name_side='left')
line(MN1R['drain'], MN2R['source'])
line(MN1R['source'],(XR,-0.3)); gnd((XR,-0.3))
tapMR=(XR+2.2, MN1R['gate'][1]); line(MN1R['gate'], tapMR); dot(tapMR)

text((XR,-1.3),'RIGHT fold leg\n(VOUT side, mirror out)', ha='center', fs=11, color=BLUE)

# ============================================================
# BUSES (dashed blue)
# ============================================================
def dash(p1,p2,c=BLUE):
    line(p1,p2,c=c,lw=1.4,ls='--')

# VP1 bus across top of all 5 P-bias columns: MP1, MPN, MTL, MP0L, MP0R
yVP1 = 14.0   # just under VDD
for tap in (tapP1, tapPN, tapTL, tapP0L, tapP0R):
    dash(tap, (tap[0], yVP1))
dash((tapP1[0], yVP1), (tapP0R[0], yVP1))
text(((tapP1[0]+tapPN[0])/2, yVP1+0.25), '$V_{P1}$ bus', ha='center', fs=11, color=BLUE)

# VP2 bus: tapP2 (col A) -> tapP2L -> tapP2R, routed in LOWER LEFT margin
yVP2 = -2.2
xLeft = -2.8
dash(tapP2, (xLeft, tapP2[1]))
dash((xLeft, tapP2[1]), (xLeft, yVP2))
dash((xLeft, yVP2), (tapP2R[0], yVP2))
dash((tapP2R[0], yVP2), tapP2R)
# branch tap to tapP2L
dash((tapP2L[0], yVP2), tapP2L)
text(((XB+XL)/2, yVP2+0.30), '$V_{P2}$ bus', ha='center', fs=11, color=BLUE)

# VN2 bus: tapN2 (col B) -> tapN2L -> tapN2R, routed in LOWER margin at y=-3.0
yVN2 = -3.4
xRight = 30.0
dash(tapN2, (xRight, tapN2[1]))
dash((xRight, tapN2[1]), (xRight, yVN2))
dash((xRight, yVN2), (tapN2L[0], yVN2))
dash((tapN2L[0], yVN2), tapN2L)
dash((tapN2R[0], yVN2), tapN2R)
text(((XL+XR)/2, yVN2+0.30), '$V_{N2}$ bus', ha='center', fs=11, color=BLUE)

# V_mir bus (red): mirror gate from MN1L (diode-tied tap) -> MN1R gate
# This stays on the RIGHT side of left leg, runs across to right leg
yVmir = (tapMRR[1] + tapMR[1])/2  # same y anyway
line(tapMRR, tapMR, c=RED, lw=1.5, ls='--')
text(((XL+XR)/2, yVmir+0.25), '$V_{mir}$ (mirror gate)', ha='center', fs=11, color=RED)

# ============================================================
# FOOTER
# ============================================================
text(((XA+XR)/2, -4.0),
     'TWO folding legs:  PMOS top current sources $M_{P0,L/R}$ deliver 2$I_B$;  '
     'PMOS cascodes $M_{P2,L/R}$;  fold nodes $V_X$ / $V_Y$ where input-pair drains merge;  '
     'NMOS cascodes $M_{N2,L/R}$;  bottom NMOS mirror ($M_{N1,L}$ diode-tied = ref, '
     '$M_{N1,R}$ = mirror out) converts diff current to SE output at $V_Y$ = $V_{OUT}$.',
     ha='center', fs=10)

plt.tight_layout()
out='/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
plt.savefig(out, dpi=130, bbox_inches='tight', facecolor='white')
print('OK', out)
