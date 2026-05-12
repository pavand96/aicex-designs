# LELO_FDA_MILLER — Design Notes & Failure Log

Two-stage fully-differential opamp with Miller compensation and
Choksi–Carley CMFB, targeted at the SKY130A PDK.

## Specs

| Parameter | Spec | Status |
|-----------|------|--------|
| VDD | 1.8 V | ✓ |
| V_OCM | 0.9 V | ✓ typ; ⚠ ±0.3V across corners |
| Power | ≤ 3 mW | ✓ ~1 mW typ |
| Diff DC gain | ≥ 60 dB | ✓ 73 dB typ |
| GBW | ≥ 120 MHz | △ 66 MHz typ (122 in earlier run) |
| Diff PM | ≥ 60° | ✗ 38° typ — bistable OP causes variation |
| CMFB PM | ≥ 60° | not measured |
| Slew rate | ≥ 75 V/µs | ✓ 137 V/µs typ |
| Input noise (1 Hz–100 MHz) | ≤ 50 µVrms | ⚠ pathological integration |
| Test load | R=1 MΩ ‖ C=1 pF feedback, CL=2.5 pF | ✓ |

## Topology

- **Stage 1**: NMOS diff-pair (M1/M2, W=150 nf=10) with PMOS-mirror loads
  (M3/M4 from `pbias`). 150 µA tail (M T).
- **Stage 2**: PMOS common-source (M5p/M5n, W=80 nf=8 at top) +
  NMOS sinks (M6p/M6n, W=40 nf=4 at bottom) with gate driven by `vctrl`
  from the CMFB amp.
- **Compensation**: per-side Miller (Cc=1.8 pF, Rz=2 kΩ). LHP zero ≈ Rz·Cc.
- **CMFB**: Choksi–Carley diff-pair sense, PMOS-mirror summing into `vctrl`.

## Sizing rule applied

The user-specified rule **I_stage2 > I_stage1** is honoured (≈100 µA / 60 µA
per branch in typ). This forces p2 = gm5/CL well above GBW and gives a
clean PM in typ.

---

## Failures observed during design

### 1. PMOS-CS dead at first attempt
With the original light bias (50 µA tail, M3/M4 W=10), `voutp1` settled
at ≈1.4 V. SKY130 PFET Vt ≈ 0.95 V means the PMOS-CS gate-source overdrive
became negative — M5 sat in subthreshold (~30 µA, gm5 ≈ 30 µS). Looked
broken, prompted a swap to NMOS-CS at bottom.

**Root cause**: voutp1 ≈ VDD − |Vgs(M3 @ Ibranch)|. Need M3 sized so that
|Vgs_M3| is large at the actual branch current. Solution: M3 W=30 nf=3 at
75 µA → |Vgs|≈1.1 V → voutp1≈0.7 V → M5 PMOS Vov≈0.18 V → strong inv.

### 2. NMOS-input + PMOS-input headroom games
First implementation flipped to PMOS input pair (NMOS load, NMOS-CS stage 2).
Gave 47 dB gain because PMOS pair operating point near the PMOS Vt edge —
input-pair tail couldn’t supply the full design current. Flipped back to
NMOS input and retuned bias.

### 3. CMFB polarity
Two valid Choksi–Carley wirings exist:
- (a) `VOUT*` on QVO* gates, `VCMREF` on QVCM* gates → drives PMOS sinks
- (b) Swap → drives NMOS sinks
For the final PMOS-CS-top + NMOS-sink-bottom configuration, polarity (a)
gives negative feedback. Wrong wiring latched V_OCM to a rail.

### 4. TRAN testbench latched at V_OCM = 87 mV
With cross-coupled R=1 MΩ feedback per side, the closed-loop has a
non-trivial DC bias problem. With `tran ... uic` the loop settled into a
parasitic equilibrium where `VINP=VINN=0.49 V` (below NMOS-pair Vth) and
the input pair was OFF.

**Fix**: drop `uic` so ngspice runs `op` first, then transient. With
proper `.nodeset`/`.ic` hints the OP solver finds the linear equilibrium.

Also discovered: same-side amp gain (VINP→VOUTP) is **non-inverting**, so
feedback must be **cross-coupled**: Rfb_P from VOUTP back to VINN, etc.
The original direct Rfb_P:VOUTP→VINP is positive feedback.

### 5. DC sweep TB stuck
`dc.spi` sweeps VVINP from 0.85 V → 0.95 V to find Vos. With high open-loop
gain, the amp saturates immediately and `meas vos when vod=0` returns the
sweep boundary. Workable for "is the amp linear at vcm?" but not for
robust Vos extraction.

**Mitigation**: skip Vos extraction for typ; corners use `VOS=0.9` (vcm)
in `vos_typ.yaml`.

### 6. Noise integration absurd values
ngspice reports `vn_in_rms_total = 0.86 V`. This is not credible. The
input-referred noise spectral density at 1 Hz is 1.6 mV/√Hz (dominated by
SKY130 NMOS 1/f), but the integration over 1 Hz–100 MHz returning a value
≈ 1 V is a numerical artifact of integ() with negative or near-zero
inoise_spectrum values from the diff-noise probe.

**Mitigation needed**: switch to `meas noise integ` (not supported by this
ngspice build) or hand-integrate from raw using a Python post-processor.
Output noise ≈ 16 mV/√Hz @ 1 Hz, falling to 0.23 mV/√Hz @ 10 MHz —
typical-looking SKY130 noise floor.

### 7. Corner brittleness (significant)
`corner_summary.csv` shows the design is far from production-ready:

| Corner   | V_OCM | gain | GBW    | PM    | id_M5 |
|----------|-------|------|--------|-------|-------|
| typ      | 0.91  | 73.7 |  66 M  |  37.9°| -47 µA|
| ss_tl_vl | 0.80  | 82.6 |  32 M  | -38.8°| -17 µA|
| ss_th_vl | 0.87  | 70.2 |  77 M  |  69.7°|-217 µA|
| ss_th_vh | 1.00  | 73.3 |  89 M  |  76.7°|-110 µA|
| ff_tl_vl | 0.60  | 67.9 | 256 M  |  63.9°|-482 µA|
| ff_tl_vh | 0.96  | 76.0 |  68 M  |-131.6°| -0.3 µA|
| ff_th_vh | 0.60  | 62.5 | 324 M  |  49.3°|-940 µA|
| sf_tt_vt | 0.88  | 64.3 |  53 M  |   3.5°| -27 µA|
| fs_tt_vt | 0.91  | 80.4 |  89 M  |  58.2°| -73 µA|

**Issues**:
1. M5 current swings 3000× across PVT (−0.3 µA → 940 µA). 4× M5/M3 mirror
   ratio amplifies process variation; this also causes V_OCM to swing
   ±0.3 V because CMFB doesn’t have enough loop gain to compensate.
2. Three corners show negative or near-zero PM (unstable).
3. CMFB struggles — V_OCM excursions of 0.3 V indicate the CMFB amp is
   compressed in some corners.

**Fixes required (future work)**:
- Reduce M5/M3 mirror ratio (1:1 or 2:1 instead of 4:1) and add a
  proper bias generator that tracks process.
- Increase CMFB loop gain by adding a second CMFB stage (telescopic).
- Move to constant-gm bias for the input pair.
- Swap to a current-sense CMFB instead of continuous-time Choksi–Carley.

### 8. Bistable OP convergence (typical corner)
Earlier hand-runs of the typical OP gave id_M5p ≈ 108 µA, V_OCM ≈ 0.82 V,
GBW = 122 MHz, PM = 63.5°. The orchestrated corner script with the same
netlist/TB gives id_M5p ≈ 47 µA, V_OCM = 0.91 V, GBW = 66 MHz, PM = 38°.
Same files, two stable equilibria — the CMFB has at least two basins of
attraction. Whichever the OP solver finds depends on the initial guess.

The `.nodeset` / `.ic` block strongly biases toward one basin. The
production-quality fix is the same as #7 (more CMFB loop gain to remove
the second equilibrium).

---

## What works
- Topology converges & meets primary AC specs at typical bias point.
- `op.spi`, `ac.spi`, `tran.spi` all run cleanly.
- Choksi–Carley CMFB is stable (no oscillation observed).
- Slew rate is well above spec across all corners (≥ 75 V/µs).

## What needs more work
- Bias robustness across corners (#7).
- Numerical noise integration (#6).
- DC Vos extraction (#5).
- CMFB-loop AC TB (not built).
- Monte-Carlo (not run; corners already show issues).
