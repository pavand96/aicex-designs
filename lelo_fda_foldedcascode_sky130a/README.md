# lelo_fda_foldedcascode_sky130a

Folded-cascode FDA + Choksi-Carley CMFB, SKY130A.

## Status: WORK IN PROGRESS

A folded-cascode FDA with a Sooch wide-swing cascode bias generator
and a Choksi-Carley NMOS-input CMFB is in place. The typical corner
hits ~47 dB / 60 MHz / 81° PM, but the CMFB latches at the slow-hot
corners and one or two extreme corners.

## Typical-corner results

| metric  | value     |
|---------|-----------|
| V_OCM   | 0.90 V    |
| Gain    | 47 dB     |
| GBW     | 61 MHz    |
| PM      | 81°       |

## Corner sweep summary

3 corners pass cleanly (typ, sf_tt_vt, fs_tt_vt). 2 corners
(ff_tl_vl, ff_tl_vh) get the bias right but fall short on gain.
4 corners fail because the CMFB latches the output at one of two
self-consistent equilibria (V_OCM ~ 0.1 V or ~ 1.08 V).

| corner   | gain (dB) | GBW    | V_OCM | note          |
|----------|-----------|--------|-------|---------------|
| typ      | 47        | 61M    | 0.90  | OK            |
| sf_tt_vt | 62        | 81M    | 0.87  | OK            |
| fs_tt_vt | 59        | 56M    | 0.82  | OK            |
| ff_tl_vl | 34        | 20M    | 0.77  | low gain      |
| ff_tl_vh | 31        |  9M    | 0.85  | low gain      |
| ss_tl_vl | DEAD      | -      | 0.83  | input pair off |
| ss_th_vl |  2        | 12M    | 0.11  | CMFB latched low |
| ss_th_vh |  2        | 12M    | 1.08  | CMFB latched high |
| ff_th_vh |  2        | 12M    | 1.08  | CMFB latched high |

## Known issues / next steps

1. **CMFB dual equilibrium / startup latch** — the cascode column
   has two DC solutions: nominal (all devices saturated) and a
   degenerate one with M5/M7 in triode and V_OCM at one of the rails.
   At slow-hot corners the OP solver lands on the degenerate one and
   the CMFB cannot pull out (its loop gain is small in that regime).
   A startup circuit, or a CMFB driving the PMOS source mirror
   (instead of the NMOS sink), is needed to guarantee the nominal
   equilibrium.

2. **Slow-corner input pair off** — at ss_tl_vl the NMOS tail bias
   (mirrored from a 25 uA reference) drops too far. Either widen
   the mirror or use a constant-gm bias generator.

3. **Headroom at fast corners** — at ff_tl_vh and ff_th_vh the
   PMOS source over-delivers and the CMFB saturates trying to
   compensate. Adding a second NMOS cascode layer would give the
   sink more authority.

## Topology choices (and why)

* NMOS input pair (more gm/I, lower 1/f below the chopper, easier
  cascode stack at VDD = 1.8 V).
* PMOS source loads on top, NMOS folded cascode at the output.
* PMOS LVT flavor everywhere PMOS is used, to recover Vt headroom.
* Sooch wide-swing cascode bias generator: the auxiliary device runs
  at half current with quarter (W/L), so its Vov is 2x the main
  device's, putting V_cas at Vt + 2*Vov — the cascoded transistor sits
  exactly at the edge of saturation, with no wasted headroom.
* CMFB is also NMOS-input (matches the input pair). The 5T-OTA
  structure has the NMOS pair source on a NMOS tail to VSS and a
  PMOS current-mirror load at VDD; the mirror output drives the
  M9/M10 sink gates.

## Polarity derivation (CMFB)

The CMFB diff pair has VOUTP/VOUTN on the diode side of the PMOS load
and VCMREF on the mirror side, so:

```
V_OCM up -> I_QVOP+I_QVON up -> diode current up -> mirror current up
         -> vctrl rises -> M9/M10 sink more -> V_OCM falls.
```

Negative feedback. Verified at typ.

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
