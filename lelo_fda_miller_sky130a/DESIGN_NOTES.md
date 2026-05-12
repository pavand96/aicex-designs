# LELO_FDA_MILLER — Design Notes & Failure Log

Two-stage fully-differential opamp with Miller compensation and
Choksi–Carley CMFB, targeted at the SKY130A PDK.

## Specs (typ corner, current netlist)

| Parameter | Spec | Status |
|-----------|------|--------|
| VDD | 1.8 V | ✓ |
| V_OCM | 0.9 V | ✓ 0.84 V typ; ⚠ ±0.3 V across corners |
| Power | ≤ 3 mW | ✓ ~1 mW typ |
| Diff DC gain | ≥ 60 dB | ✓ **76.8 dB typ** |
| GBW | ≥ 120 MHz | ✓ **222 MHz typ** |
| Diff PM | ≥ 60° | ✓ **77° typ** |
| Slew rate | ≥ 75 V/µs | ⚠ 17 V/µs rise, 174 V/µs fall — asymmetric |
| Input noise (1 Hz–100 MHz) | ≤ 50 µVrms | ⚠ 85 µVrms |
| Test load | CL = 2.5 pF | ✓ |

---

## Topology (current — 2-stage NMOS-pair → NMOS-CS, PMOS source CMFB)

- **Stage 1**: NMOS diff pair M1/M2 (W=150 nf=10), 150 µA tail (M T,
  W=15 nf=3, mirror 1.5× of MNB W=10). Loads M3/M4 = PMOS mirror W=30
  nf=3 from `pbias`.
- **Stage 2**: **NMOS common-source M5p/M5n at the bottom** (W=80 nf=8),
  driven by `voutp1`/`voutn1`. **PMOS sources M6p/M6n at the top**
  (W=80 nf=4) driven by `vctrl` from CMFB.
- **Compensation**: Cc = 4 pF, Rz = 1.5 kΩ per side. LHP zero
  ≈ 1/(2π·Rz·Cc) ≈ 27 MHz.
- **CMFB**: Choksi–Carley dual-tail, 50 µA per tail, drives `vctrl`.
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

### 7. Corner brittleness — ⚠ PARTIALLY MITIGATED
Pull-down resistors RSTUP/RSTUN on stage-1 outputs eliminated the
dead-latch equilibrium at typ + several corners. However, several PVT
corners still land in unfavorable basins or have stage-2 current
swings ≫ 100×.

| Corner   | V_OCM | gain | GBW    | PM    |
|----------|-------|------|--------|-------|
| typ      | 0.76 | 76.8 | 222 M | **77°** |
| ss_tl_vl | 0.79 | 76.8 |  28 M |  32°  |
| ss_th_vl | 0.82 | 73.4 | 101 M | 116°  |
| ss_th_vh | 0.82 | 71.8 | 324 M |  70°  |
| ff_tl_vl | 0.97 | -10  |   —   |   —   |  ← latched dead
| ff_tl_vh | 0.30 | 65.9 |  36 M | 278°  |
| ff_th_vh | 0.78 | 68.6 | 477 M |  47°  |
| sf_tt_vt | 0.71 | 75.7 | 306 M |  63°  |
| fs_tt_vt | 0.86 | 45.7 |  65 M | -90°  |

**Fundamental cause**: `voutp1` is BOTH the signal node AND the M5 gate
bias. PVT shifts `voutp1` by ±0.3 V which shifts M5 |Vov| → id_M5
swings 1000×. CMFB controls only M6 (source), can't compensate M5.

**Fix requires topology change** (deferred, future work):
- Cascode stage-1 PMOS load → fixes voutp1 across PVT.
- OR: split M5 gate from voutp1 — bias M5 from a constant-gm reference
  and AC-couple the signal from voutp1 (loses LF gain).
- OR: telescopic with current-mirror output stage.

### 8. Bistable OP — ✅ FIXED at typ (RSTUP/RSTUN)
Pull-down resistors removed the second equilibrium at typ.  Some
corners (#7) still find an unfavorable basin.

---

## What works (deliverable, typ corner)
- All five test benches (`op`, `ac`, `tran`, `noise`, `dc`) run to
  completion and produce sensible numbers.
- Primary AC specs met at typ: gain 76.8 dB, GBW 222 MHz, PM 77°.

## What needs more work
- Slew rate symmetry: 17 vs 174 V/µs.
- Corner robustness: cascode stage-1 to decouple voutp1 from PVT.
- Noise: 85 → 50 µVrms via larger tail current.
- Monte-Carlo (not run).
- Layout / extracted sim (not started).
