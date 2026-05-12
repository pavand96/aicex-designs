# Two-Stage Miller Opamp — Context & Convergence Log

Companion to `lelo_cherry_hooper_sky130a/context.md`. Records every design decision, debug step, and gotcha for the **two-stage Miller-compensated opamp** on **SKY130A + ngspice + cicsim**.

---

## 1. Design Targets

| Metric | Target | Achieved |
|---|---|---|
| DC gain | ≥ 60 dB | **82 dB** |
| Phase margin | ≥ 60° | **64°** |
| GBW | maximize | **15.6 MHz** |
| Slew rate | n/a | 47.5 V/µs |

## 2. Topology Choices

- **Stage 1**: NMOS diff pair + PMOS mirror load — single-ended output. Gain `A1 = gm1/(gds2+gds4) ≈ 100 V/V`.
- **Stage 2**: PMOS CS + NMOS current source. Gain `A2 = gm5/(gds5+gds6) ≈ 130 V/V`.
- **Compensation**: Miller `Cc = 2 pF` between stage-1 output (`vout1`) and `VOUT`, in series with **nulling resistor `Rz = 1.6 kΩ ≈ 1/gm5`** to push the right-half-plane zero into the LHP.

Sized for `L = 1–2 µm` (long-channel for high gain). Input pair stays at `L = 1 µm` to keep gm/Id reasonable.

## 3. Bias Sizing — the "systematic offset = 0" Rule

For a balanced two-stage opamp the second stage must be sized such that, when stage 1 sits at its symmetric OP, stage 2's PMOS sources exactly the current the NMOS load wants to sink. The textbook rule is:

```
   W5/W3   =   2 × W6/Wt        (where Wt = stage-1 tail)
```

Our values: `W5/W3 = 80/10 = 8`, `2*W6/Wt = 2*32/8 = 8` ✓ matched. Result: systematic offset `Vos ≈ −0.2 mV` (essentially zero).

If you violate this rule, `VOUT` rails because the open-loop gain multiplies any current mismatch by ~10 000.

## 4. The OP Convergence Trap

Open-loop OP analysis on a high-gain opamp is **mathematically singular** — any `VOUT` between the rails is a valid Newton solution given the right input voltage, so Newton always picks a rail. To force the intended bias point you need ALL of:

1. `.option srcsteps=10` — ramp every voltage source from 0 in 10 steps so Newton walks continuously through the operating-region transitions.
2. `.option itl1=300 itl6=200` — give Newton more iterations to escape pathological initial guesses.
3. `.nodeset` on **every internal node** with the lowercase node name. For this opamp:
   ```
   .nodeset v(ibias)        = 0.66
   .nodeset v(xdut.ntail)   = 0.20
   .nodeset v(xdut.n1)      = 1.10
   .nodeset v(xdut.vout1)   = 0.55     $ critical: stage-1 output
   .nodeset v(xdut.ncc)     = 0.90
   .nodeset v(vout)         = 0.90
   ```
4. **Apply `Vos` as VINP DC bias** — set `VVINP = vcm - Vos_systematic ≈ 0.89979` so the open-loop OP lands `VOUT` at mid-rail (0.96 V). With `VINP = VINN`, the OP would still rail because of the residual Vos.

To find `Vos`: do a `.dc VVINP 0.88 0.92 0.0001` sweep with `meas dc vos when v(vout) = 0.9` (see `dc.spi`).

## 5. Compensation — Miller + Nulling Resistor

Without `Rz`:
- Pole 1 (dominant): `p1 ≈ 1/(gm5 · R1 · R2 · Cc)` — set to a few hundred Hz.
- Pole 2: `p2 ≈ gm5 / CL`.
- **RHP zero**: `z = +gm5 / Cc` — kills phase margin by adding gain *and* reducing phase.

With `Rz = 1/gm5`, the zero moves to infinity. With `Rz > 1/gm5`, the zero moves to LHP and adds **positive** phase shift, recovering PM.

We picked `Rz = 1.6 kΩ` (slightly more than `1/gm5 = 1.46 kΩ`). The result was PM = 63.7° vs 57° at `Rz = 1 kΩ`.

| `Rz` | PM | GBW |
|---|---|---|
| 1.0 kΩ | 57° | 15.5 MHz |
| 1.6 kΩ | 64° | 15.6 MHz |

## 6. AC Phase Calculation Quirks

The open-loop transfer `VOUT/VINP` is **inverting** (DC phase = 180°). At UGF, ngspice's `vp(vout) * 180/π` gives a value in (-180°, 180°]. With phase rolling 180 → 90 → 64° (still positive), the simple formula `pm = 180 + phase_ugf` is wrong (gives 244°). The correct rule for an inverting transfer is:

```
   PM  =  phase_ugf       (when phase is in 0..180° range, which it is here)
```

For a more robust meas-tool-friendly version: use ngspice's `cph()` for unwrapped phase, then `PM = phase_ugf - phase_DC + 180°`.

## 7. Transient TB — Use a Behavioural E-Source for Feedback

Two-stage opamp transient TB needs CLOSED-LOOP feedback to bring `VOUT` to a meaningful operating point. The cleanest is unity-gain buffer:

```
EFB    VINP   0      vol = 'v(VOUT)'      $ NOTE: VINP, not VINN — see polarity
```

Because `VINP` is the **inverting** input of this opamp (open-loop is inverting from VINP → VOUT), feedback goes there to make a follower. Driving stimulus on `VINN` gives `VOUT ≈ VINN` with PM = 64°, ringing < 1 %.

For slew measurement use:
```
let svd  = abs(deriv(v(vout)))
meas tran sr_pos MAX svd FROM=500n TO=600n
```
NOT `meas WHEN`-style threshold crossing — `meas` rejects expressions on the RHS, and a 60° PM step still rings slightly so threshold crossings are unreliable.

## 8. Noise TB — Three Pitfalls

1. **KLU not supported**. Add `.option sparse` to noise.spi (or `unset klu` in `.control`, but that may crash on headless systems).
2. **`meas noise` doesn't exist**. `meas` is limited to tran/dc/sp/ac. Spot values must be extracted by vector indexing of `inoise_spectrum[i]` / `onoise_spectrum[i]` after `setplot noise1`.
3. **Integrated RMS via `integ()`** of the cumulative integral, then index at the upper-band frequency. The `4th` positional argument of `noise` (`pts_per_summary`) must be set to enable the per-frequency summary that populates the spectrum vectors at every analysis frequency.

```
noise v(VOUT) VVINP dec 50 1 1G 1     ; <-- last "1" enables full spectrum
setplot noise1
let vn_in_rt = sqrt(inoise_spectrum)
let v2_in_cum = integ(inoise_spectrum)
let vn_in_rms_to_GBW = sqrt(v2_in_cum[358])     ; index of ~16 MHz
```

**Caveat about integration upper bound**: input-referred noise blows up beyond `f3dB` (where open-loop gain rolls off but output noise PSD doesn't drop as fast). Integrating input-referred PSD over `[1 Hz, 1 GHz]` gives a non-physical RMS larger than the supply rail. Always integrate over a meaningful upper bound (typically the **closed-loop** bandwidth, e.g., GBW for unity-gain).

## 9. Numerical Results

OP (typical, 27 °C, 1.8 V):
- Branch currents: stage 1 = 10 µA, stage 2 = 93 µA, total IDD ≈ 113 µA
- `gm1 = 210 µS`, `gm5 = 687 µS`
- `gds2+gds4 = 2.1 µS`, `gds5+gds6 = 5.3 µS`
- `A1 = 100`, `A2 = 130`, `A_total = 13 000` → **82 dB**

AC (CL = 1 pF):
- DC gain = **82.1 dB**
- f3dB = 1.27 kHz
- GBW = **15.6 MHz**
- PM = **63.7°**

Tran (closed-loop, CL = 1 pF):
- 10 mV step: < 1 % overshoot
- 300 mV step: SR ≈ **47.5 V/µs** peak (Miller-cap-limited)

Noise:
- Spot input-referred at 1 MHz = **155 µV/√Hz** (white floor)
- Spot input-referred at 1 Hz = 2.29 mV/√Hz (1/f corner well above 100 Hz)
- Integrated `[1 Hz, 1 kHz]` = **23 mV RMS** input-referred — design is noise-limited by small input-pair area, not by topology.

## 10. To-Do for Future Iterations

- **Bigger input pair** (`W = 200, L = 2`) for noise reduction. This reduces gm/Id slightly but should drop input-referred 1/f noise by ~10×.
- **Replace EFB with realistic feedback network** (R divider + Rfb) for closed-loop characterisation in non-unity gain.
- **Add a startup kicker** to guarantee the bias loop converges to the intended equilibrium.
- **Add corner sweep** (Kss/Kff) and **MC** (Kttmm) — same templates as Cherry-Hooper.
- **Settling-time meas** at 0.1 % using `WHEN ... CROSS=LAST` after defining a band vector.
