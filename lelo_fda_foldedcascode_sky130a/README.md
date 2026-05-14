# lelo_fda_foldedcascode_sky130a

Folded-cascode FDA + Sooch wide-swing cascode bias + Choksi-Carley
NMOS-input CMFB, SKY130A, 1.8 V supply.

## Status

Sizing optimized for high gain. **TT corner: 84.7 dB / 55 MHz / 51° PM**.
Hot-corner CMFB latch is a known structural limitation (see below).

## Typical-corner results (Ktt_Tt_Vt, vos = 0.9 V)

| metric  | value    |
|---------|----------|
| V_OCM   | 1.03 V   |
| Avo     | 84.7 dB  |
| GBW     | 55.3 MHz |
| PM      | 50.8°    |

Compared to the original baseline (47 dB / 60 MHz / 81° PM): **+37 dB
DC gain** at the cost of ~10 % GBW and 30° of (excess) phase margin.

## Sizing rationale (current)

| device         | flavor                | L  | W  | nf | role / why these numbers                                |
|----------------|-----------------------|----|----|----|---------------------------------------------------------|
| XM1, XM2       | nfet_01v8             | 2  | 80 | 8  | input pair — L=2 (was 0.5) for 4× ro1                   |
| XM3, XM4       | pfet_01v8_lvt         | 4  | 40 | 8  | PMOS source — L=4 lifts ro3, W=40 halves Cgs at nfp     |
| XM5, XM6       | pfet_01v8_lvt         | 2  | 80 | 8  | PMOS cascode — L=2 enough; L=4 hurts PM via Cdb         |
| XM7, XM8       | nfet_01v8             | 2  | 60 | 6  | NMOS cascode                                            |
| XM9, XM10      | nfet_01v8             | 4  | 20 | 4  | CMFB sink — narrow + high Vov keeps nlowp out of triode |
| XMT (tail)     | nfet_01v8             | 1  | 8  | 2  | 200 µA tail (2× IBIAS = 100 µA)                         |
| XMNB           | nfet_01v8             | 1  | 4  | 1  | IBIAS diode                                             |
| XMPBN/XMPBD    | nfet+pfet_lvt diode   | 2  | 40 | 4  | pbias generator                                         |
| Sooch aux/snk  | as in netlist         |    |    |    | wide-swing cascode bias for pcas/ncas                   |
| CCMC           | 10 pF                 |    |    |    | CMFB compensation cap (was 2 pF)                        |
| RSTUFP/RSTUFN  | 20 MΩ                 |    |    |    | seed leak nfp/nfn → VSS for OP convergence              |

**Vt strategy** (carried over from telescopic OTA work): all PMOS use
the LVT flavor to recover ~500 mV of stack headroom; NMOS use SVT.

## Corner sweep (25 corners, vos = 0.9 V)

**PASS = 16 / 25**, FAIL = 9 / 25.

* **All cold (`*_Tl_*`) corners pass.** 40-76 dB gain, 14-29 MHz GBW,
  62-103° PM.
* **Most typical-temperature (`*_Tt_*`) corners pass** except
  `Kfs_Tt_Vt` (PM < 0).
* **Most hot (`*_Th_*`) corners fail by CMFB latch**:
  V_OUT settles at ~0 V with vctrl ~ 0 V. Only `Kff_Th_Vh` (where the
  PMOS sources are extra strong) escapes the latch.

### CMFB latch (root cause)

The NMOS-input CMFB has **two self-consistent DC equilibria**:

1. **Nominal:** V_OUT ≈ V_OCM, vctrl mid-rail, M9/M10 in saturation.
2. **Latched:** V_OUT = 0 V → QVOP/QVON gates at 0 V → cutoff →
   entire CMFB tail current flows through QVCMP/QVCMN → vctrl pulled
   to 0 V → M9/M10 off → cascode stack starved → V_OUT stays at 0 V.

At hot corners the OP solver lands on equilibrium (2) and there is no
loop gain to escape: this is a **fundamental topology issue, not a
solver artifact**.

### Anti-latch attempts that did NOT work

| attempt                                          | result                                                       |
|--------------------------------------------------|--------------------------------------------------------------|
| 50 MΩ / 100 MΩ / 1 GΩ V_OUT → VCMREF anchor      | either zero effect or kills CMFB DC accuracy (gain –20 dB)   |
| 50 MΩ vctrl → pbias node                         | pbias collapses too at hot corners                           |
| Larger CCMC (2 pF → 10 pF)                       | helps stability but doesn't fix OP degeneracy (kept anyway)  |
| PMOS rail-to-rail helpers (gate=V_OUT,           | wrong polarity — drives V_OUT *toward* 0; positive feedback  |
|   src=VDD, drn=vctrl)                            |                                                              |

### Real fix (out of scope)

A genuine fix requires a CMFB topology change:

* **Rail-to-rail CMFB** (parallel NMOS-input + PMOS-input sense pairs
  summing into the same control node).
* **PMOS-input CMFB** (gate = 0 V puts the sense PMOS strongly ON,
  removing the cutoff equilibrium).
* **Switched-cap CMFB** (deterministic OP, no continuous-time
  degeneracy at all).

## Topology choices (and why)

* NMOS input pair (more gm/I, easier cascode at VDD = 1.8 V).
* PMOS source loads on top, NMOS folded cascode at the output.
* PMOS LVT flavor everywhere PMOS appears (signal & bias) for headroom.
* Sooch wide-swing cascode bias generator: aux device runs at half
  current with quarter (W/L), so its Vov is 2× the main device's,
  putting V_cas at Vt + 2·Vov — cascoded transistor at the edge of
  saturation, no wasted headroom.
* CMFB is also NMOS-input (matches the input pair). 5T-OTA structure
  with PMOS mirror load; mirror output drives the M9/M10 sink gates.

## CMFB polarity (verified at typ)

```
V_OCM up -> I_QVOP+I_QVON up -> diode current up -> mirror current up
         -> vctrl rises -> M9/M10 sink more -> V_OCM falls.   (NFB)
```

## Files

- `work/xsch/LELO_FDA_MILLER.spice` — netlist (subckt name kept as
  `LELO_FDA_MILLER` so the existing testbenches just include it).
- `sim/LELO_FDA_MILLER/{op,ac,tran,noise,dc}.spi` — testbenches.
- `sim/LELO_FDA_MILLER/vos_typ.yaml` — common offset replacement.
- `sim/cicsim.yaml` — corner mapping (K/T/V).
- `tech/` — PDK corner / temp / supply scripts.

## Reproducing

```sh
cd sim/LELO_FDA_MILLER
cicsim run ac Sch Gt Ktt Tt Vt --no-sha --replace vos_typ.yaml
```

Full sweep:

```sh
for K in Ktt Kss Kff Ksf Kfs; do
  for TV in "Tt Vt" "Tl Vl" "Th Vh" "Th Vl" "Tl Vh"; do
    cicsim run ac Sch Gt $K $TV --no-sha --replace vos_typ.yaml
  done
done
```
