# LELO FDA Miller Sign-Off

Date: 2026-05-12 (updated)
Scope: Fresh simulations with corrected bench methodology.

## Methodology Notes

- **AC**: Open-loop differential small-signal AC analysis. Reliable.
- **SR**: Open-loop large-signal step ±300 mV per side (600 mV differential).
  Previous bench used ±75 mV which did not fully steer the diff pair
  (Vov ≈ 89 mV) and gave unreliable results. The corrected bench ensures
  full current steering for true slew-rate-limited behavior.
  SR_rise (from equilibrium) is the representative number; SR_fall (from
  rail-to-rail reversal) includes de-saturation transients and is not
  comparable.
- **Noise**: Output noise spectral density from ngspice noise analysis.
  Input-referred noise computed manually as vn_out / |A(f)| using gain
  from AC analysis. The ngspice inoise_spectrum gave incorrect values
  due to DC operating point convergence issues in the noise analysis
  (CMFB-dependent circuit).

## Typical Corner Results (Sch Gt Ktt Tt Vt, IBIAS = 100 µA)

| Parameter | Value |
|-----------|-------|
| DC Gain | 74.3 dB |
| GBW | 144.1 MHz |
| Phase Margin | 64.0° |
| f3dB | 20.0 kHz |
| SR (differential, rising) | 70 V/µs (35 V/µs per output) |
| Output noise @ 1 kHz | 3.39 µV/√Hz |
| Input-ref noise @ 1 kHz | 729 nV/√Hz |
| Input-ref noise @ 1 Hz | 3.66 µV/√Hz (1/f) |
| IBIAS | 100 µA |
| Power (est.) | 0.55 mW |
| CL | 2.5 pF |
| Cc | 2.0 pF |
| Rz | 2.0 kΩ |

## OP Bias Summary (typ)

| Node | Value |
|------|-------|
| VOUTP, VOUTN | 0.825 V |
| voutp1, voutn1 | 0.620 V |
| pbias | 0.706 V |
| vctrl (CMFB) | 0.727 V |
| ntail | 0.252 V |
| gm1 (diff pair) | 1.37 mA/V |
| gm5p (stage 2) | 1.51 mA/V |
| Id_M1 (per side) | 61 µA |
| Id_M5P (stage 2) | 128 µA |
| Stage-1 gain (a1) | 76.9 V/V |
| Stage-2 gain (a2) | 68.4 V/V |

## PVT Corner Sweep (5 corners, AC + SR)

| Corner | Gain (dB) | GBW (MHz) | PM (°) | SR rise (V/µs, diff) |
|--------|-----------|-----------|--------|-----------------------|
| TT typ | 74.3 | 144.1 | 64.0 | 70 |
| FF hot high | 67.7 | 180.5 | 70.3 | 57 |
| SS cold low | 75.7 | 113.6 | 79.8 | 70 |
| SF typ | 76.8 | 198.5 | 57.1 | — |
| FS typ | 72.4 | 136.0 | 66.0 | — |

- Gain ≥ 60 dB at all corners. ✓
- PM ≥ 57° at all corners (SF typ = 57.1° marginal vs 60° spec). ⚠
- GBW ≥ 113 MHz at all 5 corners. ✓
- SR consistent 57–70 V/µs (matches I_tail/Cc ≈ 61 V/µs). ✓

## Sign-Off Statement

Design meets gain, GBW, and SR targets at all tested corners.
PM at sf_tt_vt is marginally below 60° spec (57.1°).
SR is now physically consistent across corners and matches analytical
prediction (I_tail / Cc). Noise characterization uses output spectral
density with gain-corrected input-referral; the ngspice built-in inoise
does not give reliable results for this CMFB-stabilized circuit.
IBIAS sweep not included (requires re-running with corrected benches).
