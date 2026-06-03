"""
Folded-cascode SE OTA (PMOS input, low-VDD wide-swing cascode bias).

Clean v2: uses default vertical FET orientation.
NFet  -> source bottom, drain top, gate left   (flip=reverse() gives gate right)
PFet  -> source top, drain bottom, gate left   (flip=reverse() gives gate right)

Place by FET source: .at((x, y_source)).

Run: python folded_cascode_se.py
"""

import schemdraw
import schemdraw.elements as elm


def pmos(d, x, y_src, name, gate_label=None, gate_color="darkgreen", flip=False):
    m = (elm.PFet().reverse() if flip else elm.PFet()).at((x, y_src))
    d += m
    d += elm.Label().at((x + 0.35, y_src - 0.7)).label(name, loc="right", fontsize=9)
    if gate_label:
        gx, gy = m.gate
        if flip:
            d += elm.Line().at(m.gate).right(0.4)
            d += elm.Label().at((gx + 0.5, gy)).label(gate_label, loc="right",
                                                       color=gate_color, fontsize=9)
        else:
            d += elm.Line().at(m.gate).left(0.4)
            d += elm.Label().at((gx - 0.5, gy)).label(gate_label, loc="left",
                                                       color=gate_color, fontsize=9)
    return m


def nmos(d, x, y_src, name, gate_label=None, gate_color="purple", flip=False):
    m = (elm.NFet().reverse() if flip else elm.NFet()).at((x, y_src))
    d += m
    d += elm.Label().at((x + 0.35, y_src + 0.7)).label(name, loc="right", fontsize=9)
    if gate_label:
        gx, gy = m.gate
        if flip:
            d += elm.Line().at(m.gate).right(0.4)
            d += elm.Label().at((gx + 0.5, gy)).label(gate_label, loc="right",
                                                       color=gate_color, fontsize=9)
        else:
            d += elm.Line().at(m.gate).left(0.4)
            d += elm.Label().at((gx - 0.5, gy)).label(gate_label, loc="left",
                                                       color=gate_color, fontsize=9)
    return m


with schemdraw.Drawing(file="folded_cascode_se.svg", show=False) as d:
    d.config(unit=1.0, fontsize=10, lw=1.2)

    # FETs in schemdraw are ~2 units tall. Grid tuned so columns/rows fit cleanly.
    X1, X2, X3L, X3R, X4D, X4O = 0, 3, 6.5, 9.5, 13, 16
    Y_VDD, Y_VSS = 14, 0

    # Rails
    d += elm.Line().at((-1, Y_VDD)).to((18, Y_VDD)).color("red")
    d += elm.Label().at((18.3, Y_VDD)).label("VDD = 1.2 V", loc="right", color="red")
    d += elm.Line().at((-1, Y_VSS)).to((18, Y_VSS)).color("blue")
    d += elm.Label().at((18.3, Y_VSS)).label("VSS", loc="right", color="blue")

    # ============ COL-1: P-side bias (generates VP1, VP2) ============
    mpr = pmos(d, X1, Y_VDD - 1, "MPR")
    d += elm.Line().at(mpr.source).to((X1, Y_VDD))
    d += elm.Line().at(mpr.gate).left(0.6).down(mpr.gate[1] - mpr.drain[1]).right(0.6).to(mpr.drain)
    d += elm.Dot().at(mpr.drain)
    d += elm.Label().at((X1 + 0.4, mpr.drain[1])).label("VP1", loc="right", color="darkgreen")

    mpc = pmos(d, X1, mpr.drain[1] - 0.3, "MPC")
    d += elm.Line().at(mpc.source).to(mpr.drain)
    d += elm.Dot().at(mpc.drain)
    d += elm.Label().at((X1 + 0.4, mpc.drain[1])).label("VP2", loc="right", color="darkgreen")
    d += elm.Line().at(mpc.gate).left(1.0).down(mpc.gate[1] - mpc.drain[1]).right(1.0).to(mpc.drain)

    rp = elm.Resistor().at(mpc.drain).down().label("Rp")
    d += rp
    i1 = elm.SourceI().at(rp.end).down().label("I1\n(IBGR)")
    d += i1
    d += elm.Line().at(i1.end).to((X1, Y_VSS))

    # ============ COL-2: N-side bias (generates VN1, VN2) ============
    mp3 = pmos(d, X2, Y_VDD - 1, "MP3", gate_label="VP1")
    d += elm.Line().at(mp3.source).to((X2, Y_VDD))

    mp8 = pmos(d, X2, mp3.drain[1] - 0.3, "MP8(aux)")
    d += elm.Line().at(mp8.source).to(mp3.drain)
    d += elm.Line().at(mp8.gate).left(0.8).down(mp8.gate[1] - mp8.drain[1]).right(0.8).to(mp8.drain)

    rp2 = elm.Resistor().at(mp8.drain).down().label("Rp2")
    d += rp2

    mn9 = nmos(d, X2, rp2.end[1] - 1.6, "MN9")
    d += elm.Line().at(mn9.drain).to(rp2.end)
    d += elm.Dot().at(mn9.drain)
    d += elm.Label().at((X2 + 0.4, mn9.drain[1])).label("VN1", loc="right", color="purple")
    d += elm.Line().at(mn9.gate).left(0.8).up(mn9.drain[1] - mn9.gate[1]).right(0.8).to(mn9.drain)

    mn10 = nmos(d, X2, Y_VSS, "MN10", gate_label="VN2")
    d += elm.Line().at(mn10.drain).to(mn9.source)
    d += elm.Dot().at(mn9.source)
    d += elm.Label().at((X2 + 0.4, mn9.source[1])).label("VN2", loc="right", color="purple")
    d += elm.Line().at(mn10.gate).left(1.0).up(mn9.source[1] - mn10.gate[1]).right(1.0).to(mn9.source)

    # ============ COL-3: input pair + fold sinks ============
    XC = (X3L + X3R) / 2
    mtl = pmos(d, XC, Y_VDD - 1, "MTL", gate_label="VP1")
    d += elm.Line().at(mtl.source).to((XC, Y_VDD))
    vtail = mtl.drain
    d += elm.Dot().at(vtail)
    d += elm.Label().at((XC + 0.3, vtail[1])).label("Vtail", loc="right")

    y_in_src = vtail[1] - 0.5
    d += elm.Line().at(vtail).to((X3L, vtail[1])).to((X3L, y_in_src))
    d += elm.Line().at(vtail).to((X3R, vtail[1])).to((X3R, y_in_src))

    mpl = pmos(d, X3L, y_in_src, "MP_L")
    mpr_in = pmos(d, X3R, y_in_src, "MP_R", flip=True)
    d += elm.Line().at(mpl.gate).left(0.8)
    d += elm.Label().at((mpl.gate[0] - 1.0, mpl.gate[1])).label("Vinp", loc="left", color="blue")
    d += elm.Line().at(mpr_in.gate).right(0.8)
    d += elm.Label().at((mpr_in.gate[0] + 1.0, mpr_in.gate[1])).label("Vinn", loc="right", color="blue")

    d += elm.Dot().at(mpl.drain)
    d += elm.Dot().at(mpr_in.drain)
    d += elm.Label().at((mpl.drain[0] - 0.3, mpl.drain[1] - 0.3)).label("Vmidn", loc="left", color="orange")
    d += elm.Label().at((mpr_in.drain[0] + 0.3, mpr_in.drain[1] - 0.3)).label("Vmidp", loc="right", color="orange")

    mnfl = nmos(d, X3L, Y_VSS, "MNF_L", gate_label="VN1")
    mnfr = nmos(d, X3R, Y_VSS, "MNF_R", gate_label="VN1", flip=True)
    d += elm.Line().at(mnfl.drain).to((X3L, mpl.drain[1]))
    d += elm.Line().at(mnfr.drain).to((X3R, mpr_in.drain[1]))

    # ============ COL-4: output stack + mirror ============
    # LEFT branch (X4D)
    ml_d = pmos(d, X4D, Y_VDD - 1, "ML_D", gate_label="VP1")
    d += elm.Line().at(ml_d.source).to((X4D, Y_VDD))
    mc_d = pmos(d, X4D, ml_d.drain[1] - 0.3, "MC_D", gate_label="VP2")
    d += elm.Line().at(mc_d.source).to(ml_d.drain)
    nodeA = mc_d.drain
    d += elm.Dot().at(nodeA)
    d += elm.Label().at((X4D - 0.4, nodeA[1] + 0.2)).label("A", loc="left", color="red")

    mn1 = nmos(d, X4D, Y_VSS, "MN1(diode)")
    d += elm.Line().at(mn1.gate).left(0.6).up(mn1.drain[1] - mn1.gate[1]).right(0.6).to(mn1.drain)
    mnc_d = nmos(d, X4D, mn1.drain[1] + 0.3, "MNC_D", gate_label="VN2")
    d += elm.Line().at(mnc_d.source).to(mn1.drain)
    d += elm.Line().at(mnc_d.drain).to(nodeA)

    # FOLD: Vmidn (mpl.drain) -> mn1.drain
    vmidn_y = mpl.drain[1]
    d += elm.Line().at(mpl.drain).to((X4D, vmidn_y)).color("orange").linewidth(1.5)
    d += elm.Line().at((X4D, vmidn_y)).to(mn1.drain).color("orange").linewidth(1.5)

    # RIGHT branch (X4O)
    ml_o = pmos(d, X4O, Y_VDD - 1, "ML_O", gate_label="VP1", flip=True)
    d += elm.Line().at(ml_o.source).to((X4O, Y_VDD))
    mc_o = pmos(d, X4O, ml_o.drain[1] - 0.3, "MC_O", gate_label="VP2", flip=True)
    d += elm.Line().at(mc_o.source).to(ml_o.drain)
    voutp = mc_o.drain
    d += elm.Dot().at(voutp)
    d += elm.Label().at((X4O + 0.4, voutp[1] + 0.2)).label("Voutp", loc="right", color="red")

    mn2 = nmos(d, X4O, Y_VSS, "MN2(mirror)", flip=True)
    mnc_o = nmos(d, X4O, mn2.drain[1] + 0.3, "MNC_O", gate_label="VN2", flip=True)
    d += elm.Line().at(mnc_o.source).to(mn2.drain)
    d += elm.Line().at(mnc_o.drain).to(voutp)

    vmidp_y = mpr_in.drain[1]
    d += elm.Line().at(mpr_in.drain).to((X4O, vmidp_y)).color("orange").linewidth(1.5)
    d += elm.Line().at((X4O, vmidp_y)).to(mn2.drain).color("orange").linewidth(1.5)

    # *** MIRROR WIRE: MN1.gate -> MN2.gate ***
    yroute = Y_VSS - 1.2
    d += elm.Line().at(mn1.gate).left(0.6).down(mn1.gate[1] - yroute).color("red").linewidth(2)
    d += elm.Line().at((mn1.gate[0] - 0.6, yroute)).to((mn2.gate[0] + 0.6, yroute)).color("red").linewidth(2)
    d += elm.Line().at((mn2.gate[0] + 0.6, yroute)).up(mn2.gate[1] - yroute)
    d += elm.Line().at((mn2.gate[0] + 0.6, mn2.gate[1])).to(mn2.gate).color("red").linewidth(2)
    d += elm.Label().at(((X4D + X4O)/2, yroute - 0.3)).label(
        "MN1.gate -> MN2.gate   (diff -> single conversion)",
        loc="bottom", color="red", fontsize=9)

    # Load cap
    d += elm.Line().at(voutp).right(1.5)
    cl = elm.Capacitor().at((X4O + 1.5, voutp[1])).down().toy(Y_VSS).label("C_L")
    d += cl

    # Title
    d += elm.Label().at((9, Y_VDD + 1.2)).label(
        "PMOS-input SE Folded Cascode  (sky130A, VDD=1.2V, wide-swing cascode bias)",
        loc="top", fontsize=12)
    d += elm.Label().at((9, Y_VDD + 0.4)).label(
        "COL-1 P-bias | COL-2 N-bias | COL-3 input pair + fold sinks | COL-4 output stack + mirror",
        loc="top", fontsize=9, color="gray")

    d.save("folded_cascode_se.png", dpi=200)

print("OK -> folded_cascode_se.svg, folded_cascode_se.png")
