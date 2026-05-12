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
- **Noise**: ngspice noise analysis with `tran 10n 200u uic` + `op` preamble
  to settle CMFB before linearization. Spectra are in V/√Hz (ASD);
  integrated RMS = √(∫ ASD² df) over 1 Hz – 100 MHz.
  The `inoise_spectrum` is correctly input-referred by ngspice when using
  a single AC source on VVINP with `ac 0.5` (and `ac -0.5` on VVINN).

## Typical Corner Results (Sch Gt Ktt Tt Vt, IBIAS = 100 µA)

| Parameter | Value |
|-----------|-------|
| DC Gain | 74.3 dB |
| GBW | 144.1 MHz |
| Phase Margin | 64.0° |
| f3dB | 20.0 kHz |
| SR (differential, rising) | 70 V/µs (35 V/µs per output) |
| Input-ref noise @ 1 Hz | 2503 nV/√Hz (1/f) |
| Input-ref noise @ 1 kHz | 137 nV/√Hz |
| Input-ref noise @ 10 kHz | 52.5 nV/√Hz |
| Input-ref noise @ 100 kHz | 20.8 nV/√Hz |
| Input-ref noise @ 10 MHz | 6.9 nV/√Hz (thermal floor) |
| Integrated noise (1 Hz – 100 MHz) | **78.9 µVrms** |
| Noise spec | < 50 µVrms (**FAIL — 58% over**) |
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

## Noise PVT Corner Sweep

| Corner | en,in @ 1 kHz (nV/√Hz) | Integrated (µVrms) | Notes |
|--------|------------------------|--------------------|-------|
| TT typ | 137 | 78.9 | ✓ reliable |
| FF hot high | 1921 | 220.2 | ⚠ OP convergence issues |
| SS cold low | 11187 | 911.4 | ⚠ OP convergence issues |
| SF typ | 132 | 75.6 | ✓ reliable |
| FS typ | 142 | 82.1 | ✓ reliable |

- FF and SS corners have OP convergence warnings (source stepping failed);
  noise values at those corners are unreliable and inflated.
- At reliable corners (TT, SF, FS): 75.6 – 82.1 µVrms, consistently above
  50 µVrms spec. Dominated by 1/f noise in the NMOS input pair.

## Sign-Off Statement

Design meets gain, GBW, and SR targets at all tested corners.
PM at sf_tt_vt is marginally below 60° spec (57.1°).
SR is now physically consistent across corners and matches analytical
prediction (I_tail / Cc).

**Noise: FAIL.** Integrated input-referred noise (1 Hz – 100 MHz) is
78.9 µVrms at typical corner vs 50 µVrms spec. The excess is dominated
by 1/f noise in the SKY130 NMOS input pair. Mitigation options:
  - Increase input pair W/L to reduce 1/f corner frequency
  - Switch to PMOS input pair (lower 1/f in SKY130)
  - Add chopping or CDS

IBIAS sweep not included (requires re-running with corrected benches).
