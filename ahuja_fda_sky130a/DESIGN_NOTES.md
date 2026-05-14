# Ahuja FDA SKY130A — Design Notes

## Topology (frozen)

Two-stage fully-differential amplifier with Ahuja (cascoded-Miller) compensation.

- **Stage 1**: NMOS input pair (XMI1/2) → PMOS-LVT cascode (XMC1/2) → PMOS-LVT top current source (XMD1/2). Single-cascoded (PMOS side only).
- **Stage 2**: PMOS-LVT common-source (XML_P/N) with NMOS load (XMU_P/N), CMFB-controlled.
- **CMFB**: resistive averager (1 MΩ ‖ 1 MΩ from VOP, VON to v_cms) + PMOS diff pair (XQ_CMS / XQ_REF) + NMOS mirror load (XQL_REF / XQL_CMS) → drives `nVcmfb` to gates of XMU.
- **Compensation**:
  - `CC_P/N = 30 pF` Ahuja caps from VOP/VON to BPOS/BNEG (cascode source nodes).
  - `CA_P/N = 5 pF` from APOS/ANEG to VSS (stage-1 high-Z node loading; pulls dominant pole down).

## Verified specs (Sch Gt Ktt Tt Vt corner, CL = 10 pF)

| Metric        | Measured     | Spec         | Status |
|---------------|--------------|--------------|--------|
| DC gain       | 80.8 dB      | 100 dB       | ✗ (see below) |
| GBW           | 4.7 MHz      | > 5 MHz      | ✗ (marginal, see below) |
| Phase margin  | 51°          | > 50°        | ✓ |
| Slew rate avg | 5.33 V/µs    | > 5 V/µs     | ✓ |
| Output swing  | ~1.1 Vpp diff| 1 V          | ✓ |
| Power         | 1.39 mW      | < 2 mW       | ✓ |

Note: GBW dropped from 8.88 MHz to 4.68 MHz when resistor refs were
replaced with NMOS current mirrors (branch current dropped to ~73 µA
because XM_TAIL Vds is small → mirror in triode-edge region). The
resistor-ref design hit 8.88 MHz @ 81.4 dB but was not PVT-portable.

## Bias generator evolution

| Version | Topology | TT result | Notes |
|---------|----------|-----------|-------|
| v1 | Resistor refs (RREF_N=10k, RREF_PD=9.5k, RREF_PC=8k from rails) | 81.4 dB / 8.88 MHz | Best TT, but bias currents track 1/R → V_DD-dependent. |
| v2 | NMOS current mirror from external IBIAS=100 µA (bandgap) + simple PMOS diodes | 80.8 dB / 4.68 MHz | No resistors. |
| v3 | Wide-swing (separate-leg) PMOS cascode mirror | 80.8 dB / 4.68 MHz | Cleanest bias structure. |

v3 (wide-swing) is the committed version. Two NMOS legs each pull 100 µA
through a PMOS-LVT diode (XMD_REF, W=20) and a smaller diode (XMC_REF, W=8
for stronger \|Vsg\| → cascode bias). Stacked-diode wide-swing was tried
first but eats 2×\|Vsg\| (~1.8 V) which leaves no room for the NMOS sink —
separate-leg is the only viable wide-swing in 1.8 V supply.

## Corner sweep results (PVT)

Full P×T×V sweep (5 process × 3 (T,V) corners = 15 corners) on the
v3 (wide-swing) bias version:

| Process | T,V | DC | GBW | PM |
|---|---|---|---|---|
| Ktt | Tt Vt | **80.8 dB** | 4.68 MHz | **51°** |
| Ktt | Th Vh | -40.5 dB | 1.4 MHz | unstable |
| Ktt | Tl Vl | 5.2 dB | 0.56 MHz | overdamped |
| Kss | Tt Vt | -7.2 dB | 4.4 MHz | unstable |
| Kss | Th Vh | 46.5 dB | 2.1 MHz | unstable |
| Kss | Tl Vl | broken | — | — |
| Kff | Tt Vt | 21.6 dB | 2.9 MHz | overdamped |
| Kff | Th Vh | 33.0 dB | 6.9 MHz | 77° |
| Kff | Tl Vl | 22.3 dB | 2.4 MHz | overdamped |
| Ksf | * * | ~25 dB | ~2 MHz | overdamped |
| Kfs | * * | 12–52 dB | 2–6 MHz | unstable |

**Only Ktt @ Tt @ Vt is functional.** The wide-swing bias change
produced no meaningful corner improvement, which proved that the failure
is structural, not biasing.

## Why corners fail (structural diagnosis)

TT bias point breakdown (1.8 V supply):

```
VDD - |Vsg_XMD| - |Vds_XMC| - Vds_XMI - Vds_TAIL = 1.8 V
1.8 - 0.85      - 0.20      - 0.43    - 0.14     ≈ 1.62 V used
                                                  -> 0.18 V slack
```

Across PVT, the slack is consumed:
- **Vth shift ±100 mV** (Kss/Kff process): directly modulates \|Vsg_XMD\|
  which already eats 0.85 V of the supply. ±100 mV is larger than the
  200 mV cascode saturation margin.
- **VDD shift ±90 mV** (Vh/Vl): on top of Vth shifts, compresses or expands
  the entire stack.
- **Temperature**: shifts gm and Vth in opposite directions, breaks the
  carefully tuned XMD/XMC overdrive ratio.

Wide-swing biasing only helps when the failure is bias-point inaccuracy.
Here the failure is **headroom collapse** — no biasing scheme can recover
lost Vds margin.

## What it would take to make corner-robust

1. **Folded-cascode topology** (NMOS input + NMOS cascode at bottom).
   1.8 V works because NMOS Vth is in series with VSS, not VDD; PMOS
   becomes the simple top current source (no cascode in stack).
2. **HVT NMOS input pair** to free up Vth headroom from VSS side.
3. **Higher VDD** (3.3 V) — not allowed by spec.

All three are topology changes — outside the scope of this frozen Ahuja
design.


## Gain-push experiments (why 81.4 dB is the practical ceiling)

The single-cascoded 2-stage Ahuja gain budget is:

$$A_{vo} = (g_{m1} \cdot R_{out1}) \cdot (g_{m2} \cdot R_{out2})$$

With XMI uncascoded, `R_out1 ≈ (g_mc·r_oc·r_od) ‖ r_oi`. The input-NMOS r_oi shorts the cascoded PMOS branch. Stage 1 ≈ 45 dB, stage 2 ≈ 36 dB → 81 dB. Matches measurement.

Operating-point bias budget is the limiter, not r_o:

| Device | Vds (baseline) | Margin |
|--------|----------------|--------|
| XMI    | 0.43 V         | OK     |
| XMC    | 1.02 V         | deep saturation |
| XMD    | 0.21 V         | **edge of triode**, |Vov| ≈ 0.45 V |

Sum of stacked Vds ≈ 1.66 V of 1.8 V supply → only 140 mV slack across the entire branch. Every "tweak one knob" experiment failed because the branch is on a knife edge.

### Knob sweeps (all reverted)

| # | Change                                                        | Result   | Failure mode |
|---|---------------------------------------------------------------|----------|--------------|
| 1 | XMI L=2→4, W=40→80 (gm/Id-correct)                            | 35 dB    | Lower Vov_in pulled `ntail` to 0.15 V → tail mirror entered triode → branch starved (70 µA), XMI Vds=0.14 V triode. |
| 2 | XMD L=1→2, W=20→40 (gm/Id-correct)                            | crash    | OP rebalance starved branch. |
| 3 | XMD W=20→40 (ref + outputs together)                          | 18 dB    | Stronger XMD at fixed Vsg → forced deeper triode (Vds=0.16 V). |
| 4 | RREF_PD 9.5k→13k (weaken XMD via higher VbD)                  | 13 dB    | Weakened XMD couldn't source 100 µA → branch dropped to 60 µA → XMI Vds collapsed to 0.07 V. |

### Take-aways

- The 1.8 V supply leaves no headroom for incremental rebudgeting in the existing topology.
- A coordinated bias re-design (e.g. halve all stage-1 currents and re-size everything for the new bias point) could plausibly add ~5 dB on stage 1, but it directly trades against SR (we have zero SR margin: 5.33 vs 5 V/µs spec).
- Reaching 100 dB **requires a topology change**: stage-2 PMOS cascode (~+20–30 dB), a third gain stage, or gain-boost amplifiers on the cascodes.
- For the frozen topology at 1.8 V SKY130: **81.4 dB is the realistic ceiling.** The "88–92 dB without topology change" estimate quoted earlier was wrong; the bias coupling makes single-knob pushes infeasible.

## Files

- Schematic netlist: `work/xsch/AHUJA_FDA.spice`
- Testbenches: `sim/AHUJA_FDA/{op,ac,unity,dccmfb}.spi`
- DUT include: `sim/AHUJA_FDA/xdut.spi`

## Run command

```bash
cd sim/AHUJA_FDA
cicsim run <bench> Sch Gt Ktt Tt Vt --no-sha --replace vos_typ.yaml
```
