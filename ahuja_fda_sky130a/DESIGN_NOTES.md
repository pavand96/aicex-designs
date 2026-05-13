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
| DC gain       | 81.4 dB      | 100 dB       | ✗ (see below) |
| GBW           | 8.88 MHz     | > 5 MHz      | ✓ |
| Phase margin  | 56.3°        | > 50°        | ✓ |
| Slew rate avg | 5.33 V/µs    | > 5 V/µs     | ✓ |
| Output swing  | ~1.1 Vpp diff| 1 V          | ✓ |
| Power         | 1.39 mW      | < 2 mW       | ✓ |

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
