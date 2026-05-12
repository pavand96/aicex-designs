# LELO_5TOTA_PMOS — Simulation Results

Results from running the PMOS-input 5T OTA testbenches on the typical corner (`tt`, 27 °C, $V_{DD}$ = 1.8 V).

## Bias point (correctly biased for PMOS pair)

| Parameter | Value |
|-----------|-------|
| $V_{DD}$ / $V_{SS}$ | 1.8 V / 0 V |
| $V_{CM}$ (input common-mode) | **0.4 V** (low — required for PMOS pair) |
| $I_{BIAS}$ (forced) | 6.26 µA |
| $I_{TAIL}$ (in M5) | 6.09 µA |
| $V_{OUT}$ (quiescent) | 0.518 V |
| $V_{TAIL}$ (net1, M1/M2 source) | 1.426 V (close to $V_{DD}$) |
| $V_{MIRROR}$ (net2, NMOS diode) | 0.518 V |
| Total $I_{DD}$ | 8.5 µA |

## Operating-point per device

| Device | Type | $I_D$ (µA) | $g_m$ (µS) | $g_{ds}$ (µS) | $V_{ov}$ (mV) | Region |
|--------|------|-----------|-----------|---------------|--------------|--------|
| M1 (in pair) | PMOS | 3.05 | 54 | 0.25 | ~110 | sat |
| M2 (in pair) | PMOS | 3.05 | 54 | 0.25 | ~110 | sat |
| M3 (diode) | NMOS | 3.05 | – | – | 47 | sat (diode) |
| M4 (mirror) | NMOS | 3.05 | 72 | 0.52 | 47 | sat |
| M5 (tail) | PMOS | 6.09 | 98 | 0.41 | 83 | sat |
| M6 (bias diode) | PMOS | 6.27 | – | – | 83 | sat (diode) |

## AC analysis

| Spec | Value |
|------|-------|
| **DC gain** | **36.97 dB** (~71 V/V) |
| $f_{3\text{dB}}$ | 113 kHz |
| **GBW (unity-gain BW)** | **7.91 MHz** |
| **Phase margin** | **80.9°** (excellent) |
| Gain margin | unconditionally stable (phase never reaches –180°) |
| Group delay (LF) | 1.4 µs |
| Gain peaking | 0 dB (well-behaved) |

Sanity check: $A_{v,DC} = g_{m1} \times (r_{ds2} \parallel r_{ds4}) = 54\ \mu\text{S} \times (4\ \text{M}\Omega \parallel 1.9\ \text{M}\Omega) = 54 \times 1.3 = 70\ \text{V/V} = 36.9\ \text{dB}$ — matches AC measurement.

## Transient analysis

1 kHz differential sine, $V_{diff,pk}$ = 2 mV (small-signal):

| Parameter | Value |
|-----------|-------|
| Output magnitude (1st harmonic) | 134.9 mV |
| Effective gain at 1 kHz | 67.5 V/V → **36.6 dB** (matches AC) |
| Output swing peak-peak | 269 mV |
| THD | 1.47 % |

## DC ICMR/OCMR

The `dc.spi` and `dc.meas` from the NMOS variant **do not** work as-is for the PMOS topology (sweep direction and saturation-margin signs are NMOS-specific). Marked as TODO.

---

# How to Improve This Design

The 37 dB gain and 7.9 MHz GBW are reasonable for a textbook 5T OTA at 8 µA but leave a lot of room. Here are concrete next steps, ranked by impact-to-effort.

## 1. Increase output resistance → higher DC gain (easiest, +10 to +15 dB)

The output node sees $r_{ds,M2} \parallel r_{ds,M4}$ = 4 MΩ ‖ 1.9 MΩ ≈ 1.3 MΩ. The NMOS load (M4) is the limiter.

**Fix:** Increase L of M4 (and M3 for matching) from 0.8 µm → **2 µm**. This roughly **3× boosts $r_{ds,M4}$** because $r_{ds} \propto L / (\lambda I_D)$ and channel-length modulation $\lambda$ drops roughly inversely with L.

Expected: gain → ~50 dB at the same current.

## 2. Match output common-mode to mid-rail (+swing margin)

Current $V_{OUT}$ = 0.518 V — strongly biased toward $V_{SS}$. This kills positive output swing (only 1.28 V of headroom up, 0.52 V down).

**Fix:** Resize M3/M4 wider (e.g. W = 80 µm instead of 36 µm) so $V_{GS,M4}$ drops from 0.5 V → 0.35 V. Then $V_{OUT,Q}$ rises closer to $V_{DD}/2 = 0.9$ V.

## 3. Bias the input pair into stronger inversion or weak inversion?

Currently $V_{ov,M1}$ ≈ 110 mV → moderate inversion ($g_m/I_D$ ≈ 18 S/A). Two options:

- **Weak inversion (large $g_m$ for same current):** Make M1/M2 wider (W = 80 → 200 µm), which boosts $g_{m1}$ by ~2× and pushes gain up by 6 dB without adding current.
- **Strong inversion (better matching, less noise):** Reduce W (W = 80 → 40 µm), accept lower gain in exchange for better offset matching.

For low-noise instrumentation: keep wide and weakly-inverted.

## 4. Add a cascode → 5T OTA becomes telescopic / folded cascode (+30 dB)

This is the biggest jump. Adding a single cascode device per output branch raises the output impedance from $r_{ds}$ to $g_m r_{ds}^2$ — a factor of 50–100 in gain.

| Topology | Typical gain | Output swing | Complexity |
|----------|--------------|--------------|------------|
| 5T OTA (this) | 35 – 50 dB | $V_{DD} - 2V_{ov}$ | 5 devices |
| Telescopic cascode | 70 – 90 dB | $V_{DD} - 4V_{ov}$ | 9 devices, more bias |
| Folded cascode | 70 – 90 dB | $V_{DD} - 2V_{ov}$ | 11 devices, more bias |

For 1.8 V supply, **folded cascode** is the practical winner — preserves swing.

## 5. Improve the tail current source (+5–10 dB CMRR)

M5 has $r_{ds,M5}$ ≈ 2.4 MΩ. CMRR of a 5T OTA ∝ $g_{m1} r_{ds5}$, so doubling L of M5 directly doubles CMRR.

**Fix:** L = 1.0 → 2.0 µm on M5 (and M6 for matching).

## 6. Compensate for capacitive loads explicitly

The 81° phase margin is comfortable for the 1 pF test load but will degrade quickly with large $C_L$. If you intend to drive >5 pF, add a Miller compensation capacitor across M4.

## 7. Optimization roadmap

| Step | Action | Expected gain | Expected GBW | Effort |
|------|--------|---------------|--------------|--------|
| 0 | Baseline (now) | 37 dB | 7.9 MHz | – |
| 1 | L_M3/M4 = 2 µm | **~50 dB** | 6 MHz | sed |
| 2 | + L_M5/M6 = 2 µm | 51 dB | 5.5 MHz | sed |
| 3 | + W_M3/M4 = 80 µm (rebalance VOUT) | 52 dB | 7 MHz | sed |
| 4 | + Re-tune $I_{BIAS}$ to 10 µA | 50 dB | **12 MHz** | param |
| 5 | Migrate to folded cascode | **80+ dB** | 10–20 MHz | new schematic |

## 8. Using the characterization data (`lelo_modele_sky130a`)

Your NMOS/PMOS 2D characterization CSVs can drive **systematic device sizing**:
- Look up $g_m/I_D$ vs $V_{ov}$ for your target inversion level
- Pick W to hit the target $g_m$ at your bias current
- Pick L to hit the target $r_{ds}$ for required gain

This lets you size by spec rather than trial-and-error in xschem.
