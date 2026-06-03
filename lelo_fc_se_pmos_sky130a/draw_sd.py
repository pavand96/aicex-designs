"""
Folded-cascode SE OTA + wide-swing R-offset bias, drawn with schemdraw.
Top PMOS pair = current mirror (LEFT diode-tied = V_P0 self-bias, drives RIGHT).
Fold nodes V_midn/V_midp = between NMOS-cascode source and bottom-NMOS drain.
"""
import schemdraw
import schemdraw.elements as elm

schemdraw.config(lw=1.6, fontsize=11, font='sans-serif')
d = schemdraw.Drawing(show=False, canvas='matplotlib')

BLUE='#1f4fbf'; RED='#c0392b'; GREEN='#0a8a4a'

# ---- absolute column positions (schemdraw units) ----
XA, XB     =  0.0,   7.0    # bias gens
XTL        = 14.0           # tail + input pair centre
XIP_L      = XTL - 2.6
XIP_R      = XTL + 2.6
XL, XR     = 24.0,  31.5    # fold legs

YVDD       = 16.0
YGND       =  0.0

# ============================================================
# helpers
# ============================================================
def vdd(x):
    d.add(elm.Line().at((x-1.6, YVDD)).to((x+1.6, YVDD)).linewidth(2.6))
    d.add(elm.Label().at((x-1.8, YVDD)).label('$V_{DD}$', loc='left'))

def gnd(x, y_top):
    if y_top > 0.4:
        d.add(elm.Line().at((x, y_top)).to((x, 0.4)))
    d.add(elm.Ground().at((x, 0.4)))

def pmos(x, ysrc):
    """PMOS: .down() => source at top, drain at bottom, gate on LEFT."""
    return d.add(elm.PFet(bulk=False).down().at((x, ysrc)).anchor('source'))

def nmos(x, ysrc):
    """NMOS: .up()  => source at bottom, drain at top, gate on RIGHT."""
    return d.add(elm.NFet(bulk=False).up().at((x, ysrc)).anchor('source'))

def name_right(t, txt):
    yc = (t.source[1] + t.drain[1]) / 2
    d.add(elm.Label().at((t.source[0]+0.9, yc)).label(txt, loc='right', fontsize=11))

def name_left(t, txt):
    yc = (t.source[1] + t.drain[1]) / 2
    d.add(elm.Label().at((t.source[0]-0.9, yc)).label(txt, loc='left', fontsize=11))

def pmos_gate_tap_left(t):
    tap = (t.source[0]-1.3, t.gate[1])
    d.add(elm.Line().at(t.gate).to(tap))
    d.add(elm.Dot().at(tap))
    return tap

def nmos_gate_tap_right(t):
    tap = (t.drain[0]+1.3, t.gate[1])
    d.add(elm.Line().at(t.gate).to(tap))
    d.add(elm.Dot().at(tap))
    return tap

def diode_pmos_left(t, lbl):
    tap = pmos_gate_tap_left(t)
    d.add(elm.Label().at((tap[0]-0.15, tap[1])).label(lbl, loc='left', color=BLUE))
    yj = t.drain[1] - 0.5
    d.add(elm.Line().at(tap).to((tap[0], yj)))
    d.add(elm.Line().at((tap[0], yj)).to((t.drain[0], yj)))
    d.add(elm.Line().at((t.drain[0], yj)).to(t.drain))
    return tap

def diode_nmos_right(t, lbl):
    tap = nmos_gate_tap_right(t)
    d.add(elm.Label().at((tap[0]+0.15, tap[1])).label(lbl, loc='right', color=BLUE))
    yj = t.drain[1] + 0.5
    d.add(elm.Line().at(tap).to((tap[0], yj)))
    d.add(elm.Line().at((tap[0], yj)).to((t.drain[0], yj)))
    d.add(elm.Line().at((t.drain[0], yj)).to(t.drain))
    return tap

def dash(p1, p2, color=BLUE, lw=1.3):
    d.add(elm.Line().at(p1).to(p2).color(color).linestyle('--').linewidth(lw))

def solid_color(p1, p2, color, lw=1.5):
    d.add(elm.Line().at(p1).to(p2).color(color).linewidth(lw))

# ============================================================
# Title
# ============================================================
d.add(elm.Label().at(((XA+XR)/2, 19.0)).label(
    'Folded-cascode SE OTA  |  wide-swing R-offset bias  |  top-PMOS-mirror SE',
    loc='center', fontsize=16))
d.add(elm.Label().at(((XA+XR)/2, 18.3)).label(
    r'sky130A LVT,  $V_{DD}=0.9$\,V,  $I_{REF}=10$\,$\mu$A',
    loc='center', fontsize=10))

# ============================================================
# COL A : PMOS bias gen
# ============================================================
vdd(XA)
MP1 = pmos(XA, 14.5)
d.add(elm.Line().at(MP1.source).to((XA, YVDD)))
name_right(MP1, '$M_{P1}$')
diode_pmos_left(MP1, '$V_{P1}$')

MP2 = pmos(XA, MP1.drain[1])
d.add(elm.Line().at(MP1.drain).to(MP2.source))
name_right(MP2, '$M_{P2}$')
diode_pmos_left(MP2, '$V_{P2}$')

yRt = MP2.drain[1]
yRb = yRt - 2.4
d.add(elm.Resistor().down().at((XA, yRt)).to((XA, yRb)).label('$R_p$', loc='right'))
yIt = yRb - 0.3
yIb = yIt - 1.8
d.add(elm.Line().at((XA, yRb)).to((XA, yIt)))
d.add(elm.SourceI().down().at((XA, yIt)).to((XA, yIb)).label(r'$10\,\mu A$', loc='right'))
gnd(XA, yIb)
d.add(elm.Label().at((XA, -1.5)).label('PMOS bias gen', loc='center', color=BLUE))

# ============================================================
# COL B : NMOS bias gen
# ============================================================
vdd(XB)
MPN = pmos(XB, 14.5)
d.add(elm.Line().at(MPN.source).to((XB, YVDD)))
name_right(MPN, '$M_{PN}$')
tapPN = pmos_gate_tap_left(MPN)

yRnT = MPN.drain[1] - 0.5
d.add(elm.Line().at(MPN.drain).to((XB, yRnT)))
yRnB = yRnT - 2.4
d.add(elm.Resistor().down().at((XB, yRnT)).to((XB, yRnB)).label('$R_n$', loc='right'))

MN2b = nmos(XB, yRnB - 2.0)
d.add(elm.Line().at(MN2b.drain).to((XB, yRnB)))
name_left(MN2b, '$M_{N2b}$')
diode_nmos_right(MN2b, '$V_{N2}$')

MN1b = nmos(XB, MN2b.source[1] - 2.0)
d.add(elm.Line().at(MN1b.drain).to(MN2b.source))
name_left(MN1b, '$M_{N1b}$')
diode_nmos_right(MN1b, '$V_{N1}$')

gnd(XB, MN1b.source[1])
d.add(elm.Label().at((XB, -1.5)).label('NMOS bias gen', loc='center', color=BLUE))

# tap coords for buses
tapVP1_A = (MP1.source[0]-1.3, MP1.gate[1])
tapVP2_A = (MP2.source[0]-1.3, MP2.gate[1])
tapVN2_B = (MN2b.drain[0]+1.3, MN2b.gate[1])
tapVN1_B = (MN1b.drain[0]+1.3, MN1b.gate[1])

# ============================================================
# INPUT STAGE: tail + input pair
# ============================================================
vdd(XTL)
MTL = pmos(XTL, 14.5)
d.add(elm.Line().at(MTL.source).to((XTL, YVDD)))
name_right(MTL, '$M_{TL}$')
tapTL = pmos_gate_tap_left(MTL)

yTail = MTL.drain[1] - 0.7
d.add(elm.Line().at(MTL.drain).to((XTL, yTail)))
d.add(elm.Dot().at((XTL, yTail)))
d.add(elm.Label().at((XTL+0.3, yTail+0.25)).label('$V_{tail}$', loc='right', fontsize=10))
d.add(elm.Line().at((XIP_L, yTail)).to((XIP_R, yTail)))

MINP = pmos(XIP_L, yTail)
d.add(elm.Line().at(MINP.source).to((XIP_L, yTail)))
name_right(MINP, '$M_{INP}$')
tapINP = (MINP.gate[0]-1.3, MINP.gate[1])
d.add(elm.Line().at(MINP.gate).to(tapINP))
d.add(elm.Dot().at(tapINP))
d.add(elm.Label().at((tapINP[0]-0.15, tapINP[1])).label('$V_{inp}$', loc='left'))

# MINN: mirror — put gate on RIGHT (use anchor='source' with default left-gate, then mirror by reusing PFet with .flip())
MINN = d.add(elm.PFet(bulk=False).down().at((XIP_R, yTail)).anchor('source').reverse())
d.add(elm.Line().at(MINN.source).to((XIP_R, yTail)))
name_left(MINN, '$M_{INN}$')
tapINN = (MINN.gate[0]+1.3, MINN.gate[1])
d.add(elm.Line().at(MINN.gate).to(tapINN))
d.add(elm.Dot().at(tapINN))
d.add(elm.Label().at((tapINN[0]+0.15, tapINN[1])).label('$V_{inn}$', loc='right'))

d.add(elm.Label().at((XTL, -1.5)).label('Tail + PMOS input pair', loc='center', color=BLUE))

# Input pair drain tap nodes (sources for red Vmidn/Vmidp nets)
nodeVmidn_src = (MINP.drain[0], MINP.drain[1]-0.6)
d.add(elm.Line().at(MINP.drain).to(nodeVmidn_src))
d.add(elm.Dot().at(nodeVmidn_src))
d.add(elm.Label().at((nodeVmidn_src[0]-0.2, nodeVmidn_src[1]-0.3))
      .label('$V_{midn}$', loc='left', color=RED, fontsize=10))

nodeVmidp_src = (MINN.drain[0], MINN.drain[1]-0.6)
d.add(elm.Line().at(MINN.drain).to(nodeVmidp_src))
d.add(elm.Dot().at(nodeVmidp_src))
d.add(elm.Label().at((nodeVmidp_src[0]+0.2, nodeVmidp_src[1]-0.3))
      .label('$V_{midp}$', loc='right', color=RED, fontsize=10))

# ============================================================
# LEFT FOLD LEG (XL) — top PMOS DIODE-TIED (V_P0 self-bias)
# ============================================================
vdd(XL)
MP0L = pmos(XL, 14.5)
d.add(elm.Line().at(MP0L.source).to((XL, YVDD)))
name_right(MP0L, '$M_{P0,L}$')

MP2L = pmos(XL, MP0L.drain[1])
d.add(elm.Line().at(MP0L.drain).to(MP2L.source))
name_right(MP2L, '$M_{P2,L}$')
tapP2L = pmos_gate_tap_left(MP2L)

yVoutn = MP2L.drain[1] - 0.9
d.add(elm.Line().at(MP2L.drain).to((XL, yVoutn)))
d.add(elm.Dot().at((XL, yVoutn)))
d.add(elm.Label().at((XL-0.4, yVoutn+0.25))
      .label('$V_{outn}$ (mirror ref)', loc='left', fontsize=10))

# Self-bias of MP0L: gate -> down LEFT side -> across to V_outn (green)
tapP0L = pmos_gate_tap_left(MP0L)
d.add(elm.Label().at((tapP0L[0]-0.15, tapP0L[1])).label('$V_{P0}$', loc='left', color=GREEN))
xleft_loop = XL - 2.4
solid_color(tapP0L, (xleft_loop, tapP0L[1]), GREEN)
solid_color((xleft_loop, tapP0L[1]), (xleft_loop, yVoutn), GREEN)
solid_color((xleft_loop, yVoutn), (XL, yVoutn), GREEN)

MN2L = nmos(XL, yVoutn - 2.6)
d.add(elm.Line().at(MN2L.drain).to((XL, yVoutn)))
name_left(MN2L, '$M_{N2,L}$')
tapN2L = nmos_gate_tap_right(MN2L)

yFoldL = MN2L.source[1] - 0.6
d.add(elm.Line().at(MN2L.source).to((XL, yFoldL)))
d.add(elm.Dot().at((XL, yFoldL)))
d.add(elm.Label().at((XL-0.4, yFoldL+0.25))
      .label('$V_{midn}$ fold', loc='left', color=RED, fontsize=10))

MN1L = nmos(XL, yFoldL - 2.0)
d.add(elm.Line().at(MN1L.drain).to((XL, yFoldL)))
name_left(MN1L, '$M_{N1,L}$')
tapN1L = nmos_gate_tap_right(MN1L)

gnd(XL, MN1L.source[1])
d.add(elm.Label().at((XL, -1.5)).label('LEFT fold leg\n(mirror REF)', loc='center', color=BLUE, fontsize=10))

# ============================================================
# RIGHT FOLD LEG (XR) — VOUT side
# ============================================================
vdd(XR)
MP0R = pmos(XR, 14.5)
d.add(elm.Line().at(MP0R.source).to((XR, YVDD)))
name_right(MP0R, '$M_{P0,R}$')
tapP0R = pmos_gate_tap_left(MP0R)

MP2R = pmos(XR, MP0R.drain[1])
d.add(elm.Line().at(MP0R.drain).to(MP2R.source))
name_right(MP2R, '$M_{P2,R}$')
tapP2R = pmos_gate_tap_left(MP2R)

yVoutp = MP2R.drain[1] - 0.9
d.add(elm.Line().at(MP2R.drain).to((XR, yVoutp)))
d.add(elm.Dot(radius=0.18).at((XR, yVoutp)))
d.add(elm.Label().at((XR+0.5, yVoutp)).label('$V_{OUTP}$', loc='right', fontsize=13))

MN2R = nmos(XR, yVoutp - 2.6)
d.add(elm.Line().at(MN2R.drain).to((XR, yVoutp)))
name_left(MN2R, '$M_{N2,R}$')
tapN2R = nmos_gate_tap_right(MN2R)

yFoldR = MN2R.source[1] - 0.6
d.add(elm.Line().at(MN2R.source).to((XR, yFoldR)))
d.add(elm.Dot().at((XR, yFoldR)))
d.add(elm.Label().at((XR+0.4, yFoldR+0.25))
      .label('$V_{midp}$ fold', loc='right', color=RED, fontsize=10))

MN1R = nmos(XR, yFoldR - 2.0)
d.add(elm.Line().at(MN1R.drain).to((XR, yFoldR)))
name_left(MN1R, '$M_{N1,R}$')
tapN1R = nmos_gate_tap_right(MN1R)

gnd(XR, MN1R.source[1])
d.add(elm.Label().at((XR, -1.5)).label('RIGHT fold leg\n(VOUT)', loc='center', color=BLUE, fontsize=10))

# ============================================================
# V_P0 wire (green): tapP0L -> tapP0R, routed above the top PMOS row
# ============================================================
yVP0bus = 15.4
solid_color(tapP0L, (tapP0L[0], yVP0bus), GREEN)
solid_color((tapP0L[0], yVP0bus), (tapP0R[0], yVP0bus), GREEN)
solid_color((tapP0R[0], yVP0bus), tapP0R, GREEN)
d.add(elm.Label().at(((XL+XR)/2, yVP0bus+0.3))
      .label('$V_{P0}$ (top PMOS mirror, self-bias on LEFT)',
             loc='center', color=GREEN, fontsize=10))

# ============================================================
# BIAS BUSES (dashed blue)
# ============================================================
# VP1 bus: tapVP1_A -> tapPN -> tapTL  (top row)
yVP1bus = 15.0
for tap in (tapVP1_A, tapPN, tapTL):
    dash(tap, (tap[0], yVP1bus))
dash((tapVP1_A[0], yVP1bus), (tapTL[0], yVP1bus))
d.add(elm.Label().at(((XA+XB)/2, yVP1bus+0.3))
      .label('$V_{P1}$ bus', loc='center', color=BLUE, fontsize=10))

# VP2 bus: tapVP2_A -> tapP2L -> tapP2R (route in LEFT margin, then across bottom-left, up to fold legs)
yVP2bus = -2.6
xLeftMrg = -3.0
dash(tapVP2_A, (xLeftMrg, tapVP2_A[1]))
dash((xLeftMrg, tapVP2_A[1]), (xLeftMrg, yVP2bus))
dash((xLeftMrg, yVP2bus), (tapP2R[0], yVP2bus))
dash((tapP2R[0], yVP2bus), tapP2R)
dash((tapP2L[0], yVP2bus), tapP2L)
d.add(elm.Label().at(((XB+XL)/2, yVP2bus+0.3))
      .label('$V_{P2}$ bus', loc='center', color=BLUE, fontsize=10))

# VN2 bus: tapVN2_B -> tapN2L -> tapN2R (route in RIGHT margin)
yVN2bus = -3.7
xRightMrg = XR + 3.5
dash(tapVN2_B, (xRightMrg, tapVN2_B[1]))
dash((xRightMrg, tapVN2_B[1]), (xRightMrg, yVN2bus))
dash((xRightMrg, yVN2bus), (tapN2L[0], yVN2bus))
dash((tapN2L[0], yVN2bus), tapN2L)
dash((tapN2R[0], yVN2bus), tapN2R)
d.add(elm.Label().at(((XL+XR)/2, yVN2bus+0.3))
      .label('$V_{N2}$ bus', loc='center', color=BLUE, fontsize=10))

# VN1 bus
yVN1bus = -4.8
xRightMrg2 = XR + 4.2
dash(tapVN1_B, (xRightMrg2, tapVN1_B[1]))
dash((xRightMrg2, tapVN1_B[1]), (xRightMrg2, yVN1bus))
dash((xRightMrg2, yVN1bus), (tapN1L[0], yVN1bus))
dash((tapN1L[0], yVN1bus), tapN1L)
dash((tapN1R[0], yVN1bus), tapN1R)
d.add(elm.Label().at(((XL+XR)/2, yVN1bus+0.3))
      .label('$V_{N1}$ bus', loc='center', color=BLUE, fontsize=10))

# ============================================================
# Vmidn / Vmidp signal nets (RED, dashed) input drains -> fold nodes
# ============================================================
yRed1 = nodeVmidn_src[1] - 1.6
d.add(elm.Line().at(nodeVmidn_src).to((nodeVmidn_src[0], yRed1)).color(RED).linestyle('--').linewidth(1.5))
d.add(elm.Line().at((nodeVmidn_src[0], yRed1)).to((XL, yRed1)).color(RED).linestyle('--').linewidth(1.5))
d.add(elm.Line().at((XL, yRed1)).to((XL, yFoldL)).color(RED).linestyle('--').linewidth(1.5))
d.add(elm.Label().at(((nodeVmidn_src[0]+XL)/2, yRed1+0.3))
      .label('$V_{midn}$ signal', loc='center', color=RED, fontsize=10))

yRed2 = nodeVmidp_src[1] - 3.0
d.add(elm.Line().at(nodeVmidp_src).to((nodeVmidp_src[0], yRed2)).color(RED).linestyle('--').linewidth(1.5))
d.add(elm.Line().at((nodeVmidp_src[0], yRed2)).to((XR, yRed2)).color(RED).linestyle('--').linewidth(1.5))
d.add(elm.Line().at((XR, yRed2)).to((XR, yFoldR)).color(RED).linestyle('--').linewidth(1.5))
d.add(elm.Label().at(((nodeVmidp_src[0]+XR)/2, yRed2+0.3))
      .label('$V_{midp}$ signal', loc='center', color=RED, fontsize=10))

# ============================================================
# Footer
# ============================================================
d.add(elm.Label().at(((XA+XR)/2, -5.6)).label(
    r'$V_{P1}\to M_{TL},M_{PN}$;  $V_{P2}\to M_{P2,L/R}$;  '
    r'$V_{N2}\to M_{N2,L/R}$;  $V_{N1}\to M_{N1,L/R}$.  '
    r'$M_{P0,L}$ diode-tied $\Rightarrow V_{P0}$ drives $M_{P0,R}$ (top mirror = SE conv).  '
    r'Fold nodes $V_{midn}/V_{midp}$ between NMOS cascode source and bottom NMOS drain.',
    loc='center', fontsize=9))

out = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
d.save(out, dpi=140)
print('OK', out)
