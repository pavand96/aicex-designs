"""
beta-multiplier (constant-gm) self-biased reference for the 0.9V PMOS-input
folded cascode. Signal path UNTOUCHED — this sketch only shows the new
bias generator that replaces the IBIAS-fed PMOS-diode + NMOS-diode chain.

Why beta-mult:
  - Single resistor sets I_REF; current is ~ 2/(mu_n*Cox*(W/L)*(1-1/sqrt(K))^2 / R^2)
  - Both PMOS-mirror branch (-> VBP, tail) AND NMOS-mirror branch (-> VBIAS3, sinks)
    are forced to the SAME I, by construction, regardless of corner.
  - Removes the fs/sf "mirror catastrophe" where pfet-strong+nfet-weak
    (or vice versa) made tail current and sink current diverge.
  - Needs a startup kick (small leak transistor) to avoid the zero-current
    degenerate equilibrium.

Topology (left to right):
   +-------+ VDD +-------------+----------+
   |              |             |          |
  MP_S1(diode)   MP_B(K:1)     MP_VB     MP_B2  ... (mirror fan-out -> VBP)
   |              |             |          |
   o-VBP----------+----+        |          |
   |                   |        |          |
  MN_A             MN_B  (K:1)  |          |
  (W/L)            (KW/L)       |          |
   |                   |        |          |
   |                  R_BM      |          |
   |                   |        |          |
   +---o VBIAS3 -------+---+    +---NMOS diode -> VBIAS3 fan-out
                           |
                          VSS

  Startup: tiny pfet from VDD to VBIAS3, killed once loop is alive
           (or just a 1G leak resistor in sim).

Reading: I = 2/(mu_n Cox (W/L)_A R^2) * (1 - 1/sqrt(K))^2
  Pick K=4, (W/L)_A small (W=4 L=2 nf=2), target I=10uA
  -> R ~ 100 kOhm range on sky130. Use 80k as a starting point.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mp

fig, ax = plt.subplots(figsize=(11, 8))
ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis('off')

# rails
ax.plot([0.5, 11.5], [9.2, 9.2], 'k', lw=2)
ax.text(0.2, 9.3, 'VDD', fontsize=11, fontweight='bold')
ax.plot([0.5, 11.5], [0.6, 0.6], 'k', lw=2)
ax.text(0.2, 0.3, 'VSS', fontsize=11, fontweight='bold')

def box(x, y, w, h, label, sub=''):
    ax.add_patch(mp.Rectangle((x, y), w, h, fc='#eef', ec='k', lw=1.2))
    ax.text(x+w/2, y+h/2+0.15, label, ha='center', va='center', fontsize=9, fontweight='bold')
    if sub:
        ax.text(x+w/2, y+h/2-0.25, sub, ha='center', va='center', fontsize=7)

def wire(p, q):
    ax.plot([p[0], q[0]], [p[1], q[1]], 'k', lw=1.1)

def node(p, name, dx=0.15, dy=0.15, color='red'):
    ax.plot(*p, 'o', color=color, ms=4)
    ax.text(p[0]+dx, p[1]+dy, name, fontsize=8, color=color)

# ===================== beta-mult core =====================
# Branch A: PMOS diode MP_S1 on top, NMOS MN_A on bottom (1x). Sets VBP.
# Branch B: PMOS MP_S2 (K mirror of MP_S1, K=4) on top, NMOS MN_B (K x W/L)
#          bottom in series with R_BM. Diode connection on NMOS B sets VBIAS3.

# branch A (x=2)
box(1.6, 7.4, 0.8, 1.0, 'MP_S1', 'diode\nW=8 L=1\nnf=4')
box(1.6, 2.4, 0.8, 1.0, 'MN_A',  'W=4 L=2\nnf=2')
wire((2.0, 9.2),(2.0, 8.4))            # VDD -> MP_S1
wire((2.0, 7.4),(2.0, 3.4))            # drain stack
wire((2.0, 2.4),(2.0, 0.6))            # MN_A -> VSS
node((2.0, 7.4), 'VBP', dx=-1.1, dy=-0.1)  # VBP is drain/gate of MP_S1
node((2.0, 3.4), 'VBIAS3', dx=-1.7, dy=0)  # diode tie of MN_A

# branch B (x=4.5)
box(4.1, 7.4, 0.8, 1.0, 'MP_S2', 'K=4 mirror\nW=32 L=1')
box(4.1, 2.4, 0.8, 1.0, 'MN_B',  'KxW/L\nW=16 L=2')
ax.add_patch(mp.Rectangle((4.4, 1.1), 0.2, 1.0, fc='w', ec='k', lw=1.2))  # resistor
ax.text(5.4, 1.6, 'R_BM ~ 80k', fontsize=9)
wire((4.5, 9.2),(4.5, 8.4))
wire((4.5, 7.4),(4.5, 3.4))
wire((4.5, 2.4),(4.5, 2.1))            # MN_B src -> R top
wire((4.5, 1.1),(4.5, 0.6))            # R bot -> VSS

# gate ties: MP_S1 gate <- MP_S2 drain? No: MP_S1 diode, gate=drain=VBP.
# MP_S2 gate <- VBP (mirror).
wire((1.6, 7.9),(1.2, 7.9)); wire((1.2, 7.9),(1.2, 6.7))
wire((4.1, 7.9),(1.2, 7.9))            # both PMOS gates to VBP
node((1.2, 6.7),'VBP_gate', dx=-1.0, dy=-0.3, color='blue')

# MN_A diode (gate=drain) at VBIAS3
wire((1.6, 2.9),(1.2, 2.9)); wire((1.2, 2.9),(1.2, 3.4)); wire((1.2, 3.4),(2.0,3.4))
# MN_B gate also at VBIAS3 (mirror)
wire((4.1, 2.9),(3.7, 2.9)); wire((3.7, 2.9),(3.7, 3.4)); wire((3.7, 3.4),(2.0,3.4))

# Startup leak (1G in sim, tiny pfet in silicon)
ax.add_patch(mp.Rectangle((5.5, 5.0), 0.2, 0.8, fc='w', ec='k', lw=1.2))
ax.text(5.85, 5.4, 'R_START 1G (sim only)\nor startup pFET', fontsize=8)
wire((5.6, 5.8),(5.6, 9.2))
wire((5.6, 5.0),(5.6, 3.4)); wire((5.6, 3.4),(2.0, 3.4))

# ===================== mirror fan-out =====================
ax.text(7.5, 8.7, 'Fan-out (gates from VBP / VBIAS3)', fontsize=9, fontweight='bold')

# VBP -> tail mirror MP_TAIL (m=4) gating signal-path tail
box(7.2, 7.4, 0.9, 1.0, 'M_TAIL', 'g=VBP\nm=4 -> 40uA')
wire((7.65, 9.2),(7.65, 8.4))
wire((6.8, 7.9),(7.2, 7.9))            # gate from VBP bus
node((6.8, 7.9),'VBP bus', dx=-0.7, dy=-0.3, color='blue')
ax.annotate('', xy=(7.65, 6.7), xytext=(7.65, 7.4),
            arrowprops=dict(arrowstyle='->', lw=1.2))
ax.text(7.8, 6.8, '-> ntail (signal path)', fontsize=8)

# VBP -> PMOS sources for VBIAS1 and VBIAS2 ref columns
box(8.6, 7.4, 0.9, 1.0, 'MP_B2', 'g=VBP\n10uA')
wire((9.05, 9.2),(9.05, 8.4))
wire((8.0, 7.9),(8.6, 7.9))
box(8.6, 5.6, 0.9, 1.0, 'MN_B2', 'L=2 W=4 (1/4 aspect)\ndiode -> VBIAS2')
wire((9.05, 7.4),(9.05, 6.6))
wire((9.05, 5.6),(9.05, 0.6))
node((9.05, 6.6),'VBIAS2', dx=0.15, dy=0.1)

box(10.1, 7.4, 0.9, 1.0, 'MP_B1', 'diode 1/4 aspect\nL=4 W=16')
wire((10.55, 9.2),(10.55, 8.4))
node((10.55, 7.4),'VBIAS1', dx=0.15, dy=-0.2)
box(10.1, 5.6, 0.9, 1.0, 'MN_B1', 'g=VBIAS3\n10uA sink')
wire((10.55, 7.4),(10.55, 6.6))
wire((10.55, 5.6),(10.55, 0.6))
wire((6.5, 3.4),(6.5, 6.1)); wire((6.5, 6.1),(10.1, 6.1))
node((6.5, 3.4),'VBIAS3 bus', dx=0.15, dy=-0.3)

# VBIAS3 -> NMOS sink mirrors (M11/M12 in signal path)
box(7.2, 1.4, 0.9, 1.0, 'M11/M12', 'g=VBIAS3\nm=4 -> 40uA each')
wire((7.65, 0.6),(7.65, 1.4))
wire((6.5, 1.9),(7.2, 1.9))
ax.annotate('', xy=(7.65, 3.1), xytext=(7.65, 2.4),
            arrowprops=dict(arrowstyle='->', lw=1.2))
ax.text(7.8, 2.7, '-> nbL / nbR (signal path)', fontsize=8)

# Title and notes
ax.text(6, 9.7,
        'Beta-multiplier (constant-gm) bias replacing diode/diode chain  -- VDD=0.9V',
        ha='center', fontsize=12, fontweight='bold')
ax.text(0.4, 0.1,
        'I_REF = (2/(mu_n Cox (W/L)_A R^2)) * (1 - 1/sqrt(K))^2,  K=4 -> match factor 1/2',
        fontsize=8)

plt.tight_layout()
plt.savefig('/home/pavand96/pro/aicex_designs/lelo_fc_se_pmos_sky130a/sketch_beta_mult.png',
            dpi=110, bbox_inches='tight')
print('wrote sketch_beta_mult.png')
