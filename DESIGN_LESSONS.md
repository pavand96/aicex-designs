# Analog/Mixed-Signal Design Lessons Learned

A running log of recurring mistakes, gotchas, and verified practices
encountered while designing SKY130A analog blocks with ngspice + cicsim.
Read this before starting the next design.

---

## 1. Workspace / Repository Hygiene

### 1.1 Don't keep two copies of the same design in different trees
**Problem encountered**: `ip/lelo_fda_miller_sky130a/` and root
`lelo_fda_miller_sky130a/` had **completely different netlists** (different
input pair sizing, stage-2 topology, compensation). Hours wasted debugging
which one was "current".

**Practice**: One canonical netlist per design. If you must have a vendor /
IP copy, keep it read-only and only edit the working tree. Add a header
comment to each `.spice` file noting "STATUS: current" or "STATUS: archived".

### 1.2 Always `.gitignore` simulation outputs
`.raw`, `.logm`, `output_*/` directories balloon to GB-scale and bloat
git history. Pattern:
```
*.raw
*.logm
**/output_*/
```

---

## 2. cicsim-specific gotchas

### 2.1 Testbench filenames cannot contain underscores
`cicsim run cmfb_pm ...` → `Testbench name cannot contain '_'`.
Use `cmfbpm`, `clpm`, etc.

### 2.2 Corner tokens must be separated
**Wrong**: `cicsim run ac Sch GtKttTtVt` (parses as one token)
**Wrong**: `cicsim run ac Sch typ` (typ is not a defined corner → no PDK includes → `unknown subckt` error)
**Right**: `cicsim run ac Sch Gt Ktt Tt Vt` — each corner token separate

The "typ" alias is NOT defined in cicsim by default. Use the full
`Gt Ktt Tt Vt` sequence (gates, transistors, temperature, voltage).

### 2.3 cicsim copies bench `.spi` to output dir and runs from there
Therefore include paths in your bench must be:
- `.include ../../../work/xsch/MYDESIGN.spice` (back to repo root, 3 levels up from `output_<bench>/`)
- `.include ../xdut.spi` (one level up to `sim/MYDESIGN/`)

Don't use absolute paths — they break portability.

### 2.4 Never include `xdut.spi` twice
A duplicate `.include ../xdut.spi` causes `device already exists, bail out`.
Easy to introduce when copy-pasting between benches. Always grep:
```
grep -c "include.*xdut" mybench.spi   # should be exactly 1
```

---

## 3. ngspice gotchas

### 3.1 Noise spectra are ASD (V/√Hz), NOT PSD (V²/Hz)
**ngspice `inoise_spectrum` and `onoise_spectrum` return amplitude
spectral density**, units V/√Hz. To get integrated RMS noise:

```
let inoise_psd = inoise_spectrum * inoise_spectrum
let in_cum = integ(inoise_psd)
let vrms = sqrt(in_cum[length(in_cum)-1])
```

**Wrong** (forgets to square): `vrms = sqrt(integ(inoise_spectrum))` →
gives a number ~10–100× too small.

**Wrong** (forgets to take sqrt): `vrms = integ(inoise_spectrum^2)` →
gives V², not Vrms.

**Verification trick**: simulate a resistor divider and check
`onoise_spectrum / inoise_spectrum = |H|`. If you see `|H|²` you've
confused ASD with PSD. (ngspice gives `|H|`, confirming ASD.)

### 3.2 `inoise_spectrum` is already input-referred
Don't divide by gain again. It's `onoise / |H(s)|`.

### 3.3 `.option sparse` is required for noise analysis
KLU (the default solver) doesn't support noise. Without `sparse` you get
silent garbage or convergence failures.

### 3.4 SIN voltage source: only one tone per source
**Wrong**: `Vsig n 0 SIN(0 0.25 1e6) SIN(0 0.25 1.1e6)` — only the first
tone is recognized, no error.
**Right**: two separate sources summed through resistors:
```
V1 t1 0 SIN(0 0.25 1e6)
V2 t2 0 SIN(0 0.25 1.1e6)
R1 t1 sum 1k
R2 t2 sum 1k
```

### 3.5 FFT spectral leakage requires `tstart` and on-bin tones
For a two-tone IM3 sim:
- Choose tone frequencies that are exact multiples of `1/T_window`.
  E.g., 100 µs window → tones at multiples of 10 kHz → 1.0 MHz and
  1.1 MHz on-bin.
- Use `tran tstep tstop tstart` form to **discard the settling
  transient** from the FFT:
  ```
  tran 5n 300u 200u uic
  ```
  Without `tstart`, the early settling junk leaks into the spectrum and
  makes the two fundamentals unequal (saw 7 dB asymmetry).

### 3.6 `linearize` before `spec` (FFT)
`spec start_freq stop_freq npoints signal` requires uniformly-spaced
time samples. Variable-step `tran` output must be `linearize`-d first.

### 3.7 Convergence: tran preamble + .ic + .nodeset
The reliable pattern for circuits with bias loops / CMFB:
```
.nodeset v(xdut.somenode) = guess_value     # multiple, one per internal node
.ic      v(xdut.somenode) = guess_value     # same guesses for tran initial state
...
.control
tran 10n 200u uic    # transient with UIC — lets CMFB settle organically
op                   # re-OP from the settled state
ac dec 100 100 10G   # or noise / further analysis
.endc
```
Source stepping (`srcsteps=20`) often fails at FF/SS corners where
gm spreads are extreme. The tran preamble bypasses the OP solver.

### 3.8 `meas ... WHEN x=0 CROSS=1` fails silently if there's no crossing
The signal may not cross zero in the simulated range. Always print a
spot value (e.g., `print mag_at_1M`) to sanity-check before relying on
`meas`. Use `MAX` / `MIN` measures as a fallback.

### 3.9 `m=xx on .subckt line will override multiplier m hierarchy`
Harmless warning, but informational: SKY130 sub-circuits accept `m=`
to multiply transistor count. If your top-level instance passes `m=1`
explicitly, this warning fires. Ignore.

---

## 4. Simulation methodology

### 4.1 Open-loop vs closed-loop benches — both are needed
Specs split into two categories:
| Open-loop | Closed-loop |
|-----------|-------------|
| DC gain | IM3 / SFDR / THD |
| GBW | Closed-loop differential PM |
| Phase margin (worst-case β=1) | CMFB PM |
| Slew rate (large-signal) | Settling time |
| Open-loop noise | Closed-loop linearity |

**Common mistake**: writing only open-loop benches because they're
simpler, then claiming the design meets a closed-loop spec.

### 4.2 Closed-loop PM can be extracted from open-loop AC
If feedback factor β is real and frequency-flat (resistor divider):
- CL PM = 180° + ∠A(jω) at |A| = 1/β
- For unity-gain (β=1), CL PM = open-loop PM at UGF
- For β=0.5 (1MΩ/1MΩ inverting), CL PM = phase at |A|=6 dB

No need for a separate sim if open-loop Bode is available.

### 4.3 Slew rate test must fully steer the diff pair
**Wrong**: ±75 mV step when Vov ≈ 89 mV. Diff pair only partially
unbalanced → SR is just small-signal slew, much lower than the real
large-signal SR.
**Right**: ±300 mV diff step (≥ 3–4× Vov). Tail current fully
commutates to one side. Compare result to analytical I_tail/Cc.

### 4.4 Always run a "sanity check" calculation
For every measured spec, have an analytical estimate handy:
- DC gain ≈ gm1·(ro1‖ro3) · gm5·(ro5‖ro6) (for 2-stage)
- GBW = gm1 / (2π·Cc)
- SR = I_tail / Cc (per output) ≈ 2× that differentially
- en,in (thermal floor) = √(8kT·γ / gm1) where γ ≈ 2/3
- Loop gain at f1 ≈ |A(f1)| · β  (drives distortion suppression)

If sim is > 2× off from the back-of-envelope, debug the bench, not the
circuit.

### 4.5 IM3 needs LOOP GAIN at the tone frequency, not at DC
A 74 dB DC-gain opamp with 144 MHz GBW has only 20 dB gain at 1 MHz.
Closed-loop with β=0.5, loop gain = 14 dB. Distortion suppression is
about (1+T) ≈ 5×. To hit −60 dBc at 1 MHz from a stage that's −22 dBc
open-loop, need 38 dB more loop gain → either 3-stage topology or
GBW > 10 GHz.

**Lesson**: GBW is not just a "speed" spec — it directly sets HF
distortion. Estimate loop gain at signal band BEFORE committing to a
topology.

---

## 5. SKY130A PDK-specific

### 5.1 PFET Vt is HIGH (~0.95 V)
A PMOS common-source at the top of a 1.8 V supply has limited headroom.
With NMOS input pair, the stage-1 output sits HIGH (~0.7–0.8 V), which
is wrong polarity for driving a PMOS-CS gate. Pick NMOS-CS at the
bottom instead.

### 5.2 NMOS LVT (`nfet_01v8_lvt`) Vt ≈ 0.3 V
Useful when a node has wide PVT spread but the device must stay in
saturation. Trades higher off-state leakage for headroom robustness.

### 5.3 1/f noise corner is high (~100 kHz at typical sizes)
For any low-frequency analog (noise spec down to 1 Hz), 1/f dominates.
Mitigations:
- Increase input pair WL (reduces 1/f by ~1/(WL))
- Use PMOS input (slightly lower KF in SKY130 PMOS)
- Chopper stabilize / CDS
- Higher low-freq integration bound (if spec allows)

### 5.4 Mismatch corner files
`*_mismatch.corner.spice` adds Pelgrom-style mismatch to each device.
Required for Monte Carlo. Already included by cicsim when using `Kttmm`
(Kxxmm = mismatch enabled).

---

## 6. CMFB design pitfalls

### 6.1 Choksi-Carley CMFB has modest loop gain
Don't expect VCM_out = VCMREF to machine precision. ±50–100 mV offset
is normal. If you need tighter, use an opamp-based CMFB or increase
the sense-pair transconductance / mirror length.

### 6.2 CMFB polarity must match stage-2 device flavor
If `vctrl` drives PMOS sources at top: VCM↑ → vctrl↑ → less |Vgs| →
less current sourced → VOUT↓. **Negative feedback**.

If `vctrl` drives NMOS sinks at bottom: VCM↑ → vctrl↑ → more current
sunk → VOUT↓. **Negative feedback** (opposite polarity needed in the
sense circuit).

Always trace polarity end-to-end before tape-out. Wrong polarity =
latched outputs at one rail.

### 6.3 Startup latch / dead equilibrium
2-stage opamps with both stage-1 outputs floating high can latch in a
no-current state. Fixes:
- 5–10 MΩ pull-down on stage-1 outputs (DC: < 0.2% of branch current,
  AC: negligible because >> ro)
- Startup current injection circuit (more area)

### 6.4 CMFB loop bandwidth must be much lower than diff signal bandwidth
Otherwise CMFB tries to track differential transients and degrades
linearity. Typical: CMFB BW = GBW/5 to GBW/10.

---

## 7. Topology checklist for next 2-stage opamp

Before sizing any device, check:

- [ ] Where does the bias come from? Is there a real bias mirror, or am
      I using `IBIAS` directly as a gate (bad — couples bias noise into
      signal path)?
- [ ] Stage-1 output sits HIGH or LOW? Pick stage-2 flavor accordingly
      (NMOS-CS for HIGH gate, PMOS-CS for LOW gate).
- [ ] CMFB drives which device? Verify polarity end-to-end.
- [ ] Pull-down/startup resistor on stage-1 outputs?
- [ ] Compensation: Cc and Rz computed from analytic GBW & PM target?
- [ ] Is there a long-L device anywhere to fix bias node against PVT?
- [ ] Input pair WL big enough for 1/f noise spec? Check budget at 1 Hz.
- [ ] Loop gain at signal-band frequency (not just DC) supports
      distortion spec?

---

## 8. Debugging recipes

### 8.1 "Op convergence failed at FF/SS corners"
1. Tighten `.nodeset` to the actual settled values from the typical
   corner OP sim.
2. Try a longer tran preamble (`tran 10n 500u uic`) to bypass OP
   solver entirely.
3. Reduce `srcsteps` from 20 → 50 (more granular source stepping).
4. As last resort, add `set noinit` and bump `gmin`.

### 8.2 "Simulation is silent or hangs"
1. `ps aux | grep ngspice` to confirm it's running.
2. `tail -f output_*/run.log` to see real-time progress.
3. If 0% CPU for > 30 s, it's stuck in PDK library parsing or a
   solver loop — kill and inspect.

### 8.3 "Measurement returns 0 or NaN"
1. Print spot values from the vector first: `print sig[100]`.
2. Check the `meas` syntax — `WHEN x=0 CROSS=1` only works if the
   signal actually crosses zero in [tstart, tstop].
3. Always `echo` the meas variable name before printing.

### 8.4 "Numbers match but make no physical sense"
1. Cross-check units (V/√Hz vs V²/Hz, dB vs dBc, peak vs rms).
2. Re-derive with back-of-envelope.
3. Try a simpler test circuit (resistor divider, ideal cap) to
   validate the testbench infrastructure before debugging the DUT.

---

## 9. Documentation discipline

- Update `SIGNOFF.md` AND `DESIGN_NOTES.md` after every change that
  affects results. Stale docs cause re-runs.
- Always include the corner string and the date next to numbers.
- Note FAILED specs explicitly with the gap (e.g., "78.9 vs 50 µVrms
  spec — FAIL by 58%"). Don't bury failures in narrative text.

---

## 10. Common false-positive "fixes"

- **"Just increase IBIAS"** — raises GBW and SR but degrades noise
  (gm1 scales as √I; en² scales as 1/gm; net en² flat with I).
- **"Just lower Cc"** — raises GBW but tanks PM and changes loop gain
  vs frequency profile.
- **"Just widen the input pair"** — improves 1/f noise but adds Cgs
  load on the previous stage, shifts poles, and may break compensation.

Always run the full corner sweep after any sizing change. Single-corner
"improvements" routinely fail at 1–2 PVT corners.

---

## 11. CMFB topology has a startup / OP-degeneracy problem

**Lesson learned on `lelo_fda_foldedcascode_sky130a` (folded-cascode FDA
with NMOS-input Choksi-Carley CMFB).** Sizing got TT to 84.7 dB / 55 MHz
/ 51° PM (up from 47 dB), but **9 / 25 corners latched at V_OUT = 0 V**,
mostly hot-temperature corners.

### 11.1 Recognize the latch pattern
Symptoms in the `.log`:
- `v(voutp) ≈ 1e-4` (essentially zero)
- `v(...vctrl) ≈ 0`
- `dc_gain_db` large negative (–150 to –200 dB)
- AC measurements `out of interval` because phase never crosses 0

This is **not a solver artifact** — it is a true second DC equilibrium
of the circuit. Tightening `nodeset`, `gmin`, or extending the tran
preamble does not help; the OP is self-consistent.

### 11.2 Why an NMOS-input CMFB latches
With sense pair gates tied to V_OUTP/V_OUTN, when V_OUT collapses to
0 V the sense devices go into cutoff. The CMFB tail current then flows
**entirely** through the VCMREF-side branch, which pulls vctrl low,
which turns off the output-stage NMOS sink, which leaves V_OUT at 0 V.
A perfectly stable bad equilibrium.

### 11.3 Anti-latch hacks that do NOT work
| attempted hack                             | failure mode                         |
|--------------------------------------------|--------------------------------------|
| 50 MΩ – 1 GΩ resistor V_OUT → VCMREF       | either no effect, or fights the     |
|                                            | CMFB and drops gain by 20+ dB        |
| Resistor leak vctrl → pbias                | pbias node also collapses at hot    |
| Bigger CMFB compensation cap               | addresses stability, not OP issue    |
| PMOS "rail-to-rail helper" with            | wrong sign — provides positive       |
| gate=V_OUT, src=VDD, drn=vctrl             | feedback that drives V_OUT toward 0  |

The first three hurt the working equilibrium. The fourth is a polarity
trap: if you try to inject a "lift vctrl when V_OUT is low" current,
think through the loop sign before committing — the helper has to sit
on the *opposite* side of the CMFB sense pair (PMOS-input pair sensing
V_OUT), not in parallel with the NMOS sense pair.

### 11.4 Real fixes (when this matters)
- **PMOS-input CMFB** — gate=0 V drives the PMOS strongly ON, so the
  "V_OUT = 0" point is no longer an equilibrium.
- **Rail-to-rail CMFB** — NMOS *and* PMOS sense pairs in parallel. At
  least one pair is always active for any V_OUT ∈ [0, VDD].
- **Switched-cap CMFB** — deterministic discrete-time OP, no
  continuous-time degeneracy possible.

### 11.5 Practice
- **Always check V_OUT and V_CMFB-control node in the OP printout**,
  on every corner, before trusting AC numbers. If V_OUT is within
  10 mV of either rail, the sim has latched even if AC "completes".
- **Add a startup-equilibrium check to the corner-sweep summary**
  (e.g., flag `|V_OUT − V_OCM_target| > 200 mV`).
- **Pick the CMFB topology with the OP-degeneracy question in mind**,
  not just gain/BW/noise. An NMOS-input CMFB driving an NMOS sink is
  a common textbook block but has this exact failure at hot/fast
  PMOS corners.

---

## 12. Polarity sanity check before adding any "helper" device

Before adding a startup device, anti-latch leak, or any cross-coupled
helper, **trace the small-signal sign all the way around the loop**
on paper. A surprising number of "obvious" anti-latch fixes are
actually positive feedback that worsens the bad equilibrium:

- "Lift vctrl when V_OUT drops" → only NFB if the path is
  V_OUT → (–) → vctrl → (–) → output sink → (+) → V_OUT.
  If the helper inserts a (+) where you needed (–), you have made the
  latch *more* attractive.
- The cleanest sanity check: simulate the helper alone with the main
  CMFB *disconnected* and verify that perturbing V_OUT by ±50 mV
  produces a vctrl change in the *correcting* direction.

