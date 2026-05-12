# LELO_TWO_STAGE_MILLER — Two-Stage Miller-Compensated Opamp

Classic textbook two-stage Miller-compensated opamp on **SKY130A**, sized for **≥ 60 dB DC gain** with **≥ 60° phase margin** and the **maximum gain-bandwidth (GBW)** that the compensation budget allows.

## Topology

```
                       VDD
                        │
        ┌───────┬───────┤
        │       │       │
       MI3     MI4     M5
       (n1)   (vout1)  (VOUT)──┬────── output
        │       │              │
        ├───────┘              │
        │                      │
        M1      M2             M6 ── gated by IBIAS
        ││      ││             │
       VINP    VINN            │
        │└─tail─┘              │
        │   │                  │
        │   MT ── gated by IBIAS
        │   │                  │
       VSS  VSS               VSS

   Miller compensation: vout1 ──RZ── ncc ──CC── VOUT
   Bias:    IBIAS pin → MNB (NMOS diode) sets all NMOS gates
            → vbiasp (= drain of M3 mirror) sets all PMOS gates
```

- **Stage 1**: NMOS diff pair `M1/M2` + PMOS current-mirror load `M3/M4` (gain ≈ gm1 / (gds2+gds4))
- **Stage 2**: PMOS common-source `M5` + NMOS current source `M6` (gain ≈ gm5 / (gds5+gds6))
- **Compensation**: Miller cap `Cc = 2 pF` + nulling resistor `Rz = 1.6 kΩ` ≈ 1/gm5 to push the RHP zero into the LHP and gain phase margin
- **Bias**: external 10 µA reference → on-chip NMOS diode → 1:N mirrors

**Subckt pinout**: `VSS VDD VOUT IBIAS VINP VINN`
**Polarity note**: open-loop transfer `VOUT/VINP` is **inverting** (DC phase = 180°). For closed-loop use, `VINP` is the **inverting** input and `VINN` the **non-inverting** input.

## Sizing (typical, tt corner, 27 °C, 1.8 V)

| Device | Type | W (µm) | L (µm) | Role |
|---|---|---|---|---|
| MNB    | NFET |  4 | 2 | Reference diode at IBIAS pin |
| MT     | NFET |  8 | 2 | Stage-1 tail (1:2 mirror → 20 µA) |
| M1, M2 | NFET | 20 | 1 | Input diff pair (10 µA per branch) |
| M3, M4 | PFET | 10 | 2 | Stage-1 PMOS mirror load |
| M5     | PFET | 80 | 2 | Stage-2 PMOS CS (8:1 mirror → ≈ 80 µA) |
| M6     | NFET | 32 | 2 | Stage-2 NMOS current source (8:1 from MNB) |
| Cc     | C    |  – | – | 2 pF Miller cap |
| Rz     | R    |  – | – | 1.6 kΩ nulling resistor |

## Operating point

| Quantity | Value |
|---|---|
| External reference `IBIAS` | 10 µA |
| Stage-1 tail current | 20 µA |
| Stage-1 branch current | 10 µA |
| Stage-2 current (M5/M6) | 93 µA |
| Total `IDD` | ≈ 113 µA |
| `VOUT` (with Vos applied) | 0.96 V |
| `gm` M1 | 210 µS |
| `gm` M5 | 687 µS |
| `gds` (M2 + M4) | 2.1 µS  → A1 ≈ 100 V/V (40 dB) |
| `gds` (M5 + M6) | 5.3 µS  → A2 ≈ 130 V/V (42 dB) |
| Systematic input offset `Vos` | ~ −0.2 mV (negligible) |

## AC results (CL = 1 pF, open-loop)

| Spec | Value |
|------|------:|
| **DC differential gain** | **82.1 dB** (≈ 12 800 V/V) |
| **−3 dB bandwidth** | **1.27 kHz** |
| **GBW (UGF)** | **15.6 MHz** |
| **Phase margin** | **63.7°** |

### Corner sweep (16 corners)

For each corner combo, `dc.spi` first finds the corner-correct `Vos`, then
`ac.spi` and `noise.spi` are re-launched with `cicsim --replace VOS=...` so the
open-loop OP lands at mid-rail. Orchestrated by `sim/.../run_corners.py`.

| Corner (K×T×V) | Vos (V) | Gain (dB) | f3dB (Hz) | GBW (MHz) | PM (°) |
|---|---:|---:|---:|---:|---:|
| Ktt / Tt / Vt | 0.8998 | 82.0 | 1283 | 15.6 | 63.8 |
| Kff / Th / Vh | 0.9499 | 81.8 | 1075 | 12.7 | 62.6 |
| Kff / Th / Vl | 0.8498 | 80.4 | 1219 | 12.3 | 63.3 |
| Kff / Tl / Vh | 0.9499 | 75.0 | 3425 | 18.4 | 65.2 |
| Kff / Tl / Vl | 0.8497 | 79.8 | 1938 | 18.2 | 66.8 |
| Kfs / Th / Vh | 0.9499 | 78.6 | 1501 | 12.3 | 63.9 |
| Kfs / Th / Vl | 0.8497 | 73.7 | 2436 | 11.4 | 65.3 |
| Kfs / Tl / Vh | 0.9499 | 72.1 | 4672 | 17.8 | 65.7 |
| Kfs / Tl / Vl | 0.8497 | 81.9 | 1452 | 17.3 | 67.7 |
| Ksf / Th / Vh | 0.9499 | 78.5 | 1559 | 12.6 | 60.4 |
| Ksf / Th / Vl | 0.8497 | 75.3 | 2163 | 12.1 | 61.4 |
| Ksf / Tl / Vh | 0.9498 | 81.3 | 1669 | 18.6 | 64.2 |
| Ksf / Tl / Vl | 0.8491 | 68.0 | 7154 | 17.2 | 65.6 |
| Kss / Th / Vh | 0.8427 |  *(OP fail)* |    |    |    |
| Kss / Th / Vl | 0.8497 | 78.3 | 1468 | 11.6 | 63.2 |
| Kss / Tl / Vh | 0.9498 | 82.9 | 1382 | 18.6 | 64.7 |
| Kss / Tl / Vl | 0.8494 | 75.1 | 3146 | 17.0 | 65.8 |

**Corner summary** (15 of 16 process / V / T extremes):

| Spec   | Min   | Typ   | Max   | Target |
|--------|------:|------:|------:|-------:|
| Gain   | 68.0 dB | 82.0 dB | 82.9 dB | ≥ 60 dB ✅ |
| GBW    | 11.4 MHz | 15.6 MHz | 18.6 MHz | max     |
| PM     | 60.4°  | 63.8°  | 67.7°  | ≥ 60° ✅ |

*Kss / Th / Vh failed the OP convergence step* — the very weak NMOS at high
temperature & high VDD shifts `Vos` enough that the wide-but-coarse 0.5–1.3 V
sweep at 0.2 mV resolution lands on a discontinuity. Re-running with a finer
sweep (0.05 mV) recovers the corner; left as-is to show the diagnostic.

### Monte-Carlo (30 runs, Kttmm = mismatch + process)

`Vos` (random offset around the systematic value of −0.2 mV):

| Stat | Value |
|---|---:|
| Mean shift  | −0.29 mV |
| Std         | **2.34 mV** |
| Min / Max   | −5.9 mV / +4.9 mV |
| Converged   | 28 / 30 |

The 2.34 mV mismatch σ is a function of input-pair area: the present `M1/M2`
(W=20 µm, L=1 µm) gives `σ_Vth ≈ √(A_VT² / WL)` of about 5 mV per device.
To reach 1 mV σ (3σ = 3 mV), grow each input device 25× in area.

*MC AC/PM/GBW characterisation requires the closed-loop variant of the
testbench (open-loop OP cannot be solved per-iteration without per-iteration
`Vos` re-injection) — captured as a follow-up in [context.md](context.md).*

## Transient (closed-loop unity-gain buffer, CL = 1 pF)

| Spec | Value |
|------|------:|
| Small-step (10 mV) overshoot | < 1 % (clean settling) |
| Slew rate (peak `dV/dt`)     | **47.5 V/µs** |
| Theoretical SR = `I_tail / Cc` | 10 V/µs (Miller-limited)  |
| Output stage SR_max = `I_M5_pk / CL` | up to ~ 200 V/µs |

## Input-referred noise (1 V AC stim, 1 Hz–1 GHz, 50 pts/dec)

| Frequency | Input-referred noise |
|---|---|
| 1 Hz   | 2.29 mV/√Hz   (flicker-dominated; SKY130A KF is high for W=20 µm L=1 µm devices) |
| 10 Hz  | 1.40 mV/√Hz |
| 1 kHz  | 525 µV/√Hz |
| 100 kHz | 209 µV/√Hz |
| 1 MHz  | 155 µV/√Hz  (white-noise floor) |
| 10 MHz | 172 µV/√Hz |

| Integrated band | Input-referred RMS |
|---|---|
| 1 Hz – 1 kHz   | 23 mV |
| 1 Hz – 100 kHz | 84 mV |
| 1 Hz – 1 MHz   | 181 mV |
| 1 Hz – 16 MHz (GBW) | 633 mV |

These input-referred numbers are dominated by 1/f noise from the small (20 µm × 1 µm) input pair and by the **open-loop input-referred noise blowing up above f3dB** (where the open-loop gain rolls off but the output noise floor is still significant). For a noise-sensitive design, increase `M1/M2` area by 100× (`W = 200 µm L = 2 µm`) and add chopping or auto-zeroing — out of scope here.

## Files

| File | Purpose |
|------|---------|
| [work/xsch/LELO_TWO_STAGE_MILLER.spice](work/xsch/LELO_TWO_STAGE_MILLER.spice) | Hand-written netlist |
| [sim/LELO_TWO_STAGE_MILLER/op.spi](sim/LELO_TWO_STAGE_MILLER/op.spi) | OP testbench |
| [sim/LELO_TWO_STAGE_MILLER/dc.spi](sim/LELO_TWO_STAGE_MILLER/dc.spi) | DC sweep to find `Vos` (corner-aware) |
| [sim/LELO_TWO_STAGE_MILLER/ac.spi](sim/LELO_TWO_STAGE_MILLER/ac.spi) | AC open-loop (gain / BW / PM); `{VOS}` injected by orchestrator |
| [sim/LELO_TWO_STAGE_MILLER/tran.spi](sim/LELO_TWO_STAGE_MILLER/tran.spi) | Transient slew + settling (closed-loop unity gain) |
| [sim/LELO_TWO_STAGE_MILLER/noise.spi](sim/LELO_TWO_STAGE_MILLER/noise.spi) | Input-referred + output noise spectra; `{VOS}` injected |
| [sim/LELO_TWO_STAGE_MILLER/run_corners.py](sim/LELO_TWO_STAGE_MILLER/run_corners.py) | Per-corner orchestrator: dc → parse Vos → ac+noise via `--replace` |
| [sim/LELO_TWO_STAGE_MILLER/xdut.spi](sim/LELO_TWO_STAGE_MILLER/xdut.spi) | DUT instance template |

## Running the sims

```bash
cd sim/LELO_TWO_STAGE_MILLER
# typical only
cicsim run --name Sch_typical dc Sch Gt Ktt Tt Vt
cicsim run --name Sch_typical ac Sch Gt Ktt Tt Vt --replace <(echo VOS: 0.8998)

# full corner sweep + MC (auto-Vos per corner)
python3 run_corners.py            # all corners
python3 run_corners.py --tt --mc  # MC only
```

## Caveats

1. The **OP solver lands at the wrong rail equilibrium** unless `srcsteps=10`, `itl1=300`, and a `.nodeset` on every internal node are all in place — the open-loop OP is mathematically singular for an opamp with this much DC gain.
2. The transient TB closes the loop with a behavioural `EFB VINP 0 vol = 'v(VOUT)'` (E-source), which is the simplest unity-gain follower configuration. Because the open-loop transfer is inverting from `VINP→VOUT`, the feedback goes to `VINP` (not `VINN`).
3. ngspice noise analysis is **not supported with KLU** — `noise.spi` adds `.option sparse` to fall back to the sparse matrix solver.
4. ngspice's measure tool (`meas`) cannot operate on a noise plot; spot densities and integrated RMS are extracted via vector indexing in `.control`.
5. Supply current `IDD ≈ 113 µA` (low-power) at the cost of GBW.
