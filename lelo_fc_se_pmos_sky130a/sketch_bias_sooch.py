"""
Sooch low-voltage cascoded bias  --  analog-textbook convention.

Mirror gates are tied directly at gate height -- no separate top "bias buses".
Devices are labelled with short names (M1..M9) right at the device; a sizing
table at the bottom gives the W/L and multiplicity for each.
"""
import matplotlib
matplotlib.rcParams['savefig.facecolor'] = 'white'
import schemdraw
import schemdraw.elements as elm
schemdraw.config(bgcolor='white', color='black', fontsize=11, lw=1.2)

# ---- vertical positions ----
Y_VDD     = 17.0
Y_PTOP_S  = 14.5
Y_PTOP_D  = 13.0
Y_PTOP_G  = 13.75
Y_PCAS_S  = 11.5     # 1.5 unit gap so mid-node label is visible
Y_PCAS_D  = 10.0
Y_PCAS_G  = 10.75
Y_NMOS_D  = 8.5
Y_NMOS_S  = 7.0
Y_NMOS_G  = 7.75
Y_VSS     = 5.0

# ---- column x positions (well spaced so device labels do not collide) ----
X1 = 4.0     # VBP master  (col 1)
X2 = 11.0    # VBIAS3 cascoded (col 2)
X3 = 18.0    # VBIAS2 cascoded (col 3)
X4 = 26.0    # VBIAS1 generator (col 4)

XL = -1.0
XR = 32.0

GATE_DX = 1.3666666666


def lab(d, pos, text, fontsize=9, halign='center'):
    d += elm.Label().at(pos).label(text, fontsize=fontsize, halign=halign)


def vwire(d, x, y1, y2): d += elm.Line().endpoints((x, y1), (x, y2))
def hwire(d, x1, x2, y): d += elm.Line().endpoints((x1, y), (x2, y))


def diode_short(d, dev, side='L'):
    """Short the device's gate to its drain via a small L on `side`."""
    gx, gy = dev.gate; dx, dy = dev.drain
    if side == 'L':
        jx = min(gx, dx) - 0.6
    else:
        jx = max(gx, dx) + 0.6
    d += elm.Line().endpoints((gx, gy), (jx, gy))
    d += elm.Line().endpoints((jx, gy), (jx, dy))
    d += elm.Line().endpoints((jx, dy), (dx, dy))
    d += elm.Dot().at((dx, dy))


with schemdraw.Drawing(show=False) as d:
    # rails
    hwire(d, XL, XR, Y_VDD)
    hwire(d, XL, XR, Y_VSS)
    lab(d, (XL - 0.3, Y_VDD + 0.4), 'VDD = 0.9 V', fontsize=12, halign='right')
    lab(d, (XL - 0.3, Y_VSS - 0.6), 'VSS',         fontsize=12, halign='right')

    # ==================== COL 1: VBP master ====================
    x = X1
    vwire(d, x, Y_VDD, Y_PTOP_S); d += elm.Dot().at((x, Y_VDD))
    P1 = elm.PFet().anchor('source').at((x, Y_PTOP_S)); d += P1
    diode_short(d, P1, side='R')
    # drain wire continues down to IBIAS pin (sink at right)
    vwire(d, x, Y_PTOP_D, Y_NMOS_D)
    d += elm.Dot(open=True).at((x, Y_NMOS_D))
    lab(d, (x - 0.3, Y_NMOS_D - 0.5),
        'IBIAS pin\n(10 uA to VSS)', fontsize=9, halign='right')
    # device name BELOW the source, above the gate-wire row would clash,
    # so put it just to the right of the source at the top
    lab(d, (x - 1.0, (Y_PTOP_S + Y_PTOP_D)/2), 'M1', fontsize=10, halign='right')
    lab(d, (x, Y_VSS - 1.3), 'Col 1: VBP master', fontsize=9)

    # ==================== COL 2: VBIAS3 cascoded ====================
    x = X2
    vwire(d, x, Y_VDD, Y_PTOP_S); d += elm.Dot().at((x, Y_VDD))
    P2T = elm.PFet().anchor('source').at((x, Y_PTOP_S)); d += P2T
    # mid-node nVB3i
    vwire(d, x, Y_PTOP_D, Y_PCAS_S)
    mid_y2 = (Y_PTOP_D + Y_PCAS_S) / 2
    d += elm.Dot().at((x, mid_y2))
    lab(d, (x - 0.3, mid_y2), 'nVB3i', fontsize=8, halign='right')
    P2C = elm.PFet().anchor('source').at((x, Y_PCAS_S)); d += P2C
    vwire(d, x, Y_PCAS_D, Y_NMOS_D)
    N2 = elm.NFet().anchor('drain').at((x, Y_NMOS_D)); d += N2
    diode_short(d, N2, side='R')
    vwire(d, x, Y_NMOS_S, Y_VSS); d += elm.Dot().at((x, Y_VSS))
    # node label at NMOS drain
    lab(d, (x - 0.3, N2.drain[1] + 0.4), 'VBIAS3', fontsize=11, halign='right')
    # device names: just to the right of the source/drain of each device,
    # carefully avoiding the gate-mirror wires
    lab(d, (x - 1.0, (Y_PTOP_S + Y_PTOP_D)/2), 'M2', fontsize=10, halign='right')
    lab(d, (x - 1.0, (Y_PCAS_S + Y_PCAS_D)/2), 'M3', fontsize=10, halign='right')
    lab(d, (x - 1.0, (Y_NMOS_D + Y_NMOS_S)/2), 'M4', fontsize=10, halign='right')
    lab(d, (x, Y_VSS - 1.3), 'Col 2: VBIAS3 cascoded', fontsize=9)

    # ==================== COL 3: VBIAS2 cascoded ====================
    x = X3
    vwire(d, x, Y_VDD, Y_PTOP_S); d += elm.Dot().at((x, Y_VDD))
    P3T = elm.PFet().anchor('source').at((x, Y_PTOP_S)); d += P3T
    vwire(d, x, Y_PTOP_D, Y_PCAS_S)
    mid_y3 = (Y_PTOP_D + Y_PCAS_S) / 2
    d += elm.Dot().at((x, mid_y3))
    lab(d, (x - 0.3, mid_y3), 'nVB2i', fontsize=8, halign='right')
    P3C = elm.PFet().anchor('source').at((x, Y_PCAS_S)); d += P3C
    vwire(d, x, Y_PCAS_D, Y_NMOS_D)
    N3 = elm.NFet().anchor('drain').at((x, Y_NMOS_D)); d += N3
    diode_short(d, N3, side='R')
    vwire(d, x, Y_NMOS_S, Y_VSS); d += elm.Dot().at((x, Y_VSS))
    lab(d, (x - 0.3, N3.drain[1] + 0.4), 'VBIAS2', fontsize=11, halign='right')
    # VBIAS2 -> signal path port arrow on the right
    PORT_X = x + 3.0
    hwire(d, x, PORT_X, N3.drain[1])
    d += elm.Dot(open=True).at((PORT_X, N3.drain[1]))
    lab(d, (PORT_X + 0.2, N3.drain[1] - 0.4),
        'to signal-path\nfolded-cascode bias',
        fontsize=8, halign='left')
    lab(d, (x - 1.0, (Y_PTOP_S + Y_PTOP_D)/2), 'M5', fontsize=10, halign='right')
    lab(d, (x - 1.0, (Y_PCAS_S + Y_PCAS_D)/2), 'M6', fontsize=10, halign='right')
    lab(d, (x - 1.0, (Y_NMOS_D + Y_NMOS_S)/2), 'M7', fontsize=10, halign='right')
    lab(d, (x, Y_VSS - 1.3), 'Col 3: VBIAS2 cascoded', fontsize=9)

    # ==================== COL 4: VBIAS1 generator ====================
    x = X4
    vwire(d, x, Y_VDD, Y_PTOP_S); d += elm.Dot().at((x, Y_VDD))
    # default-orientation pfet (gate on right), diode-tied on RIGHT
    # so the VBIAS1 gate node sits on the right and the mirror wire
    # runs LEFT from there to cols 2 / 3 cascode gates.
    P4 = elm.PFet().anchor('source').at((x, Y_PTOP_S)); d += P4
    diode_short(d, P4, side='R')
    # drain wire straight down to NMOS drain
    vwire(d, x, Y_PTOP_D, Y_NMOS_D)
    N4 = elm.NFet().anchor('drain').at((x, Y_NMOS_D)); d += N4
    vwire(d, x, Y_NMOS_S, Y_VSS); d += elm.Dot().at((x, Y_VSS))
    lab(d, (P4.gate[0] + 0.7, P4.gate[1] + 0.4),
        'VBIAS1', fontsize=11, halign='left')
    lab(d, (x + 1.8, (Y_PTOP_S + Y_PTOP_D)/2), 'M8', fontsize=10, halign='left')
    lab(d, (x + 1.8, (Y_NMOS_D + Y_NMOS_S)/2), 'M9', fontsize=10, halign='left')
    lab(d, (x, Y_VSS - 1.3),
        'Col 4: VBIAS1 gen (uncascoded)', fontsize=9)

    # ==================== mirror gate wires ====================
    # VBP wire spans P1.gate -> P2T.gate -> P3T.gate at y = Y_PTOP_G
    hwire(d, P1.gate[0], P3T.gate[0], Y_PTOP_G)
    for px in (P1.gate[0], P2T.gate[0], P3T.gate[0]):
        d += elm.Dot().at((px, Y_PTOP_G))
    # VBP label sits ABOVE the wire in the gap between cols 1 and 2
    lab(d, ((P1.gate[0] + P2T.gate[0])/2, Y_PTOP_G + 0.35),
        'VBP', fontsize=11)

    # VBIAS1 wire spans P2C.gate -> P3C.gate -> P4.gate at y = Y_PCAS_G
    hwire(d, P2C.gate[0], P4.gate[0], Y_PCAS_G)
    for px in (P2C.gate[0], P3C.gate[0], P4.gate[0]):
        d += elm.Dot().at((px, Y_PCAS_G))
    lab(d, ((P3C.gate[0] + P4.gate[0])/2, Y_PCAS_G + 0.35),
        'VBIAS1', fontsize=11)

    # VBIAS3 wire: route BELOW the NMOS devices (between source row and VSS)
    # so it doesn't cut through M4 / M7 bodies.  Drop vertical stubs from
    # N2.gate and N4.gate down to that height, then a clean horizontal run.
    Y_VB3 = Y_VSS + 0.8
    d += elm.Line().endpoints((N2.gate[0], Y_NMOS_G), (N2.gate[0], Y_VB3))
    d += elm.Line().endpoints((N4.gate[0], Y_NMOS_G), (N4.gate[0], Y_VB3))
    hwire(d, N2.gate[0], N4.gate[0], Y_VB3)
    d += elm.Dot().at((N2.gate[0], Y_NMOS_G))
    d += elm.Dot().at((N4.gate[0], Y_NMOS_G))

    # ==================== title + sizing table ====================
    lab(d, ((XL + XR)/2, Y_VDD + 1.3),
        'Sooch low-voltage cascoded bias  --  VDD = 0.9 V',
        fontsize=14)

    table_y = Y_VSS - 3.0
    lab(d, ((XL + XR)/2, table_y + 0.6),
        'Device sizing  (sky130_fd_pr LVT)', fontsize=11)
    rows = [
        'M1 = XMP_REF    L=1  W=16 nf=4 m=8     (PMOS, diode)',
        'M2 = XMP_VB3    L=1  W=16 nf=4 m=8     (PMOS, top of cascode)',
        'M3 = XMP_VB3C   L=0.5 W=16 nf=4 m=8    (PMOS, cascode)',
        'M4 = XMN_REF    L=0.5 W=4  nf=2 m=8    (NMOS, diode)',
        'M5 = XMP_B2     L=1  W=16 nf=4 m=8     (PMOS, top of cascode)',
        'M6 = XMP_B2C    L=0.5 W=16 nf=4 m=8    (PMOS, cascode)',
        'M7 = XMN_B2     L=2  W=4  nf=2 m=8     (NMOS, 1/4 aspect diode)',
        'M8 = XMP_B1     L=4  W=16 nf=4 m=8     (PMOS, 1/4 aspect diode)',
        'M9 = XMN_B1     L=0.5 W=4  nf=2 m=8    (NMOS, sink)',
    ]
    for i, row in enumerate(rows):
        lab(d, (XL + 1.0, table_y - 0.4 - i * 0.55), row,
            fontsize=8, halign='left')

    lab(d, ((XL + XR)/2, table_y - 0.4 - len(rows) * 0.55 - 0.6),
        'Mirror gates connect directly at gate height (no top buses).  '
        'Cascoded pfets pin Vds = Vov ~ 0.15 V  ->  copy accuracy boosted '
        'by gm*rds (~30 dB).\n'
        'Col 4 (VBIAS1) stays uncascoded: at VBIAS1 ~ 0.2 V there is no '
        'NMOS Vds_sat margin to stack a second device.\n'
        'Startup (not drawn): 50M from nVB3i / nVB2i to VSS, 20M from '
        'VBIAS1 to VSS.  Signal path UNTOUCHED.',
        fontsize=9)

    OUT = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_bias_sooch'
    d.save(OUT + '.png', dpi=180)
    d.save(OUT + '.svg')

print('wrote sketch_bias_sooch.{png,svg}')
