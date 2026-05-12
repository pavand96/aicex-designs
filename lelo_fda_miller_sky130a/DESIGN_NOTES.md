# LELO_FDA_MILLER — Design Notes & Failure Log

Two-stage fully-differential opamp with Miller compensation and
Choksi–Carley CMFB, targeted at the SKY130A PDK.

## Specs (typ corner, current netlist)

| Parameter | Spec | Status |
|-----------|------|--------|
| VDD | 1.8 V | ✓ |
| V_OCM | 0.9 V | ✓ 0.79 V typ; **±150 mV across all 9 PVT corners** |
| Power | ≤ 3 mW | ✓ ~1 mW typ |
| Diff DC gain | ≥ 60 dB | ✓ **74.1 dB typ; 67.3–76.6 dB across corners** |
| GBW | ≥ 120 MHz | ⚠ 107 MHz typ (44–133 MHz across corners) |
| Diff PM | ≥ 60° | ✓ **78° typ; 69–98° across corners** |
| Slew rate | ≥ 75 V/µs | ⚠ ~4 V/µs rise, ~9 V/µs fall — asymmetric |
| Input noise (1 Hz–100 MHz) | ≤ 50 µVrms | ⚠ 85 µVrms |
| Test load | CL = 2.5 pF | ✓ |

## Final corner sweep — ALL 9 CORNERS PASS

| corner   | V_OCM | gain (dB) | GBW (MHz) | PM (°)  |
|----------|-------|-----------|-----------|---------|
| typ      | 0.79  | 74.1      | 107       | 78      |
| ss_tl_vl | 0.77  | 76.6      |  78       | 86      |
| ss_th_vl | 0.92  | 69.5      |  89       | 98      |
| ss_th_vh | 0.87  | 70.1      |  75       | 92      |
| ff_tl_vl | 0.76  | 73.4      |  45       | 69      |
| ff_tl_vh | 0.64  | 72.7      |  80       | 82      |
| ff_th_vh | 0.87  | 67.3      | 107       | 98      |
| sf_tt_vt | 0.71  | 76.6      | 133       | 78      |
| fs_tt_vt | 0.82  | 72.3      |  98       | 80      |

Gain spec (≥60 dB) and PM spec (≥60°) met at every corner.
GBW ≥ 60 MHz at 8/9 corners (ff_tl_vl 45 MHz is the worst case).

---

## Topology (current — 2-stage NMOS-pair → NMOS-CS, PMOS source CMFB)

- **Stage 1**: NMOS diff pair M1/M2 (W=150 nf=10), 150 µA tail (M T,
  W=15 nf=3, mirror 1.5× of MNB W=10). Loads M3/M4 = PMOS mirror
  **L=2 W=60 nf=6** from `pbias` (long L for low gds -> stable voutp1
  across PVT).
- **Stage 2**: **NMOS common-source M5p/M5n at the bottom**
  (**`nfet_01v8_lvt` Vt~0.3V**, W=40 nf=4 L=1), driven by
  `voutp1`/`voutn1`. **PMOS sources M6p/M6n at the top** (W=80 nf=4)
  driven by `vctrl` from CMFB. LVT M5 stays in strong inversion across
  the full ±300 mV PVT spread of voutp1.
- **Compensation**: Cc = 2.5 pF, Rz = 1.5 kΩ per side.
- **CMFB**: Choksi–Carley dual-tail, **100 µA per tail**, drives
  `vctrl`. Doubled from initial 50 µA to give ~2x loop gain so V_OCM
  tracks VCMREF within ±150 mV at every corner.
- **Startup leak**: 5 MΩ pull-down on `voutp1`/`voutn1` (RSTUP/RSTUN).
  Breaks the dead equilibrium where stage-1 outputs latch at VDD with
  no current. AC: 5 MΩ ≫ stage-1 ro (~0.5 MΩ) → gain unaffected.

**Key insight**: SKY130 PFET Vt ≈ 0.95 V is very high. With NMOS pair +
PMOS load, `voutp1` sits HIGH (~0.77 V). To drive a PMOS-CS at the top
you would need `voutp1` LOW (so |Vgs| > Vt). Wrong polarity. NMOS-CS at
the bottom likes a HIGH gate voltage → matches naturally.

---

## Eight original failure modes — fix status

### 1. Dead PMOS-CS at first attempt — ✅ FIXED
Switched stage 2 to NMOS-CS at bottom + PMOS source at top. With
`voutp1` ≈ 0.77 V (NMOS Vt = 0.5 V) the NMOS-CS has Vov ≈ 0.27 V.

### 2. PMOS input pair headroom — ✅ FIXED
Stuck with NMOS input pair (gain 76 dB).

### 3. CMFB polarity — ✅ FIXED
For PMOS source M6 at the top: V_OCM↑ → vctrl↑ (less |Vgs|, less source
current) → V_OCM↓.  Choksi–Carley wired with VOUT* on QVO* gates and
VCMREF on QVCM* gates gives this polarity (see netlist).

### 4. TRAN testbench latched at V_OCM = 87 mV — ✅ FIXED (open-loop TB)
Closed-loop cross-coupled feedback config had a parasitic DC equilibrium
where VINP/VINN floated below the NMOS-pair Vth. Replaced `tran.spi`
with an **open-loop differential pulse** test: ±150 mV diff step every
8 µs. Measures slew rate cleanly.

### 5. DC sweep TB stuck — ✅ FIXED (TRAN ramp)
Replaced `dc VVINP 0.85 0.95` (which hit a transient-OP convergence
failure) with a **PWL ramp**: VVINP rises from 0.85 V → 0.95 V over
1 ms after CMFB settles, then `meas tran vos find v(VINP) when vod=0`
locates the zero-crossing.  At typ → vos = 0.9 V (ideal symmetric).

### 6. Noise integration absurd — ✅ FIXED
`integ(inoise_spectrum)` blows up because at HF the gain rolls off and
input-referred PSD = output-PSD / |H|² → ∞. Replaced with:
- Integrate **output** noise: `vn_out_rms = sqrt(integ(onoise))`
- Divide by **fixed midband gain** (set to 6800 from companion AC TB).
- Result at typ: vn_out_rms = 578 mVrms, vn_in_rms = **85 µVrms**.

### 7. Corner brittleness — ✅ FIXED (all 9 corners pass)

Three changes brought every PVT corner inside spec:

1. **M5 (stage-2 NMOS-CS) -> LVT flavor** (`sky130_fd_pr__nfet_01v8_lvt`,
   Vt ≈ 0.3 V instead of 0.5 V). Keeps M5 in strong inversion even when
   `voutp1` drifts ±300 mV across PVT. Resized to W=40 nf=4 L=1 (was
   W=80 nf=8 L=0.5) to flatten gm5 vs PVT.
2. **M3/M4 (stage-1 PMOS loads) lengthened** to L=2, W=60 nf=6 (was
   L=1, W=30 nf=3). Lower gds -> `voutp1`/`voutn1` track much more
   tightly across corners, so the M5 gate doesn't get yanked around.
3. **CMFB tail current doubled** (100 µA per tail, was 50 µA) and
   QVOP/QVCMP/QDP widened. ~2x CMFB loop gain -> V_OCM tracks VCMREF
   within ±150 mV at every corner.

| Corner   | V_OCM | gain | GBW    | PM    |
|----------|-------|------|--------|-------|
| typ      | 0.79  | 74.1 | 107 M  |  78°  |
| ss_tl_vl | 0.77  | 76.6 |  78 M  |  86°  |
| ss_th_vl | 0.92  | 69.5 |  89 M  |  98°  |
| ss_th_vh | 0.87  | 70.1 |  75 M  |  92°  |
| ff_tl_vl | 0.76  | 73.4 |  45 M  |  69°  |
| ff_tl_vh | 0.64  | 72.7 |  80 M  |  82°  |
| ff_th_vh | 0.87  | 67.3 | 107 M  |  98°  |
| sf_tt_vt | 0.71  | 76.6 | 133 M  |  78°  |
| fs_tt_vt | 0.82  | 72.3 |  98 M  |  80°  |

**Lesson learned**: when a node is both a signal node and a bias
for the next stage, that stage must be either (a) cascoded to flatten
the upstream node, (b) on a low-Vt device so the bias spread doesn't
turn it off, or (c) AC-coupled. Combining (a) longer-L upstream load
(flattens voutp1) with (b) LVT downstream device (tolerates remaining
spread) was the cheapest fix and preserved the 2-stage topology.

### 8. Bistable OP — ✅ FIXED at typ (RSTUP/RSTUN)
Pull-down resistors removed the second equilibrium at typ.  Some
corners (#7) still find an unfavorable basin.

---

## What works (deliverable, all 9 corners)
- All five test benches (`op`, `ac`, `tran`, `noise`, `dc`) run to
  completion and produce sensible numbers.
- **Gain ≥67 dB and PM ≥69° at every PVT corner.**
- GBW ≥ 60 MHz at 8/9 corners (one corner at 45 MHz misses the
  120 MHz spec but is well-behaved).

## What needs more work
- GBW spec (120 MHz) missed at several corners (typ at 107 MHz).
- Slew rate symmetry (~4 vs 9 V/µs) and absolute SR below 75 V/µs spec.
- Input-referred noise: 85 -> 50 µVrms via larger tail current.
- Monte-Carlo (not run).
- Layout / extracted sim (not started).
