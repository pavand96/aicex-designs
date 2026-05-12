# LELO_CHERRY_HOOPER — Cherry-Hooper Differential Amplifier

Wide-bandwidth two-stage differential amplifier on **SKY130A**, sized for **maximum gain-bandwidth (GBW)** and biased entirely from a single external 10 µA reference current via on-chip diode-mirror generators.

## Topology

- **Bias generator**: NMOS diode `MNB` at the `IBIAS` pin sets V<sub>GSn</sub>; mirrored by `MNREF` into a PMOS diode `MPB` to set `vbiasp`. All on-chip mirrors then derive their bias from these two reference legs.
- **Stage 1**: NMOS differential pair `M1/M2` with PMOS current-source loads `MI3/MI4` (gated by `vbiasp`) and tail mirror `MT1` (gated by `IBIAS`)
- **Stage 2**: NMOS common-source pair `M3/M4` with PMOS loads `MI1/MI2`, tail mirror `MT2`, and **shunt feedback resistors `RF`** from each output back to the same-side `M3/M4` gate (which is also the `M1/M2` drain node)
- The Cherry-Hooper trick: `RF` collapses the impedance at the inter-stage nodes (`nA`, `nB`) to ≈ `1/gm3`, removing what would otherwise be a low-frequency pole and dramatically extending the bandwidth

**Subckt pinout**: `VSS VDD VOUTP VOUTN IBIAS VINP VINN`

## Sizing (typical, tt corner, 27 °C, 1.8 V)

| Device | Type | W (µm) | L (µm) | Role |
|--------|------|--------|--------|------|
| MNB    | NFET |  8 | 1.0 | NMOS reference diode (at IBIAS pin) |
| MNREF  | NFET |  8 | 1.0 | Reference mirror leg into MPB |
| MPB    | PFET |  2 | 1.0 | PMOS reference diode |
| M1, M2 | NFET | 60 | 0.5 | Input pair |
| M3, M4 | NFET | 15 | 0.5 | 2nd-stage CS |
| MT1, MT2 | NFET | 80 | 1.0 | Tail mirrors (1:10 from MNB) |
| MI1–MI4 | PFET | 20 | 1.0 | PMOS load mirrors (1:10 from MPB) |
| RF1, RF2 | R | – | – | **16 kΩ** shunt feedback (sized for ~20 dB midband gain) |

External bias is just one current source: `IIBIAS VSS IBIAS dc 10u`.

## Operating point (with bias mirror)

| Quantity | Value |
|---|---|
| IBIAS reference current | 10.0 µA (set externally) |
| Mirror legs (MNREF, MPB) | 9.78 µA |
| Tail current (MT1, MT2) | 126 / 135 µA |
| Branch current (per side) | 63 µA |
| `VOUTP` = `VOUTN` | 1.60 V |
| `IBIAS` (NMOS V<sub>GS</sub>) | 0.66 V |
| `vbiasp` | 0.44 V |
| `gm` M1 (input) | **1.30 mS** |
| `gm` M3 (2nd stage) | **0.96 mS** |
| Total `IDD` | ≈ 540 µA |

All devices in saturation. The mirror loop requires `.option srcsteps=10 itl1=300` and a `.nodeset` on every leg to avoid the trivial-zero equilibrium — see [context.md](context.md) § 10 for the full story.

## AC results (CL = 100 fF per output, RF = 16 kΩ)

| Spec | Value |
|------|------:|
| **Differential DC gain** | **19.6 dB** (≈ 9.6 V/V) |
| **−3 dB bandwidth** | **405 MHz** |
| **GBW** | **1.42 GHz** |
| Phase margin (open-loop) | ~ 0° — ringing in tran (needs Miller cap for closed-loop use) |

## Transient: slew rate & settling (CL = 100 fF)

| Spec | Value |
|------|------:|
| Peak `\|d(VOUTP−VOUTN)/dt\|` (200 mV diff step) | **1.57 V/ns ≈ 1570 V/µs** |
| Theoretical SR  = 2 · I<sub>tail</sub> / C<sub>L</sub> | 2.52 V/ns |
| Small-step (10 mV) overshoot pk-pk / final | 357 mV / 225 mV (~60 % overshoot) |

## Corner sweep (Sch_typical / Sch_ss / Sch_ff)

| Corner | Gain (dB) | f3dB (MHz) | GBW (GHz) |
|--------|----------:|-----------:|----------:|
| TT 27 °C 1.80 V       | 19.6 | 405 | 1.42 |
| SS 85 °C 1.62 V       | 15.8 | 350 | 1.01 |
| FF −40 °C 1.98 V    | 23.2 | 466 | 1.87 |

Gain spread ±3.7 dB; GBW spread 0.86 GHz. SS is the worst-case for both.

## Monte-Carlo — process + mismatch (Kttmm, 30 runs)

| Metric | Mean | σ | Min | Max |
|--------|-----:|--:|----:|----:|
| Gain (dB) — healthy 27/30   | **19.8** | **1.34** | 17.3 | 23.2 |
| f3dB (MHz)                  | 379 | 94 | 83 | 482 |

**Startup yield warning**: 3 of 30 runs (10 %) landed in the *wrong* equilibrium of the self-biased mirror under heavy mismatch (gain came out around −32 dB). A startup-kicker circuit is required for production use — see context.md § 13.


## Why this maximises GBW

The Cherry-Hooper restructures the bandwidth limit:
- Conventional 5T OTA: `GBW ≈ gm1 / (2π × CL_total)` where `CL_total` is dominated by the intrinsic high-impedance node capacitance Miller-multiplied by the second stage gain.
- Cherry-Hooper: `RF` makes the inter-stage node low-impedance (≈ `1/gm3` ≈ 800 Ω here). The pole at that node is pushed past the unity-gain frequency. The remaining output pole is `≈ gm3 / CL`, also very high.

Comparison vs the LELO_5TOTA design in this same repo:

| Design | IDD | DC gain | GBW | GBW/µA |
|--------|-----|---------|-----|--------|
| LELO_5TOTA (PMOS in) | 8.5 µA | 37 dB | 7.9 MHz | 0.93 MHz/µA |
| LELO_CHERRY_HOOPER | 540 µA | 19.6 dB | **1.42 GHz** | **2.6 MHz/µA** |

GBW improved ~180×; GBW per current ~2.8× — a textbook Cherry-Hooper trade-off (trades gain for bandwidth at the same current density).

## Files

| File | Purpose |
|------|---------|
| [work/xsch/LELO_CHERRY_HOOPER.spice](work/xsch/LELO_CHERRY_HOOPER.spice) | Hand-written netlist (with bias mirror) |
| [sim/LELO_CHERRY_HOOPER/op.spi](sim/LELO_CHERRY_HOOPER/op.spi) | OP testbench |
| [sim/LELO_CHERRY_HOOPER/ac.spi](sim/LELO_CHERRY_HOOPER/ac.spi) | AC differential testbench |
| [sim/LELO_CHERRY_HOOPER/tran.spi](sim/LELO_CHERRY_HOOPER/tran.spi) | Transient: slew + settling |
| [sim/LELO_CHERRY_HOOPER/acmc.spi](sim/LELO_CHERRY_HOOPER/acmc.spi) | AC TB for Monte-Carlo (no fgbw/pm meas) |
| [sim/LELO_CHERRY_HOOPER/xdut.spi](sim/LELO_CHERRY_HOOPER/xdut.spi) | DUT instance template |

## Running the sims

The netlist must NOT be regenerated by `make typical` (it would overwrite the hand-written one). Run cicsim directly:

```bash
cd sim/LELO_CHERRY_HOOPER

# Bring-up
cicsim run --name Sch_typical op   Sch Gt Ktt Tt Vt
cicsim run --name Sch_typical ac   Sch Gt Ktt Tt Vt
cicsim run --name Sch_typical tran Sch Gt Ktt Tt Vt

# Corners
cicsim run --name Sch_ss ac Sch Gt Kss Th Vl
cicsim run --name Sch_ff ac Sch Gt Kff Tl Vh

# Monte-Carlo (process+mismatch, 30 runs)
cicsim run --name Sch_mc --count 30 acmc Sch Gt Kttmm Tt Vt
```

## Design knobs

| To increase | Adjust |
|-------------|--------|
| **GBW** | Lower `CL`, increase tail current (raise `VBIASN`), shrink `RF` |
| **DC gain** | Lengthen M3/M4 (`L 0.5 → 1`), increase `RF`, lengthen PMOS loads |
| **Phase margin** | Raise `RF` (slower but more damped) |

## Caveats

1. SKY130A `L = 0.15 µm` was tried — `gm` rises but `gds` rises faster, dropping intrinsic gain below 1 dB. Sweet spot for max-GBW with usable gain is `L = 0.5 µm`.
2. The self-biased NMOS/PMOS reference loop has two stable equilibria. Convergence to the intended one requires both `.option srcsteps=10 itl1=300` *and* a `.nodeset` on every mirror leg — see [context.md](context.md) § 10.1.
3. **Open-loop phase margin ≈ 0°**: differential output rings ~60 % on a small step. Closed-loop use requires a Miller compensation cap.
4. **Mirror startup yield ≈ 90 %** under MC mismatch — a startup kicker is required for production.
3. All devices use `nf = 1` because ngspice multi-finger devices break the `@m.<inst>.<model>[id]` access strings used in the OP measurement script.
