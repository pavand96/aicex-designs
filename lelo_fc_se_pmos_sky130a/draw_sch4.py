"""
Folded-cascode SE OTA + wide-swing R-offset bias.
Full circuit: bias gen (cols A,B) + main amp (input pair + 2 fold legs).
Top PMOS mirror = SE conversion (left MP0 diode-tied, drives right).
Fold nodes Vmidn/Vmidp = bottom of NMOS-cascode (above MN1), shared with input-pair drains.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(28, 20))
ax.set_xlim(-4, 36); ax.set_ylim(-5.5, 19)
ax.set_aspect('equal'); ax.axis('off')

BLUE='#1f4fbf'; RED='#c0392b'; GREEN='#0a8a4a'

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
    text((x-w/2-0.2,y),'$V_{DD}$',ha='right',va='center',fs=11)

CH=0.7; GAP=0.18; GBH=0.5; GST=0.9; SD=0.45

def pmos(xc,yc,name,gate_side='left',name_side='right'):
    gs=-1 if gate_side=='left' else 1
    line((xc,yc-CH),(xc,yc+CH),lw=3)
    sd=-gs
    line((xc,yc+CH),(xc+sd*SD,yc+CH))
    line((xc+sd*SD,yc+CH),(xc+sd*SD,yc+CH+0.35))
    line((xc,yc-CH),(xc+sd*SD,yc-CH))
    line((xc+sd*SD,yc-CH),(xc+sd*SD,yc-CH-0.35))
    gbx=xc+gs*GAP
    line((gbx,yc-GBH),(gbx,yc+GBH),lw=2.4)
    line((gbx,yc),(xc+gs*(GAP+GST),yc))
    # PMOS arrow OUT of source
    ax_=xc+sd*0.05; ay_=yc+CH
    ax.add_patch(Polygon([(ax_,ay_),(ax_+sd*0.22,ay_+0.13),(ax_+sd*0.22,ay_-0.13)],
                         closed=True,facecolor='k'))
    nx=xc+(0.95 if name_side=='right' else -0.95)
    text((nx,yc),name,ha='left' if name_side=='right' else 'right',fs=11)
    return {'source':(xc+sd*SD,yc+CH+0.35),'drain':(xc+sd*SD,yc-CH-0.35),
            'gate':(xc+gs*(GAP+GST),yc)}

def nmos(xc,yc,name,gate_side='right',name_side='left'):
    gs=-1 if gate_side=='left' else 1
    line((xc,yc-CH),(xc,yc+CH),lw=3)
    sd=-gs
    line((xc,yc+CH),(xc+sd*SD,yc+CH))
    line((xc+sd*SD,yc+CH),(xc+sd*SD,yc+CH+0.35))
    line((xc,yc-CH),(xc+sd*SD,yc-CH))
    line((xc+sd*SD,yc-CH),(xc+sd*SD,yc-CH-0.35))
    gbx=xc+gs*GAP
    line((gbx,yc-GBH),(gbx,yc+GBH),lw=2.4)
    line((gbx,yc),(xc+gs*(GAP+GST),yc))
    ax_=xc+sd*0.27; ay_=yc-CH
    ax.add_patch(Polygon([(ax_,ay_),(ax_-sd*0.22,ay_+0.13),(ax_-sd*0.22,ay_-0.13)],
                         closed=True,facecolor='k'))
    nx=xc+(0.95 if name_side=='right' else -0.95)
    text((nx,yc),name,ha='left' if name_side=='right' else 'right',fs=11)
    return {'source':(xc+sd*SD,yc-CH-0.35),'drain':(xc+sd*SD,yc+CH+0.35),
            'gate':(xc+gs*(GAP+GST),yc)}

def resistor(pt,pb,label,side='right'):
    x=pt[0]; y0=pt[1]; y1=pb[1]; n=6; h=y0-y1; ws=0.22
    pts=[(x,y0)]
    for i in range(n):
        yi=y0-h*(i+0.5)/n
        xi=x+(ws if i%2==0 else -ws)
        pts.append((xi,yi))
    pts.append((x,y1))
    for a,b in zip(pts[:-1],pts[1:]): line(a,b)
    lx=x+(0.55 if side=='right' else -0.55)
    text((lx,(y0+y1)/2),label,ha='left' if side=='right' else 'right',fs=11)

def csrc(pt,pb,label,side='right'):
    x=pt[0]; yc=(pt[1]+pb[1])/2; r=0.42
    line(pt,(x,yc+r)); line((x,yc-r),pb)
    ax.add_patch(Circle((x,yc),r,facecolor='white',edgecolor='k',lw=1.6))
    line((x,yc+r*0.55),(x,yc-r*0.55))
    ax.add_patch(Polygon([(x-0.15,yc-r*0.25),(x+0.15,yc-r*0.25),(x,yc-r*0.55)],
                         closed=True,facecolor='k'))
    lx=x+(0.65 if side=='right' else -0.65)
    text((lx,yc),label,ha='left' if side=='right' else 'right',fs=11)

def diode_left(t,glbl):
    """diode-tie a PMOS/NMOS-type symbol whose gate is on its LEFT, drain BELOW."""
    tap=(t['gate'][0]-0.5,t['gate'][1])
    line(t['gate'],tap); dot(tap)
    text((tap[0]-0.15,tap[1]),glbl,ha='right',fs=11,color=BLUE)
    # short straight down to drain inner x and across
    line(tap,(tap[0],t['drain'][1]-0.4))
    line((tap[0],t['drain'][1]-0.4),(t['drain'][0],t['drain'][1]-0.4))
    line((t['drain'][0],t['drain'][1]-0.4),t['drain'])

def diode_right(t,glbl):
    """NMOS gate RIGHT, drain ABOVE."""
    tap=(t['gate'][0]+0.5,t['gate'][1])
    line(t['gate'],tap); dot(tap)
    text((tap[0]+0.15,tap[1]),glbl,ha='left',fs=11,color=BLUE)
    line(tap,(tap[0],t['drain'][1]+0.4))
    line((tap[0],t['drain'][1]+0.4),(t['drain'][0],t['drain'][1]+0.4))
    line((t['drain'][0],t['drain'][1]+0.4),t['drain'])

def dash(p1,p2,c=BLUE,lw=1.4):
    line(p1,p2,c=c,lw=lw,ls='--')

# ============================================================
# Columns
# ============================================================
XA  = 1.5   # PMOS bias gen
XB  = 7.5   # NMOS bias gen
# Input pair area:
XTL = 13.0  # tail M_TL centered here
XIP_L = XTL-2.0   # MINP
XIP_R = XTL+2.0   # MINN
# Fold legs:
XL  = 22.0  # LEFT fold leg (mirror REF, diode-tied top)
XR  = 28.0  # RIGHT fold leg (Vout)

YVDD = 16.0

# ============================================================
# TITLE
# ============================================================
text(((XA+XR)/2,18.4),
     'Folded-cascode SE OTA  |  wide-swing R-offset bias  |  top-PMOS-mirror SE conversion',
     ha='center',fs=17)
text(((XA+XR)/2,17.7),
     r'sky130A LVT,  $V_{DD}=0.9$ V,  $I_{REF}=10$ µA',
     ha='center',fs=11)

# ============================================================
# COL A : PMOS bias gen  (MP1 diode VP1, MP2 diode VP2, Rp, 10uA sink)
# ============================================================
vdd_bar(XA,YVDD)
MP1=pmos(XA,14.5,'$M_{P1}$','left','right')
line(MP1['source'],(MP1['source'][0],YVDD)); line((MP1['source'][0],YVDD),(XA,YVDD))
MP2=pmos(XA,12.5,'$M_{P2}$','left','right')
line(MP1['drain'],MP2['source'])
yRt=MP2['drain'][1]; yRb=yRt-2.0
line(MP2['drain'],(MP2['drain'][0],yRt)); line((MP2['drain'][0],yRt),(XA,yRt))
resistor((XA,yRt),(XA,yRb),'$R_p$','right')
yIt=yRb-0.4; yIb=yIt-1.4
line((XA,yRb),(XA,yIt))
csrc((XA,yIt),(XA,yIb),r'$10\,\mu A$','right')
line((XA,yIb),(XA,0.0)); gnd((XA,0.0))
diode_left(MP1,'$V_{P1}$')
diode_left(MP2,'$V_{P2}$')
text((XA,-1.6),'PMOS bias gen',ha='center',fs=12,color=BLUE)

# tap coords for buses (re-extract)
tapVP1_A=(MP1['gate'][0]-0.5, MP1['gate'][1])
tapVP2_A=(MP2['gate'][0]-0.5, MP2['gate'][1])

# ============================================================
# COL B : NMOS bias gen
# ============================================================
vdd_bar(XB,YVDD)
MPN=pmos(XB,14.5,'$M_{PN}$','left','right')
line(MPN['source'],(MPN['source'][0],YVDD)); line((MPN['source'][0],YVDD),(XB,YVDD))
tapPN=(MPN['gate'][0]-0.5,MPN['gate'][1]); line(MPN['gate'],tapPN); dot(tapPN)

yRnT=MPN['drain'][1]-0.6
line(MPN['drain'],(MPN['drain'][0],yRnT)); line((MPN['drain'][0],yRnT),(XB,yRnT))
yRnB=yRnT-2.0
resistor((XB,yRnT),(XB,yRnB),'$R_n$','right')

MN2b=nmos(XB,yRnB-CH-0.35,'$M_{N2b}$','right','left')
line((XB,yRnB),MN2b['drain'])
MN1b=nmos(XB,MN2b['source'][1]-CH-0.35,'$M_{N1b}$','right','left')
line(MN1b['drain'],MN2b['source'])
line(MN1b['source'],(XB,0.0)); gnd((XB,0.0))
diode_right(MN2b,'$V_{N2}$')
diode_right(MN1b,'$V_{N1}$')
text((XB,-1.6),'NMOS bias gen',ha='center',fs=12,color=BLUE)
tapVN2_B=(MN2b['gate'][0]+0.5,MN2b['gate'][1])
tapVN1_B=(MN1b['gate'][0]+0.5,MN1b['gate'][1])

# ============================================================
# INPUT STAGE : Tail M_TL + input pair MINP, MINN
# ============================================================
vdd_bar(XTL,YVDD)
MTL=pmos(XTL,14.5,'$M_{TL}$','left','right')
line(MTL['source'],(MTL['source'][0],YVDD)); line((MTL['source'][0],YVDD),(XTL,YVDD))
tapTL=(MTL['gate'][0]-0.5,MTL['gate'][1]); line(MTL['gate'],tapTL); dot(tapTL)
yTail=MTL['drain'][1]-0.6
line(MTL['drain'],(MTL['drain'][0],yTail)); line((MTL['drain'][0],yTail),(XTL,yTail))
dot((XTL,yTail))
text((XTL+0.2,yTail+0.3),'$V_{tail}$',ha='left',fs=10)
line((XIP_L,yTail),(XIP_R,yTail))

MINP=pmos(XIP_L,yTail-CH-0.35,'$M_{INP}$','left','right')
line(MINP['source'],(XIP_L,yTail))
tapINP=(MINP['gate'][0]-0.9,MINP['gate'][1])
line(MINP['gate'],tapINP); dot(tapINP)
text((tapINP[0]-0.2,tapINP[1]),'$V_{inp}$',ha='right',fs=11)

MINN=pmos(XIP_R,yTail-CH-0.35,'$M_{INN}$','right','left')
line(MINN['source'],(XIP_R,yTail))
tapINN=(MINN['gate'][0]+0.9,MINN['gate'][1])
line(MINN['gate'],tapINN); dot(tapINN)
text((tapINN[0]+0.2,tapINN[1]),'$V_{inn}$',ha='left',fs=11)

text((XTL,-1.6),'Tail + PMOS input pair',ha='center',fs=12,color=BLUE)

# Input pair drains -> Vmidn (left, MINP.drain) and Vmidp (right, MINN.drain)
# These nets travel RIGHT and merge into fold legs at the bottom-NMOS-cascode mid
# We name the source of those nets here:
ymid_src_n = MINP['drain'][1] - 0.4  # just below drain
line(MINP['drain'],(MINP['drain'][0], ymid_src_n))
dot((MINP['drain'][0], ymid_src_n))
text((MINP['drain'][0]-0.3, ymid_src_n-0.35),'$V_{midn}$',ha='right',fs=10,color=RED)

ymid_src_p = MINN['drain'][1] - 0.4
line(MINN['drain'],(MINN['drain'][0], ymid_src_p))
dot((MINN['drain'][0], ymid_src_p))
text((MINN['drain'][0]+0.3, ymid_src_p-0.35),'$V_{midp}$',ha='left',fs=10,color=RED)

# ============================================================
# LEFT FOLD LEG (col XL) — top PMOS DIODE-TIED (self-bias VP0)
# ============================================================
vdd_bar(XL,YVDD)
MP0L=pmos(XL,14.5,'$M_{P0,L}$','left','right')
line(MP0L['source'],(MP0L['source'][0],YVDD)); line((MP0L['source'][0],YVDD),(XL,YVDD))
MP2L=pmos(XL,12.5,'$M_{P2,L}$','left','right')
line(MP0L['drain'],MP2L['source'])
tapP2L=(MP2L['gate'][0]-0.5,MP2L['gate'][1]); line(MP2L['gate'],tapP2L); dot(tapP2L)

# Voutn node (low-Z mirror-ref side, between MP2L.drain and MN2L.drain)
yVoutn = MP2L['drain'][1]-0.7
line(MP2L['drain'],(MP2L['drain'][0],yVoutn)); line((MP2L['drain'][0],yVoutn),(XL,yVoutn))
dot((XL,yVoutn))
text((XL-0.4,yVoutn+0.25),'$V_{outn}$ (mirror ref)',ha='right',fs=10)

# DIODE-TIE MP0L: gate (LEFT) -> down to V_outn node (since MP0L's drain via MP2L cascode IS V_outn at low-freq mirror reference)
# Wide-swing top mirror: actually MP0L gate tied DIRECTLY to its own drain (= MP2L source) — but standard variant ties gate to Voutn through bottom of cascode pair
# We'll show: gate -> down LEFT-side -> across to V_outn
tapP0L=(MP0L['gate'][0]-0.5,MP0L['gate'][1]); line(MP0L['gate'],tapP0L); dot(tapP0L)
text((tapP0L[0]-0.15,tapP0L[1]),'$V_{P0}$',ha='right',fs=11,color=GREEN)
# Self-bias loop: tapP0L --down left edge-- across at yVoutn back into Voutn node
xleft_loop = XL-2.0
line(tapP0L,(xleft_loop,tapP0L[1]),c=GREEN,lw=1.5)
line((xleft_loop,tapP0L[1]),(xleft_loop,yVoutn),c=GREEN,lw=1.5)
line((xleft_loop,yVoutn),(XL,yVoutn),c=GREEN,lw=1.5)

MN2L=nmos(XL,yVoutn-CH-0.7,'$M_{N2,L}$','right','left')
line((XL,yVoutn),MN2L['drain'])
tapN2L=(MN2L['gate'][0]+0.5,MN2L['gate'][1]); line(MN2L['gate'],tapN2L); dot(tapN2L)

# Fold node Vmidn (between MN2L source and MN1L drain) — joined by MINP drain wire
yfold_L = MN2L['source'][1] - 0.5
line(MN2L['source'],(XL,yfold_L))
dot((XL,yfold_L))
text((XL-0.4,yfold_L+0.25),'$V_{midn}$ (fold)',ha='right',fs=10,color=RED)

MN1L=nmos(XL,yfold_L-CH-0.35,'$M_{N1,L}$','right','left')
line(MN1L['drain'],(XL,yfold_L))
tapN1L=(MN1L['gate'][0]+0.5,MN1L['gate'][1]); line(MN1L['gate'],tapN1L); dot(tapN1L)
line(MN1L['source'],(XL,0.0)); gnd((XL,0.0))

text((XL,-1.6),'LEFT fold leg\n(mirror REF)',ha='center',fs=11,color=BLUE)

# ============================================================
# RIGHT FOLD LEG (col XR) — VOUT side; MP0R gate driven by VP0 (self-bias from L)
# ============================================================
vdd_bar(XR,YVDD)
MP0R=pmos(XR,14.5,'$M_{P0,R}$','left','right')
line(MP0R['source'],(MP0R['source'][0],YVDD)); line((MP0R['source'][0],YVDD),(XR,YVDD))
tapP0R=(MP0R['gate'][0]-0.5,MP0R['gate'][1]); line(MP0R['gate'],tapP0R); dot(tapP0R)

MP2R=pmos(XR,12.5,'$M_{P2,R}$','left','right')
line(MP0R['drain'],MP2R['source'])
tapP2R=(MP2R['gate'][0]-0.5,MP2R['gate'][1]); line(MP2R['gate'],tapP2R); dot(tapP2R)

yVoutp=MP2R['drain'][1]-0.7
line(MP2R['drain'],(MP2R['drain'][0],yVoutp)); line((MP2R['drain'][0],yVoutp),(XR,yVoutp))
dot((XR,yVoutp),r=0.14)
text((XR+0.45,yVoutp),'$V_{OUTP}$',ha='left',fs=13)

MN2R=nmos(XR,yVoutp-CH-0.7,'$M_{N2,R}$','right','left')
line((XR,yVoutp),MN2R['drain'])
tapN2R=(MN2R['gate'][0]+0.5,MN2R['gate'][1]); line(MN2R['gate'],tapN2R); dot(tapN2R)

yfold_R = MN2R['source'][1] - 0.5
line(MN2R['source'],(XR,yfold_R))
dot((XR,yfold_R))
text((XR+0.4,yfold_R+0.25),'$V_{midp}$ (fold)',ha='left',fs=10,color=RED)

MN1R=nmos(XR,yfold_R-CH-0.35,'$M_{N1,R}$','right','left')
line(MN1R['drain'],(XR,yfold_R))
tapN1R=(MN1R['gate'][0]+0.5,MN1R['gate'][1]); line(MN1R['gate'],tapN1R); dot(tapN1R)
line(MN1R['source'],(XR,0.0)); gnd((XR,0.0))

text((XR,-1.6),'RIGHT fold leg\n(VOUT)',ha='center',fs=11,color=BLUE)

# ============================================================
# VP0 connection: tapP0L -> tapP0R (top PMOS mirror gate, GREEN)
# ============================================================
yVP0bus = 15.5
line(tapP0L,(tapP0L[0],yVP0bus),c=GREEN,lw=1.5)
line((tapP0L[0],yVP0bus),(tapP0R[0],yVP0bus),c=GREEN,lw=1.5)
line((tapP0R[0],yVP0bus),tapP0R,c=GREEN,lw=1.5)
text(((XL+XR)/2,yVP0bus+0.25),'$V_{P0}$  (top PMOS mirror, self-biased on LEFT)',
     ha='center',fs=11,color=GREEN)

# ============================================================
# BIAS BUSES — DASHED BLUE
# ============================================================
# VP1: tapVP1_A -> MPN.gate, MTL.gate (all PMOS top-current-source gates)
yVP1bus = 15.4
for tap in (tapVP1_A, tapPN, tapTL):
    dash(tap,(tap[0],yVP1bus))
dash((tapVP1_A[0],yVP1bus),(tapTL[0],yVP1bus))
text(((XA+XB)/2,yVP1bus+0.25),'$V_{P1}$ bus',ha='center',fs=11,color=BLUE)

# VP2: tapVP2_A (col A) -> tapP2L (XL) -> tapP2R (XR), route in bottom-LEFT margin
yVP2bus = -2.6
xleftMrg = -3.3
dash(tapVP2_A,(xleftMrg,tapVP2_A[1]))
dash((xleftMrg,tapVP2_A[1]),(xleftMrg,yVP2bus))
dash((xleftMrg,yVP2bus),(tapP2R[0],yVP2bus))
dash((tapP2R[0],yVP2bus),tapP2R)
dash((tapP2L[0],yVP2bus),tapP2L)
text(((XB+XL)/2,yVP2bus+0.28),'$V_{P2}$ bus',ha='center',fs=11,color=BLUE)

# VN2: tapVN2_B -> tapN2L -> tapN2R, route in bottom-RIGHT margin
yVN2bus = -3.6
xrightMrg = 35.0
dash(tapVN2_B,(xrightMrg,tapVN2_B[1]))
dash((xrightMrg,tapVN2_B[1]),(xrightMrg,yVN2bus))
dash((xrightMrg,yVN2bus),(tapN2L[0],yVN2bus))
dash((tapN2L[0],yVN2bus),tapN2L)
dash((tapN2R[0],yVN2bus),tapN2R)
text(((XL+XR)/2,yVN2bus+0.28),'$V_{N2}$ bus',ha='center',fs=11,color=BLUE)

# VN1: tapVN1_B -> tapN1L -> tapN1R, route in bottom margin even lower
yVN1bus = -4.6
xrightMrg2 = 35.7
dash(tapVN1_B,(xrightMrg2,tapVN1_B[1]))
dash((xrightMrg2,tapVN1_B[1]),(xrightMrg2,yVN1bus))
dash((xrightMrg2,yVN1bus),(tapN1L[0],yVN1bus))
dash((tapN1L[0],yVN1bus),tapN1L)
dash((tapN1R[0],yVN1bus),tapN1R)
text(((XL+XR)/2,yVN1bus+0.28),'$V_{N1}$ bus',ha='center',fs=11,color=BLUE)

# ============================================================
# Vmidn / Vmidp SIGNAL NETS (RED) — from input drains to fold nodes
# ============================================================
# Vmidn: (MINP.drain x, ymid_src_n) -> (XL, yfold_L)
yRedTrack = ymid_src_n - 1.2   # red track between input pair and fold
line((MINP['drain'][0], ymid_src_n),(MINP['drain'][0], yRedTrack),c=RED,lw=1.6,ls='--')
line((MINP['drain'][0], yRedTrack),(XL, yRedTrack),c=RED,lw=1.6,ls='--')
line((XL, yRedTrack),(XL, yfold_L),c=RED,lw=1.6,ls='--')
text(((MINP['drain'][0]+XL)/2, yRedTrack+0.25),'$V_{midn}$  (signal)',
     ha='center',fs=11,color=RED)

# Vmidp: (MINN.drain x, ymid_src_p) -> (XR, yfold_R), use a slightly lower track
yRedTrack2 = ymid_src_p - 2.4
line((MINN['drain'][0], ymid_src_p),(MINN['drain'][0], yRedTrack2),c=RED,lw=1.6,ls='--')
line((MINN['drain'][0], yRedTrack2),(XR, yRedTrack2),c=RED,lw=1.6,ls='--')
line((XR, yRedTrack2),(XR, yfold_R),c=RED,lw=1.6,ls='--')
text(((MINN['drain'][0]+XR)/2, yRedTrack2+0.25),'$V_{midp}$  (signal)',
     ha='center',fs=11,color=RED)

# ============================================================
# Footer notes
# ============================================================
text(((XA+XR)/2,-5.2),
     'Bias: $V_{P1}\\to$ tail $M_{TL}$ + PMOS mirror $M_{PN}$;   '
     '$V_{P2}\\to$ PMOS cascodes $M_{P2,L/R}$;   '
     '$V_{N2}\\to$ NMOS cascodes $M_{N2,L/R}$;   '
     '$V_{N1}\\to$ bottom NMOS $M_{N1,L/R}$.   '
     'Top PMOS pair $M_{P0,L/R}$: $M_{P0,L}$ DIODE-TIED (gate=$V_{P0}$) drives $M_{P0,R}$ '
     '— SE conversion at $V_{OUTP}$.   '
     'Fold nodes $V_{midn}$/$V_{midp}$ = between NMOS-cascode source and bottom-NMOS drain.',
     ha='center',fs=10)

plt.tight_layout()
out='/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
plt.savefig(out,dpi=130,bbox_inches='tight',facecolor='white')
print('OK',out)
