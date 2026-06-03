"""
Generate xschem schematic for PMOS-input SE folded cascode (sky130A).
Bias voltages (VP1, VP2, VN1, VN2) are external ipins for clarity.

Run:  python gen_xschem_sch.py
Open: xschem folded_cascode_se.sch
"""

# ---------- xschem helpers ----------

OUT = []

def wire(x1, y1, x2, y2, lab="#net"):
    OUT.append(f'N {x1} {y1} {x2} {y2} {{lab={lab}}}')

def label(x, y, name, rot=0, flip=0):
    OUT.append(f'C {{devices/lab_pin.sym}} {x} {y} {rot} {flip} {{name=l_{name} sig_type=std_logic lab={name}}}')

def ipin(x, y, name, rot=0, flip=0):
    OUT.append(f'C {{devices/ipin.sym}} {x} {y} {rot} {flip} {{name=p_{name} lab={name}}}')

def opin(x, y, name, rot=0, flip=0):
    OUT.append(f'C {{devices/opin.sym}} {x} {y} {rot} {flip} {{name=p_{name} lab={name}}}')

def pfet(x, y, name, W=10, L=0.5, nf=2, model="pfet_01v8_lvt", flip=0):
    """PFET symbol origin at (x,y). Pins (rot=0, flip=0):
       S = (x+20, y-30)  G = (x-20, y)  D = (x+20, y+30)  B = (x+20, y)
       With flip=1: S = (x-20, y-30) G = (x+20, y) D = (x-20, y+30)
    """
    OUT.append(
        f'C {{sky130_fd_pr/{model}.sym}} {x} {y} 0 {flip} {{name={name}\n'
        f'W={W}\nL={L}\nnf={nf}\nmult=1\n'
        f'ad="expr(\'int((@nf + 1)/2) * @W / @nf * 0.29\')"\n'
        f'pd="expr(\'2*int((@nf + 1)/2) * (@W / @nf + 0.29)\')"\n'
        f'as="expr(\'int((@nf + 2)/2) * @W / @nf * 0.29\')"\n'
        f'ps="expr(\'2*int((@nf + 2)/2) * (@W / @nf + 0.29)\')"\n'
        f'nrd="expr(\'0.29 / @W \')" nrs="expr(\'0.29 / @W \')"\n'
        f'sa=0 sb=0 sd=0\n'
        f'model={model}\nspiceprefix=X\n}}'
    )

def nfet(x, y, name, W=4, L=0.5, nf=2, model="nfet_01v8_lvt", flip=0):
    OUT.append(
        f'C {{sky130_fd_pr/{model}.sym}} {x} {y} 0 {flip} {{name={name}\n'
        f'W={W}\nL={L}\nnf={nf}\nmult=1\n'
        f'ad="expr(\'int((@nf + 1)/2) * @W / @nf * 0.29\')"\n'
        f'pd="expr(\'2*int((@nf + 1)/2) * (@W / @nf + 0.29)\')"\n'
        f'as="expr(\'int((@nf + 2)/2) * @W / @nf * 0.29\')"\n'
        f'ps="expr(\'2*int((@nf + 2)/2) * (@W / @nf + 0.29)\')"\n'
        f'nrd="expr(\'0.29 / @W \')" nrs="expr(\'0.29 / @W \')"\n'
        f'sa=0 sb=0 sd=0\n'
        f'model={model}\nspiceprefix=X\n}}'
    )

def cap(x, y, name, value="1p"):
    OUT.append(f'C {{devices/capa.sym}} {x} {y} 0 0 {{name={name} value={value} footprint=1206 device="ceramic capacitor"}}')

def res(x, y, name, value="10k"):
    """Vertical resistor: P pin at (x, y-30), M pin at (x, y+30)."""
    OUT.append(f'C {{devices/res.sym}} {x} {y} 0 0 {{name={name} value={value} footprint=1206 device=resistor m=1}}')

def isrc(x, y, name, value="10u"):
    """Vertical current source: p pin at (x, y-30) (top, current flows IN from + to -), m pin at (x, y+30)."""
    OUT.append(f'C {{devices/isource.sym}} {x} {y} 0 0 {{name={name} value={value}}}')


# Pin offsets for placed FETs
def pS(x, y, flip=0):  # PFET source (top)
    return (x - 20 if flip else x + 20, y - 30)
def pD(x, y, flip=0):  # PFET drain (bottom)
    return (x - 20 if flip else x + 20, y + 30)
def pG(x, y, flip=0):  # PFET gate (left/right)
    return (x + 20 if flip else x - 20, y)

def nD(x, y, flip=0):  # NFET drain (top)
    return (x - 20 if flip else x + 20, y - 30)
def nS(x, y, flip=0):  # NFET source (bottom)
    return (x - 20 if flip else x + 20, y + 30)
def nG(x, y, flip=0):
    return (x + 20 if flip else x - 20, y)


# ============================================================================
# LAYOUT
# ============================================================================
# Column X positions
X_BIAS  = -200         # external bias ipins live here
X_IN    = 200          # input ipin column (Vinp/Vinn)
X_TAIL  = 600          # MTL (tail PMOS) and input pair sits around here
X_L     = 500          # MP_L  (input pair left)
X_R     = 700          # MP_R  (input pair right) - flipped
X_FOLDL = 500          # MNF_L
X_FOLDR = 700          # MNF_R
X_OUT_L = 1000         # output stack LEFT branch (diode side)
X_OUT_R = 1200         # output stack RIGHT branch (Voutp)

# Row Y positions (xschem +Y is DOWN on screen)
Y_VDD     = -700
Y_TAIL    = -600       # MTL placement Y
Y_INPUT   = -440       # input pair MP_L / MP_R placement Y
Y_FOLD    = -200       # fold-node Y (the bus between input drains and cascode sources)
Y_OUT_PCAS = -350      # MC_D / MC_O placement Y (PMOS cascode)
Y_OUT_PLD  = -550      # ML_D / ML_O placement Y (PMOS load)
Y_OUT_NCAS = -50       # MNC_D / MNC_O placement Y (NMOS cascode)
Y_MIRROR   = 150       # MN1 / MN2 placement Y (mirror)
Y_VSS      = 280

# ============ PINS ============
# VDD / VSS power pins (top-right and bottom-right area)
ipin(X_BIAS - 600, Y_VDD, "VDD")
ipin(X_BIAS - 600, Y_VSS, "VSS")
# Inputs
ipin(X_IN, Y_INPUT, "Vinp")
ipin(X_IN, Y_INPUT, "Vinn"); OUT.pop()  # remove dup; we'll place Vinn on right
# place Vinn properly far right
ipin(1500, Y_INPUT, "Vinn", rot=0, flip=1)
# Output
opin(1500, Y_OUT_PCAS + 30, "Voutp")

# ============ VDD and VSS RAILS ============
wire(X_BIAS - 600, Y_VDD, 1400, Y_VDD, "VDD")
wire(X_BIAS - 600, Y_VSS, 1400, Y_VSS, "VSS")

# ============================================================================
# BIAS GENERATOR (wide-swing Sooch style, low-VDD compatible)
#
# COL-A (X_BP, X_BN below): generates VP1, VP2 (P-side wide-swing)
#   VDD -- MPR(diode) --VP1-- MPC --VP2-- Rp -- I1(IBGR sink) -- VSS
#   MPC.gate ties to VP2 (its own drain) -> Sooch low-Vdsat scheme
#
# COL-B: generates VN1, VN2 (N-side wide-swing) using same I_REF mirrored
#   VDD -- MP3(gate=VP1 mirror) -- MP8(aux,diode) -- Rp2 -- MN9(diode)=VN1 --VN2-- MN10 -- VSS
#   MN10.gate ties to VN2 (its own drain) -> Sooch wide-swing
# ============================================================================
X_BP = -500
X_BN = -300

# ---- P-side bias generator ----
# MPR: PMOS diode at top. Place at (X_BP, Y_TAIL). Source up to VDD, drain down = VP1.
pfet(X_BP, Y_TAIL, "MPR", W=10, L=1.0, nf=2)
sx, sy = pS(X_BP, Y_TAIL)
dx, dy = pD(X_BP, Y_TAIL)
gx, gy = pG(X_BP, Y_TAIL)
wire(sx, sy, sx, Y_VDD, "VDD")
# diode connect: gate -> drain (route to the left and down)
wire(gx, gy, gx - 30, gy, "VP1")
wire(gx - 30, gy, gx - 30, dy, "VP1")
wire(gx - 30, dy, dx, dy, "VP1")
label(dx + 40, dy, "VP1")  # tag node VP1 by name

# MPC: PMOS cascode below MPR. Source = MPR.drain (VP1), drain = VP2, gate = VP2 (self).
pfet(X_BP, Y_OUT_PLD, "MPC", W=10, L=1.0, nf=2)
sx2, sy2 = pS(X_BP, Y_OUT_PLD)
dx2, dy2 = pD(X_BP, Y_OUT_PLD)
gx2, gy2 = pG(X_BP, Y_OUT_PLD)
wire(sx2, sy2, dx, dy, "VP1")  # connect MPC.source to MPR.drain
wire(gx2, gy2, gx2 - 50, gy2, "VP2")
wire(gx2 - 50, gy2, gx2 - 50, dy2, "VP2")
wire(gx2 - 50, dy2, dx2, dy2, "VP2")
label(dx2 + 40, dy2, "VP2")

# Rp resistor: drops Vov_p so MPC stays in saturation
res(X_BP + 20, Y_OUT_PCAS + 40, "Rp", value="20k")
# res P pin at (X_BP+20, Y_OUT_PCAS+40-30) ; M pin at (X_BP+20, Y_OUT_PCAS+40+30)
rp_top_y = Y_OUT_PCAS + 40 - 30
rp_bot_y = Y_OUT_PCAS + 40 + 30
wire(dx2, dy2, X_BP + 20, rp_top_y, "VP2")  # connect MPC.drain to Rp top (same wire as VP2)
# I1 current sink (IBGR): top = bottom of Rp, bottom -> VSS
isrc(X_BP + 20, Y_OUT_NCAS + 50, "I1", value="10u")
i1_top_y = Y_OUT_NCAS + 50 - 30
i1_bot_y = Y_OUT_NCAS + 50 + 30
wire(X_BP + 20, rp_bot_y, X_BP + 20, i1_top_y, "n_rp_i1")
wire(X_BP + 20, i1_bot_y, X_BP + 20, Y_VSS, "VSS")

# ---- N-side bias generator ----
# MP3: PMOS mirror, gate=VP1.  Generates the same I_REF in the N branch.
pfet(X_BN, Y_TAIL, "MP3", W=10, L=1.0, nf=2)
sx3, sy3 = pS(X_BN, Y_TAIL)
dx3, dy3 = pD(X_BN, Y_TAIL)
gx3, gy3 = pG(X_BN, Y_TAIL)
wire(sx3, sy3, sx3, Y_VDD, "VDD")
wire(gx3, gy3, gx3 - 40, gy3, "VP1")
label(gx3 - 60, gy3, "VP1")

# MP8 aux PMOS diode (Sooch helper) below MP3.
pfet(X_BN, Y_OUT_PLD, "MP8", W=10, L=1.0, nf=2)
sx4, sy4 = pS(X_BN, Y_OUT_PLD)
dx4, dy4 = pD(X_BN, Y_OUT_PLD)
gx4, gy4 = pG(X_BN, Y_OUT_PLD)
wire(sx4, sy4, dx3, dy3, "n_mp3_mp8")
# diode connect MP8
wire(gx4, gy4, gx4 - 30, gy4, "n_mp8_d")
wire(gx4 - 30, gy4, gx4 - 30, dy4, "n_mp8_d")
wire(gx4 - 30, dy4, dx4, dy4, "n_mp8_d")

# Rp2 resistor below MP8
res(X_BN + 20, Y_OUT_PCAS + 40, "Rp2", value="20k")
rp2_top_y = Y_OUT_PCAS + 40 - 30
rp2_bot_y = Y_OUT_PCAS + 40 + 30
wire(dx4, dy4, X_BN + 20, rp2_top_y, "n_mp8_d")

# MN9: NMOS diode = VN1 node. Drain at top connects to Rp2 bottom; source goes to VN2 node.
Y_MN9 = Y_OUT_NCAS
nfet(X_BN, Y_MN9, "MN9", W=4, L=0.5, nf=2)
dx9, dy9 = nD(X_BN, Y_MN9)
sx9, sy9 = nS(X_BN, Y_MN9)
gx9, gy9 = nG(X_BN, Y_MN9)
wire(dx9, dy9, X_BN + 20, rp2_bot_y, "VN1")
# diode connect MN9
wire(gx9, gy9, gx9 - 30, gy9, "VN1")
wire(gx9 - 30, gy9, gx9 - 30, dy9, "VN1")
wire(gx9 - 30, dy9, dx9, dy9, "VN1")
label(dx9 + 40, dy9, "VN1")

# MN10: NMOS at bottom, source = VSS. Drain = source of MN9 = VN2; gate = VN2 (Sooch).
Y_MN10 = Y_VSS - 30  # so source at VSS
nfet(X_BN, Y_MN10, "MN10", W=4, L=0.5, nf=2)
dx10, dy10 = nD(X_BN, Y_MN10)
sx10, sy10 = nS(X_BN, Y_MN10)
gx10, gy10 = nG(X_BN, Y_MN10)
wire(dx10, dy10, sx9, sy9, "VN2")
wire(sx10, sy10, sx10, Y_VSS, "VSS")
# Sooch tie: MN10.gate to VN2 (its own drain)
wire(gx10, gy10, gx10 - 50, gy10, "VN2")
wire(gx10 - 50, gy10, gx10 - 50, dy10, "VN2")
wire(gx10 - 50, dy10, dx10, dy10, "VN2")
label(dx10 + 40, dy10, "VN2")


# ============ COL-3 : TAIL + INPUT PAIR ============
# MTL: PMOS tail. Place at (X_TAIL, Y_TAIL). Source up to VDD, drain down = Vtail.
pfet(X_TAIL, Y_TAIL, "MTL", W=20, L=0.5, nf=4)
sx, sy = pS(X_TAIL, Y_TAIL)
dx, dy = pD(X_TAIL, Y_TAIL)
gx, gy = pG(X_TAIL, Y_TAIL)
wire(sx, sy, sx, Y_VDD, "VDD")        # source up to VDD rail
wire(gx, gy, X_BIAS + 50, gy, "VP1")  # gate stub to left
wire(X_BIAS + 50, gy, X_BIAS + 50, -640, "VP1")
wire(X_BIAS + 50, -640, X_BIAS + 20, -640, "VP1")
label(gx - 20, gy, "VP1")
# Vtail node = drain of MTL, split to MP_L and MP_R sources
wire(dx, dy, dx, -480, "Vtail")  # short stub down
label(dx, -490, "Vtail")
# Horizontal Vtail bus
y_vtail = -480
wire(dx, y_vtail, X_L + 20, y_vtail, "Vtail")    # to MP_L source (flip=0 source at X_L+20)
wire(dx, y_vtail, X_R - 20, y_vtail, "Vtail")    # to MP_R source (flip=1 source at X_R-20)

# MP_L: PMOS input left at (X_L, Y_INPUT). flip=0 → source top, gate left.
pfet(X_L, Y_INPUT, "MP_L", W=20, L=0.5, nf=4)
sx, sy = pS(X_L, Y_INPUT)
dx, dy = pD(X_L, Y_INPUT)
gx, gy = pG(X_L, Y_INPUT)
wire(sx, sy, sx, y_vtail, "Vtail")
wire(gx, gy, X_IN + 20, gy, "Vinp")
label(gx - 20, gy, "Vinp")
# drain = Vmidn down to fold node
wire(dx, dy, dx, Y_FOLD, "Vmidn")
label(dx, Y_FOLD - 10, "Vmidn")

# MP_R: input right at (X_R, Y_INPUT), flip=1 → source top (x-20), gate right.
pfet(X_R, Y_INPUT, "MP_R", W=20, L=0.5, nf=4, flip=1)
sx, sy = pS(X_R, Y_INPUT, flip=1)
dx, dy = pD(X_R, Y_INPUT, flip=1)
gx, gy = pG(X_R, Y_INPUT, flip=1)
wire(sx, sy, sx, y_vtail, "Vtail")
wire(gx, gy, 1500 - 20, gy, "Vinn")
label(gx + 20, gy, "Vinn")
wire(dx, dy, dx, Y_FOLD, "Vmidp")
label(dx, Y_FOLD - 10, "Vmidp")

# ============ COL-3 : FOLD SINKS MNF_L / MNF_R ============
# MNF_L: NFET at (X_FOLDL, ...). NFET drain top, source bottom.
# We want drain of MNF_L to connect to Vmidn (which sits at X_L = 500 = X_FOLDL).
# Place MNF_L so drain = Y_FOLD and source touches VSS rail.
Y_MNF = Y_VSS - 30 - 60   # leave room (NFET extends ±30 from origin); place so source = VSS
# Actually we want source at VSS rail. NFET source at (x+20, y+30). For source y = Y_VSS:
#   y_origin = Y_VSS - 30
Y_MNF = Y_VSS - 30
nfet(X_FOLDL, Y_MNF, "MNF_L", W=8, L=0.5, nf=4)
dx, dy = nD(X_FOLDL, Y_MNF)
sx, sy = nS(X_FOLDL, Y_MNF)
gx, gy = nG(X_FOLDL, Y_MNF)
# drain up to fold node Vmidn (drain x = X_FOLDL+20; Vmidn wire x = X_L+20 = X_FOLDL+20 ✓)
wire(dx, dy, dx, Y_FOLD, "Vmidn")
wire(sx, sy, sx, Y_VSS, "VSS")
# gate = VN1
wire(gx, gy, X_BIAS + 80, gy, "VN1")
wire(X_BIAS + 80, gy, X_BIAS + 80, -200, "VN1")
wire(X_BIAS + 80, -200, X_BIAS + 20, -200, "VN1")
label(gx - 20, gy, "VN1")

# MNF_R: flip=1 so gate-right, drain at (x-20, y-30); for drain x = X_R-20 = X_FOLDR-20
nfet(X_FOLDR, Y_MNF, "MNF_R", W=8, L=0.5, nf=4, flip=1)
dx, dy = nD(X_FOLDR, Y_MNF, flip=1)
sx, sy = nS(X_FOLDR, Y_MNF, flip=1)
gx, gy = nG(X_FOLDR, Y_MNF, flip=1)
wire(dx, dy, dx, Y_FOLD, "Vmidp")
wire(sx, sy, sx, Y_VSS, "VSS")
wire(gx, gy, gx + 50, gy, "VN1")
label(gx + 20, gy, "VN1")

# ============ COL-4 LEFT : ML_D, MC_D, MNC_D, MN1 (diode) ============
# ML_D: PMOS load, gate=VP1. Source up to VDD.
pfet(X_OUT_L, Y_OUT_PLD, "ML_D", W=20, L=0.5, nf=4)
sx, sy = pS(X_OUT_L, Y_OUT_PLD)
dx_mld, dy_mld = pD(X_OUT_L, Y_OUT_PLD)
gx, gy = pG(X_OUT_L, Y_OUT_PLD)
wire(sx, sy, sx, Y_VDD, "VDD")
wire(gx, gy, gx - 50, gy, "VP1")
label(gx - 20, gy, "VP1")

# MC_D: PMOS cascode, gate=VP2. Source = drain of ML_D.
pfet(X_OUT_L, Y_OUT_PCAS, "MC_D", W=20, L=0.5, nf=4)
sx, sy = pS(X_OUT_L, Y_OUT_PCAS)
dx_mcd, dy_mcd = pD(X_OUT_L, Y_OUT_PCAS)
gx, gy = pG(X_OUT_L, Y_OUT_PCAS)
wire(sx, sy, dx_mld, dy_mld, "n_ml_d_drain")  # ML_D.drain → MC_D.source
wire(gx, gy, gx - 50, gy, "VP2")
label(gx - 20, gy, "VP2")
# Node A = drain of MC_D
label(dx_mcd, dy_mcd - 10, "A")

# MNC_D: NMOS cascode, gate=VN2. Drain at top connects up to Node A.
nfet(X_OUT_L, Y_OUT_NCAS, "MNC_D", W=8, L=0.5, nf=4)
dx_ncd, dy_ncd = nD(X_OUT_L, Y_OUT_NCAS)
sx_ncd, sy_ncd = nS(X_OUT_L, Y_OUT_NCAS)
gx, gy = nG(X_OUT_L, Y_OUT_NCAS)
wire(dx_ncd, dy_ncd, dx_mcd, dy_mcd, "A")    # NMOS cascode drain → Node A
wire(gx, gy, gx - 50, gy, "VN2")
label(gx - 20, gy, "VN2")

# MN1: NMOS diode (mirror diode). Source at VSS.
Y_MN1 = Y_VSS - 30
nfet(X_OUT_L, Y_MN1, "MN1", W=8, L=0.5, nf=4)
dx_n1, dy_n1 = nD(X_OUT_L, Y_MN1)
sx_n1, sy_n1 = nS(X_OUT_L, Y_MN1)
gx_n1, gy_n1 = nG(X_OUT_L, Y_MN1)
wire(dx_n1, dy_n1, sx_ncd, sy_ncd, "Vfold_L")  # MN1.drain → MNC_D.source
wire(sx_n1, sy_n1, sx_n1, Y_VSS, "VSS")
# Diode connect: gate to drain
wire(gx_n1, gy_n1, gx_n1 - 30, gy_n1, "mirror_gate")  # gate stub left
wire(gx_n1 - 30, gy_n1, gx_n1 - 30, dy_n1, "mirror_gate")  # up
wire(gx_n1 - 30, dy_n1, dx_n1, dy_n1, "mirror_gate")  # to drain
# bring Vmidn IN to this fold node (MN1.drain at (X_OUT_L+20, Y_MN1-30) = (1020, 120))
# Wait, Vmidn was routed down to Y_FOLD = -200 at x = X_L+20 = 520
# Now connect Y_FOLD level horizontally to col-4 left fold node.
# Easier: connect Vmidn rail at X_L+20=520, Y_FOLD=-200 horizontally to X_OUT_L+20=1020 at same Y,
# then DOWN to MN1.drain at Y = Y_MN1-30 = 120.
wire(520, Y_FOLD, 1020, Y_FOLD, "Vmidn")
wire(1020, Y_FOLD, 1020, dy_n1, "Vmidn")

# ============ COL-4 RIGHT : ML_O, MC_O, MNC_O, MN2 (mirror) ============
pfet(X_OUT_R, Y_OUT_PLD, "ML_O", W=20, L=0.5, nf=4, flip=1)
sx, sy = pS(X_OUT_R, Y_OUT_PLD, flip=1)
dx_mlo, dy_mlo = pD(X_OUT_R, Y_OUT_PLD, flip=1)
gx, gy = pG(X_OUT_R, Y_OUT_PLD, flip=1)
wire(sx, sy, sx, Y_VDD, "VDD")
wire(gx, gy, gx + 50, gy, "VP1")
label(gx + 20, gy, "VP1")

pfet(X_OUT_R, Y_OUT_PCAS, "MC_O", W=20, L=0.5, nf=4, flip=1)
sx, sy = pS(X_OUT_R, Y_OUT_PCAS, flip=1)
dx_mco, dy_mco = pD(X_OUT_R, Y_OUT_PCAS, flip=1)
gx, gy = pG(X_OUT_R, Y_OUT_PCAS, flip=1)
wire(sx, sy, dx_mlo, dy_mlo, "n_ml_o_drain")
wire(gx, gy, gx + 50, gy, "VP2")
label(gx + 20, gy, "VP2")
label(dx_mco + 10, dy_mco - 10, "Voutp")

nfet(X_OUT_R, Y_OUT_NCAS, "MNC_O", W=8, L=0.5, nf=4, flip=1)
dx_nco, dy_nco = nD(X_OUT_R, Y_OUT_NCAS, flip=1)
sx_nco, sy_nco = nS(X_OUT_R, Y_OUT_NCAS, flip=1)
gx, gy = nG(X_OUT_R, Y_OUT_NCAS, flip=1)
wire(dx_nco, dy_nco, dx_mco, dy_mco, "Voutp")
wire(gx, gy, gx + 50, gy, "VN2")
label(gx + 20, gy, "VN2")

Y_MN2 = Y_VSS - 30
nfet(X_OUT_R, Y_MN2, "MN2", W=8, L=0.5, nf=4, flip=1)
dx_n2, dy_n2 = nD(X_OUT_R, Y_MN2, flip=1)
sx_n2, sy_n2 = nS(X_OUT_R, Y_MN2, flip=1)
gx_n2, gy_n2 = nG(X_OUT_R, Y_MN2, flip=1)
wire(dx_n2, dy_n2, sx_nco, sy_nco, "Vfold_R")
wire(sx_n2, sy_n2, sx_n2, Y_VSS, "VSS")

# *** MIRROR WIRE: MN1.gate → MN2.gate ***
# MN1.gate is at (980, Y_MN1) = (980, 250). MN2.gate is at (1220, Y_MN2) = (1220, 250).
# Already have mirror_gate horizontal stubs. Now connect across.
# MN1 gate stub goes to (gx_n1 - 30, gy_n1) = (950, 250)
# Route at y = 230 (just above source rail) across to MN2.gate stub.
y_mirror_route = Y_VSS + 60   # 340 — below the VSS rail
# Actually below VSS would be off-canvas messy; route at Y_VSS+50.
y_mirror_route = Y_VSS + 50
# From MN1 gate stub down, across, up to MN2 gate.
# MN1 gate is at (980, 250); existing stub goes left to (950, 250). We extend down from (950,250).
wire(950, gy_n1, 950, y_mirror_route, "mirror_gate")
wire(950, y_mirror_route, gx_n2 + 30, y_mirror_route, "mirror_gate")
wire(gx_n2 + 30, y_mirror_route, gx_n2 + 30, gy_n2, "mirror_gate")
wire(gx_n2 + 30, gy_n2, gx_n2, gy_n2, "mirror_gate")

# Vmidp → MN2.drain via horizontal at Y_FOLD then down
wire(680, Y_FOLD, 1180, Y_FOLD, "Vmidp")    # 680 = X_R-20; 1180 = X_OUT_R-20
wire(1180, Y_FOLD, 1180, dy_n2, "Vmidp")

# Load cap at Voutp to VSS
cap(1400, -200, "CL", value="1p")
wire(1400 - 0, -230, dx_mco, dy_mco, "Voutp")
wire(1400, -170, 1400, Y_VSS, "VSS")

# ============================================================================
# Write file
# ============================================================================
header = """v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
"""

with open("folded_cascode_se.sch", "w") as f:
    f.write(header)
    f.write("\n".join(OUT))
    f.write("\n")

print("Wrote folded_cascode_se.sch ({} lines)".format(len(OUT)))
