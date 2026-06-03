"""
Folded-cascode SE OTA + wide-swing R-offset bias.
4-column topology matching user's hand drawing.
"""
import schemdraw
import schemdraw.elements as elm

schemdraw.config(lw=1.7, fontsize=12, font='sans-serif')

d = schemdraw.Drawing(show=False, canvas='matplotlib')

XA, XB, XC, XD = 0.0, 7.0, 14.0, 21.0
YVDD = 14.0

DASH_BLUE = '#1f4fbf'
SIG_RED   = '#c0392b'

def vdd_stub(x):
    d.add(elm.Line().at((x-1.8, YVDD)).to((x+1.8, YVDD)).linewidth(2.6))
    d.add(elm.Label().at((x-2.0, YVDD)).label('$V_{DD}$', loc='left'))

def gnd_at(x, y_top):
    if y_top > 0.5:
        d.add(elm.Line().at((x, y_top)).to((x, 0.5)))
    d.add(elm.Ground().at((x, 0.5)))

def pmos(x, ysrc):
    return d.add(elm.PFet(bulk=False).down().at((x, ysrc)).anchor('source'))

def nmos(x, ysrc):
    return d.add(elm.NFet(bulk=False).up().at((x, ysrc)).anchor('source'))

def diode_tie_pmos_left(t, glbl):
    tap = (t.source[0] - 1.4, t.gate[1])
    d.add(elm.Line().at(t.gate).to(tap))
    d.add(elm.Dot().at(tap))
    d.add(elm.Label().at((tap[0]-0.2, tap[1])).label(glbl, loc='left'))
    yj = t.drain[1] - 0.5
    d.add(elm.Line().at(tap).to((tap[0], yj)))
    d.add(elm.Line().at((tap[0], yj)).to((t.drain[0], yj)))
    d.add(elm.Line().at((t.drain[0], yj)).to(t.drain))

def diode_tie_nmos_right(t, glbl):
    tap = (t.drain[0] + 1.4, t.gate[1])
    d.add(elm.Line().at(t.gate).to(tap))
    d.add(elm.Dot().at(tap))
    d.add(elm.Label().at((tap[0]+0.2, tap[1])).label(glbl, loc='right'))
    yj = t.drain[1] + 0.5
    d.add(elm.Line().at(tap).to((tap[0], yj)))
    d.add(elm.Line().at((tap[0], yj)).to((t.drain[0], yj)))
    d.add(elm.Line().at((t.drain[0], yj)).to(t.drain))

def gate_tap_pmos_left(t):
    tap = (t.source[0] - 1.4, t.gate[1])
    d.add(elm.Line().at(t.gate).to(tap))
    d.add(elm.Dot().at(tap))
    return tap

def gate_tap_nmos_right(t):
    tap = (t.drain[0] + 1.4, t.gate[1])
    d.add(elm.Line().at(t.gate).to(tap))
    d.add(elm.Dot().at(tap))
    return tap

def dash(p1, p2, color=DASH_BLUE):
    d.add(elm.Line().at(p1).to(p2).color(color).linestyle('--').linewidth(1.2))

def fet_label(t, txt, side='right'):
    yc = (t.source[1]+t.drain[1])/2
    if side == 'right':
        d.add(elm.Label().at((t.source[0]+0.65, yc)).label(txt, loc='right', fontsize=12))
    else:
        d.add(elm.Label().at((t.source[0]-0.65, yc)).label(txt, loc='left', fontsize=12))

# ---- title ----
d.add(elm.Label().at(((XA+XD)/2, 16.0))
      .label('Folded-cascode SE OTA   |   wide-swing R-offset bias',
             loc='center', fontsize=17))
d.add(elm.Label().at(((XA+XD)/2, 15.3))
      .label('sky130A LVT,  $V_{DD}=0.9$\u2009V,  $I_{REF}=10$\u2009\u03BCA',
             loc='center', fontsize=11))

# ---- COL A : PMOS bias gen ----
vdd_stub(XA)
MP1 = pmos(XA, 12.5)
d.add(elm.Line().at(MP1.source).to((XA, YVDD)))
diode_tie_pmos_left(MP1, '$V_{P1}$')
fet_label(MP1, '$M_{P1}$', 'right')

MP2 = pmos(XA, MP1.drain[1])
d.add(elm.Line().at(MP1.drain).to(MP2.source))
diode_tie_pmos_left(MP2, '$V_{P2}$')
fet_label(MP2, '$M_{P2}$', 'right')

yRt = MP2.drain[1]
yRb = yRt - 2.0
d.add(elm.Resistor().down().at((XA, yRt)).to((XA, yRb)).label('$R_p$', loc='right'))
yIt = yRb - 0.3
yIb = yIt - 2.0
d.add(elm.Line().at((XA, yRb)).to((XA, yIt)))
d.add(elm.SourceI().down().at((XA, yIt)).to((XA, yIb)).label('$10\\,\\mu A$', loc='right'))
gnd_at(XA, yIb)
d.add(elm.Label().at((XA, -1.2))
      .label('PMOS bias gen', loc='center', fontsize=12, color=DASH_BLUE))

# ---- COL B : NMOS bias gen ----
vdd_stub(XB)
MPN = pmos(XB, 12.5)
d.add(elm.Line().at(MPN.source).to((XB, YVDD)))
tapMPN = gate_tap_pmos_left(MPN)
fet_label(MPN, '$M_{PN}$', 'right')

yRnT = MPN.drain[1] - 0.3
d.add(elm.Line().at(MPN.drain).to((XB, yRnT)))
yRnB = yRnT - 2.0
d.add(elm.Resistor().down().at((XB, yRnT)).to((XB, yRnB)).label('$R_n$', loc='right'))

MN2 = nmos(XB, yRnB - 2.0)
d.add(elm.Line().at(MN2.drain).to((XB, yRnB)))
diode_tie_nmos_right(MN2, '$V_{N2}$')
fet_label(MN2, '$M_{N2}$', 'left')

MN1 = nmos(XB, MN2.source[1] - 2.0)
d.add(elm.Line().at(MN1.drain).to(MN2.source))
diode_tie_nmos_right(MN1, '$V_{N1}$')
fet_label(MN1, '$M_{N1}$', 'left')

gnd_at(XB, MN1.source[1])
d.add(elm.Label().at((XB, -1.2))
      .label('NMOS bias gen', loc='center', fontsize=12, color=DASH_BLUE))

# ---- COL C : Tail + input pair ----
vdd_stub(XC)
MTL = pmos(XC, 12.5)
d.add(elm.Line().at(MTL.source).to((XC, YVDD)))
tapMTL = gate_tap_pmos_left(MTL)
fet_label(MTL, '$M_{TL}$', 'right')

yTail = MTL.drain[1] - 0.6
d.add(elm.Line().at(MTL.drain).to((XC, yTail)))
d.add(elm.Dot().at((XC, yTail)))
d.add(elm.Label().at((XC+0.3, yTail+0.3)).label('$V_{tail}$', loc='right'))

xL, xR = XC - 3.0, XC + 3.0
d.add(elm.Line().at((xL, yTail)).to((xR, yTail)))
MIP = pmos(xL, yTail)
fet_label(MIP, '$M_{INP}$', 'right')
d.add(elm.Line().at(MIP.gate).to((MIP.gate[0]-1.4, MIP.gate[1])))
d.add(elm.Dot().at((MIP.gate[0]-1.4, MIP.gate[1])))
d.add(elm.Label().at((MIP.gate[0]-1.6, MIP.gate[1])).label('$V_{inp}$', loc='left'))

MIN = pmos(xR, yTail)
fet_label(MIN, '$M_{INN}$', 'right')
d.add(elm.Line().at(MIN.gate).to((MIN.gate[0]-1.4, MIN.gate[1])))
d.add(elm.Dot().at((MIN.gate[0]-1.4, MIN.gate[1])))
d.add(elm.Label().at((MIN.gate[0]-1.6, MIN.gate[1])).label('$V_{inn}$', loc='left'))

yMid = MIP.drain[1] - 1.4
d.add(elm.Line().at(MIP.drain).to((xL, yMid)))
d.add(elm.Dot().at((xL, yMid)))
d.add(elm.Label().at((xL, yMid-0.45)).label('$V_{midn}$', loc='center', fontsize=11))
d.add(elm.Line().at(MIN.drain).to((xR, yMid)))
d.add(elm.Dot().at((xR, yMid)))
d.add(elm.Label().at((xR, yMid-0.45)).label('$V_{midp}$', loc='center', fontsize=11))
d.add(elm.Label().at((XC, -1.2))
      .label('Tail + PMOS input pair', loc='center', fontsize=12, color=DASH_BLUE))

# ---- COL D : SE output cascode ----
vdd_stub(XD)
MP0 = pmos(XD, 12.5)
d.add(elm.Line().at(MP0.source).to((XD, YVDD)))
tapMP0 = gate_tap_pmos_left(MP0)
fet_label(MP0, '$M_{P0}$', 'right')

MP2o = pmos(XD, MP0.drain[1])
d.add(elm.Line().at(MP0.drain).to(MP2o.source))
tapMP2o = gate_tap_pmos_left(MP2o)
fet_label(MP2o, '$M_{P2,o}$', 'right')

yOut = MP2o.drain[1] - 1.0
d.add(elm.Line().at(MP2o.drain).to((XD, yOut)))
d.add(elm.Dot(radius=0.18).at((XD, yOut)))
d.add(elm.Label().at((XD+0.6, yOut+0.1)).label('$V_{OUTP}$', loc='right', fontsize=13))

MN2o = nmos(XD, yOut - 2.0)
d.add(elm.Line().at(MN2o.drain).to((XD, yOut)))
tapMN2o = gate_tap_nmos_right(MN2o)
fet_label(MN2o, '$M_{N2,o}$', 'left')

MN1o = nmos(XD, MN2o.source[1] - 2.0)
d.add(elm.Line().at(MN1o.drain).to(MN2o.source))
tapMN1o = gate_tap_nmos_right(MN1o)
fet_label(MN1o, '$M_{N1,o}$', 'left')

gnd_at(XD, MN1o.source[1])
d.add(elm.Label().at((XD, -1.2))
      .label('SE output cascode', loc='center', fontsize=12, color=DASH_BLUE))

# ---- BIAS BUSES ----
yVP1 = 13.4
for t in (MP1, MPN, MTL, MP0):
    gx = t.source[0] - 1.4
    dash((gx, t.gate[1]), (gx, yVP1))
dash((MP1.source[0]-1.4, yVP1), (MP0.source[0]-1.4, yVP1))
d.add(elm.Label().at(((XA+XB)/2, yVP1+0.3))
      .label('$V_{P1}$ bus', loc='center', fontsize=11, color=DASH_BLUE))

yVP2 = MP2.drain[1] - 0.7
xL_bus = XA - 2.4
xR_bus = XD - 2.4
gP2A = (MP2.source[0]-1.4, MP2.gate[1])
gP2D = (MP2o.source[0]-1.4, MP2o.gate[1])
dash(gP2A, (xL_bus, gP2A[1]))
dash((xL_bus, gP2A[1]), (xL_bus, yVP2))
dash((xL_bus, yVP2), (xR_bus, yVP2))
dash((xR_bus, yVP2), (xR_bus, gP2D[1]))
dash((xR_bus, gP2D[1]), gP2D)
d.add(elm.Label().at(((XB+XC)/2, yVP2+0.3))
      .label('$V_{P2}$ bus', loc='center', fontsize=11, color=DASH_BLUE))

yVN2 = MN2.drain[1] - 0.7
xRb_bus = XB + 2.4
xR_endD = XD + 2.4
gN2B = (MN2.drain[0]+1.4, MN2.gate[1])
gN2D = (MN2o.drain[0]+1.4, MN2o.gate[1])
dash(gN2B, (xRb_bus, gN2B[1]))
dash((xRb_bus, gN2B[1]), (xRb_bus, yVN2))
dash((xRb_bus, yVN2), (xR_endD, yVN2))
dash((xR_endD, yVN2), (xR_endD, gN2D[1]))
dash((xR_endD, gN2D[1]), gN2D)
d.add(elm.Label().at(((XB+XC)/2, yVN2+0.3))
      .label('$V_{N2}$ bus', loc='center', fontsize=11, color=DASH_BLUE))

# VN1 tap label (col B only — col D bottom NMOS is signal-driven, not VN1)
gN1B = (MN1.drain[0]+1.4, MN1.gate[1])
d.add(elm.Label().at((gN1B[0]+0.2, gN1B[1])).label('$V_{N1}$', loc='right', color=DASH_BLUE))

# Vmidn signal (red) col C -> col D MN1o gate
yVm = yMid - 1.5
d.add(elm.Line().at((xL, yMid)).to((xL, yVm)).color(SIG_RED).linestyle('--').linewidth(1.4))
d.add(elm.Line().at((xL, yVm)).to((XD+3.0, yVm)).color(SIG_RED).linestyle('--').linewidth(1.4))
d.add(elm.Line().at((XD+3.0, yVm)).to((XD+3.0, tapMN1o[1])).color(SIG_RED).linestyle('--').linewidth(1.4))
d.add(elm.Line().at((XD+3.0, tapMN1o[1])).to(tapMN1o).color(SIG_RED).linestyle('--').linewidth(1.4))
d.add(elm.Label().at(((XC+XD)/2, yVm+0.3))
      .label('$V_{midn}$ (signal)', loc='center', fontsize=11, color=SIG_RED))

# ---- Footer ----
d.add(elm.Label().at(((XA+XD)/2, -2.5)).label(
    'Buses (blue dashed):  $V_{P1}$ sets top PMOS;  $V_{P2}$ cascodes top PMOS;  '
    '$V_{N2}$ cascodes bottom NMOS;  $V_{N1}$ sets bottom NMOS.',
    loc='center', fontsize=10))
d.add(elm.Label().at(((XA+XD)/2, -3.1)).label(
    'R-offset trick:  $R_p$ drops $V_{ov}$ so cascode $V_{DS}=V_{ov}$  '
    '(maximises output swing at $V_{DD}=0.9$\u2009V).',
    loc='center', fontsize=10))

out = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_clean.png'
d.save(out, dpi=140)
print('OK', out)
