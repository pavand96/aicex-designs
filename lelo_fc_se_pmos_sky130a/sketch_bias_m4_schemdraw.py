"""
Schemdraw schematic of the bias-only m=4 fix (signal path UNTOUCHED).

Shows the four reference branches of the bias generator, each device labeled
with L, W, nf, m. Signal-path block shown abstractly on the right as a box.

Run:  python sketch_bias_m4_schemdraw.py
Output: sketch_bias_m4_schemdraw.svg, .png
"""
import schemdraw
import schemdraw.elements as elm

OUT_SVG = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_bias_m4_schemdraw.svg'
OUT_PNG = '/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_bias_m4_schemdraw.png'

# --- helper ---
def label_dev(d, fet, lines):
    """Attach a multi-line label to the side of a FET."""
    txt = '\n'.join(lines)
    d += elm.Label().at(fet.center).label(txt, loc='right', ofst=(0.6, 0), fontsize=8)


with schemdraw.Drawing(file=OUT_SVG, show=False) as d:
    d.config(unit=2.0, fontsize=10)

    # ============================================================
    # VDD rail (top) and VSS rail (bottom)
    # ============================================================
    d += elm.Line().right(d.unit * 12).label('VDD', loc='left').color('red')
    VDD_start = (0, 0)
    # We will use anchors via at() instead. Keep absolute coords.

    # Reset and build from scratch with explicit positions.

with schemdraw.Drawing(file=OUT_SVG, show=False) as d:
    d.config(unit=2.0, fontsize=10)

    # ---- rails ----
    d += (vdd := elm.Line().endpoints((0, 0), (24, 0)).color('red'))
    d += elm.Label().at((-0.4, 0)).label('VDD', loc='left', color='red')
    d += (vss := elm.Line().endpoints((0, -14), (24, -14)).color('blue'))
    d += elm.Label().at((-0.4, -14)).label('VSS', loc='left', color='blue')

    # ============================================================
    # Branch 1: IBIAS pin -> VBP diode (m=4 NEW)
    # ============================================================
    x1 = 2
    # PMOS diode at IBIAS, drain=gate=IBIAS
    d += (mp_ref := elm.PFet(bulk=True).at((x1, -2)).label(
        'XMP_REF\nL=1 W=16\nnf=4  m=4', loc='right', fontsize=7, ofst=(0.4, 0)))
    # source -> VDD
    d += elm.Line().endpoints(mp_ref.source, (x1, 0))
    # drain (down) -> IBIAS node
    d += elm.Dot().at(mp_ref.drain).label('IBIAS / VBP', loc='left', fontsize=8)
    # diode tie: gate -> drain
    d += elm.Line().left(0.8).at(mp_ref.gate)
    d += elm.Line().down(abs(mp_ref.gate[1] - mp_ref.drain[1]))
    d += elm.Line().right(0.8)
    # external 10uA sink to VSS via current source symbol
    d += (isink := elm.SourceI().at(mp_ref.drain).down().length(2.2).label('10uA\n(ext)', fontsize=7))
    d += elm.Line().endpoints(isink.end, (x1, -14))

    # tap VBP to the right for fan-out
    d += elm.Line().right(2).at(mp_ref.drain).color('green')
    d += elm.Label().at((x1+2, mp_ref.drain[1]+0.3)).label('VBP bus', loc='right', fontsize=7, color='green')
    vbp_bus_y = mp_ref.drain[1]

    # ============================================================
    # Branch 2: VBP-mirror PMOS over NMOS diode -> VBIAS3 (m=4 NEW)
    # ============================================================
    x2 = 7
    d += (mp_vb3 := elm.PFet(bulk=True).at((x2, -2)).label(
        'XMP_VB3\nL=1 W=16\nnf=4  m=4', loc='right', fontsize=7, ofst=(0.4, 0)))
    d += elm.Line().endpoints(mp_vb3.source, (x2, 0))
    # gate from VBP bus
    d += elm.Line().left(x2 - x1).at(mp_vb3.gate).color('green')
    # drain down to NMOS diode drain
    d += elm.Line().endpoints(mp_vb3.drain, (x2, -8))
    d += elm.Dot().at((x2, -8)).label('VBIAS3', loc='right', fontsize=8)
    vbias3_y = -8
    d += (mn_ref := elm.NFet(bulk=True).at((x2, -10)).label(
        'XMN_REF\nL=0.5 W=4\nnf=2  m=4', loc='right', fontsize=7, ofst=(0.4, 0)))
    d += elm.Line().endpoints(mn_ref.drain, (x2, -8))
    d += elm.Line().endpoints(mn_ref.source, (x2, -14))
    # diode tie
    d += elm.Line().left(0.8).at(mn_ref.gate)
    d += elm.Line().up(abs(mn_ref.gate[1] - mn_ref.drain[1]))
    d += elm.Line().right(0.8)
    # tap VBIAS3 bus
    d += elm.Line().right(2).at((x2, vbias3_y)).color('purple')
    d += elm.Label().at((x2+2, vbias3_y+0.3)).label('VBIAS3 bus', loc='right', fontsize=7, color='purple')

    # ============================================================
    # Branch 3: VBIAS2 (low-V NMOS cascode bias), m=4 NEW
    # ============================================================
    x3 = 12
    d += (mp_b2 := elm.PFet(bulk=True).at((x3, -2)).label(
        'XMP_B2\nL=1 W=16\nnf=4  m=4', loc='right', fontsize=7, ofst=(0.4, 0)))
    d += elm.Line().endpoints(mp_b2.source, (x3, 0))
    # gate from VBP bus
    d += elm.Line().left(x3 - x1).at(mp_b2.gate).color('green')
    d += elm.Line().endpoints(mp_b2.drain, (x3, -6))
    d += elm.Dot().at((x3, -6)).label('VBIAS2', loc='right', fontsize=8)
    d += (mn_b2 := elm.NFet(bulk=True).at((x3, -10)).label(
        'XMN_B2\nL=2 W=4\nnf=2  m=4\n(1/4 aspect)', loc='right', fontsize=7, ofst=(0.4, 0)))
    d += elm.Line().endpoints(mn_b2.drain, (x3, -6))
    d += elm.Line().endpoints(mn_b2.source, (x3, -14))
    # diode tie
    d += elm.Line().left(0.8).at(mn_b2.gate)
    d += elm.Line().up(abs(mn_b2.gate[1] - mn_b2.drain[1]))
    d += elm.Line().right(0.8)

    # ============================================================
    # Branch 4: VBIAS1 (low-V PMOS cascode bias), m=4 NEW
    # ============================================================
    x4 = 18
    d += (mp_b1 := elm.PFet(bulk=True).at((x4, -2)).label(
        'XMP_B1\nL=4 W=16\nnf=4  m=4\n(1/4 aspect)', loc='right', fontsize=7, ofst=(0.4, 0)))
    d += elm.Line().endpoints(mp_b1.source, (x4, 0))
    d += elm.Dot().at(mp_b1.drain).label('VBIAS1', loc='right', fontsize=8)
    # diode tie
    d += elm.Line().left(0.8).at(mp_b1.gate)
    d += elm.Line().down(abs(mp_b1.gate[1] - mp_b1.drain[1]))
    d += elm.Line().right(0.8)
    d += elm.Line().endpoints(mp_b1.drain, (x4, -10))
    d += (mn_b1 := elm.NFet(bulk=True).at((x4, -10)).label(
        'XMN_B1\nL=0.5 W=4\nnf=2  m=4', loc='right', fontsize=7, ofst=(0.4, 0)))
    d += elm.Line().endpoints(mn_b1.drain, (x4, -10))  # connection
    d += elm.Line().endpoints(mn_b1.source, (x4, -14))
    # gate of MN_B1 from VBIAS3 bus
    d += elm.Line().left(x4 - x2).at(mn_b1.gate).color('purple')

    # ============================================================
    # Title and notes
    # ============================================================
    d += elm.Label().at((12, 1.5)).label(
        'Bias-only m=4 fix (signal path UNTOUCHED) -- VDD = 0.9 V',
        fontsize=12)
    d += elm.Label().at((12, -15.5)).label(
        'All bias references now use m=4 parallel unit cells. '
        'W/L unchanged -> mirror ratios preserved, DC OP unchanged.\n'
        'sigma(deltaVt) ~ 1/sqrt(m*W*L)  =>  m=4 halves Vt mismatch '
        '-> MC: 250/250 PASS, A0 >= 39.7 dB, PM >= 74 deg.',
        fontsize=8)

    d.save(OUT_PNG, dpi=150)

print(f'wrote {OUT_SVG}')
print(f'wrote {OUT_PNG}')
