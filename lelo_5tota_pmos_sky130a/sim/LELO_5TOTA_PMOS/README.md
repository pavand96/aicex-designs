# LELO_5TOTA_PMOS — PMOS-Input 5-Transistor OTA

A complementary version of [`lelo_5tota_sky130a`](../lelo_5tota_sky130a) using a **PMOS input differential pair** instead of NMOS.

## Why a PMOS input?

| Trade-off | NMOS-input 5T OTA | PMOS-input 5T OTA |
|-----------|-------------------|-------------------|
| Transconductance per W | High (μ_n ≈ 3·μ_p) | Lower — needs ~3× width for same g_m |
| 1/f (flicker) noise | Higher | **Lower** (PMOS in surface-channel n-well is quieter) |
| Input common-mode range | Best near VDD | **Best near VSS / ground** |
| Tail device | NMOS (sources to VSS) | PMOS (sources to VDD) |
| Load mirror | PMOS at top | **NMOS at bottom** |

Use the PMOS-input version when you need **low-frequency / low-noise** signal handling, or when the input common-mode is biased close to ground (e.g. sensor front-ends, bandgap output buffers).

## Topology

```
                VDD
                 │
        ┌────┬───┴────┬─────┐
        │    │        │     │
       M6   M5       M1     M2
     (diode)(tail)  (PMOS pair)
        │    │       │  │
        │   net1─────┘  │
       IBIAS            │
                  net2 VOUT
                   │    │
                  M3    M4    ← NMOS mirror load
                (diode)
                   │    │
                  VSS  VSS
```

| Device | Type | Role |
|--------|------|------|
| M1, M2 | PMOS, W=80, L=0.8 | Differential input pair |
| M3 (diode), M4 | NMOS, W=36, L=0.8 | Current-mirror load |
| M5 | PMOS, W=36, L=1.0 | Tail current source |
| M6 (diode) | PMOS, W=36, L=1.0 | Bias mirror reference |

## Key netlist differences from the NMOS version

1. All NMOS / PMOS device types swapped.
2. Input pair sources (`net1`) are now the **tail node referenced to VDD** instead of VSS.
3. Mirror diode node (`net2`) is the **drain of M1 / gate of M3** (NMOS load), expected around 0.4 – 0.5 V.
4. **`IIBIAS` source direction reversed**: current is now drawn *out* of `IBIAS` (toward VSS) so that the PMOS diode M6 conducts from VDD → IBIAS.

## Simulations

Same set as the NMOS variant — `op`, `ac`, `dc` (ICMR/OCMR), `tran`, `slew`. All testbenches in `sim/LELO_5TOTA_PMOS/` have been updated for the new topology (model names and bias direction).

```bash
cd sim/LELO_5TOTA_PMOS
make typical TB=op    # operating point
make typical TB=ac    # AC: gain, GBW, PM
make typical TB=dc    # ICMR / OCMR sweeps
make typical TB=tran  # transient sine response
```
