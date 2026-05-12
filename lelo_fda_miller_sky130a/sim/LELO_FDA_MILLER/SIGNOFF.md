# LELO FDA Miller Sign-Off

Date: 2026-05-12
Scope: Final available simulation data from current run artifacts.

## Final Operating Points

| Operating Point | IBIAS (uA) | Power (mW) | Gain (dB, typ) | GBW (MHz, typ) | PM (deg, typ) | SR Rise (V/us) | SR Fall (V/us) | Input-Referred Noise RMS (uV) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Nominal sign-off | 100 | 0.5472 | 74.31 | 144.10 | 64.04 | 3.376 | 7.701 | 155.5 |
| Max slew under 3 mW | 900 | 2.1700 | - | - | - | 673.7 | 643.5 | 183.3 |
| Min noise in sweep | 250 | 1.1620 | - | - | - | 159.8 | 312.6 | 77.89 |

## PVT Snapshot (100 uA)

| Metric | Value |
|---|---:|
| Gain range across 9 corners (dB) | 67.67 to 76.78 |
| GBW range across 9 corners (MHz) | 34.37 to 198.48 |
| PM range across 9 corners (deg) | 57.06 to 79.82 |
| Worst PM corner | sf_tt_vt (57.06 deg) |
| Worst GBW corner | ff_tl_vl (34.37 MHz) |

## Sign-Off Statement

Design meets gain and power targets at nominal conditions, with selectable high-slew (900 uA) and lower-noise (250 uA) operating modes under the 3 mW budget. Worst-case stability remains at sf_tt_vt.
