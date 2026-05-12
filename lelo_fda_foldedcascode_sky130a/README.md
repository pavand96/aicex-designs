# lelo_fda_foldedcascode_sky130a

Folded-cascode FDA + Choksi-Carley CMFB, SKY130A.

## Status: WORK IN PROGRESS

A first iteration of a folded-cascode topology is in place. The circuit
biases up cleanly and small-signal-AC simulates at the typical corner,
but the gain target and corner robustness are not yet met. See
`sim/LELO_FDA_MILLER/corner_summary.csv` for the corner sweep.

## Typical-corner results

| metric  | value     |
|---------|-----------|
| V_OCM   | 0.90 V    |
| Gain    | ~43 dB    |
| GBW     | ~80 MHz   |
| PM      | ~81°      |
| Power   | ~3 mW @ 1.8 V |

## Corner sweep summary

Only 4 of 9 corners produce sensible AC results today:

| corner   | gain (dB) | GBW    | V_OCM | note          |
|----------|-----------|--------|-------|---------------|
| typ      | 43        | 80M    | 0.90  | OK            |
| ff_tl_vl | 38        | 35M    | 0.67  | OK            |
| ff_tl_vh | 53        | 37M    | 1.72  | V_OCM high    |
| fs_tt_vt | 37        | 65M    | 0.66  | OK            |
| ss_tl_vl | -82       | -      | 0.42  | DEAD          |
| ss_th_vl | 4         | 13M    | 0.22  | broken        |
| ss_th_vh | 4         | 14M    | 1.09  | broken        |
| ff_th_vh | 3         | 11M    | 1.09  | broken        |
| sf_tt_vt | -180      | -      | 0.89  | DEAD          |

## Known issues / next steps

1. **Cascode bias drift across PVT** — the simple stacked-PMOS bias
   generator for `pcas` (and the pbias-sourced `ncas`) does not track
   PVT well. At slow corners or low VDD the cascode gates collapse and
   the high-impedance node loses its operating point. Replace with a
   wide-swing Sooch cascode bias generator.

2. **CMFB strength** — at ss corners V_OCM drifts >100 mV. The CMFB
   tail/gm ratio needs to be increased (or the output sinks made
   weaker so vctrl has more authority).

3. **Output Rds** — typical-corner gain at 43 dB is below the 60 dB
   target. Both rds_M3 (PMOS source) and rds_M9 (NMOS CMFB sink) are
   the limiters. Either bump L further or add a second cascode layer
   on the NMOS side.

## Files

- `work/xsch/LELO_FDA_MILLER.spice` — netlist (subckt name kept as
  `LELO_FDA_MILLER` so the existing testbenches just include it).
- `sim/LELO_FDA_MILLER/{op,ac,tran,noise,dc}.spi` — testbenches.
- `sim/LELO_FDA_MILLER/run_corners.py` — corner driver.
- `sim/LELO_FDA_MILLER/corner_summary.csv` — last sweep results.

## Topology

```
VDD ─┬──── M3 ─┬── nfp ──┬── M5 (PMOS cascode, gate=pcas) ──┐
     │        │          │                                  │
     │ pbias  │          │       M1 (NMOS input, VINP)      ▼
     │ diode  │          ├────── M1.drain                  VOUTP
     │ MPBD   │          │       │                          ▲
     │        │          │       │                          │
     │ MPBN  M4 (sym) ── nfn ── M2 (NMOS, VINN)             │
     │ pulls │                   ntail                       │
     │ pbias │                   │                           │
     │       │                   XMT (NMOS tail, gate=IBIAS) │
     │       │                   │                           │
     │       │                  VSS                          │
     │       │                                               │
     │       │      M7 (NMOS cascode, gate=ncas) ────────────┤
     │       │      │                                        │
     │       │      nlowp                                    │
     │       │      │                                        │
     │       │      M9 (NMOS sink, gate=vctrl from CMFB)    M10
     │       │      │                                        │
VSS ─┴───────┴──────┴────────────────────────────────────────┘
```

Devices that use the LVT flavor (`sky130_fd_pr__pfet_01v8_lvt`):
all PMOS in the signal path and bias generators, to give enough Vt
headroom on the PMOS side.
