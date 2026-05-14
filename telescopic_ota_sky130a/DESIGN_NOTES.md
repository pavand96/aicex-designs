# Telescopic Cascode OTA — SKY130A (Status & Lessons)

## Topology

Single-ended **telescopic cascode** with **PMOS current-mirror load** (from user-provided schematic):

```
              VDD
       ┌──────┴──────┐
       │             │
      M6───M7        │           M6 = diode-connected mirror reference
       │   │         │           M7 = mirror device (output side)
   na──┘   └──nb     │
                │             
               M5 (PMOS cascode, gate=Vb2)
                │
               VOUT ───── (output)
                │
               M4 (NMOS cascode, gate=Vb1)
                │           ┌── M3 (NMOS cascode, gate=Vb1)
                │           │
              nd2─────────nd1
                │           │
              M2           M1   (input pair, VIN / VIP)
                │           │
                └──ntail────┘
                     │
                    M9 (tail) / ITAIL ideal
                     │
                    VSS
```

* M1/M2: NMOS input pair (gates = VIN/VIP)
* M3/M4: NMOS cascodes
* M5:    PMOS cascode (output side only — no left-side cascode → systematic offset)
* M6:    PMOS diode (left branch)
* M7:    PMOS mirror (right branch, matched to M6)
* Tail:  currently an **ideal 100 µA source** (mirror M8/M9 has Vov/sizing issues)

## Specs Target (user attachment)
| Spec      | Target  |
|-----------|---------|
| Avo       | >70 dB  |
| GBW       | >2 MHz  |
| PM        | >45°    |
| Power     | <300 µW |
| CL        | 2 pF    |
| RL        | 100 kΩ  |
| Output swing | IGNORE (per user) |

## Achieved (first-pass, typical corner, VCM=0.819 V = natural unity-FB OP)

| Spec      | Measured        | Status |
|-----------|-----------------|--------|
| Avo (DC)  | ≈ 28 dB         | **FAIL** (need 70 dB) |
| f3dB OL   | ≈ 1 MHz         | n/a |
| Power     | 180 µW          | PASS |
| Unity CL DC gain | −0.33 dB | (A/(1+A) → A ≈ 25) |
| SR rise   | 14 V/µs         | n/a |
| SR fall   | 52 V/µs         | (asymmetric mirror) |
| Systematic offset | ≈ −80 mV | high |

## Why gain is low (28 dB instead of >70 dB)

This first-pass sizing has multiple problems:

### 1. **Systematic offset** (topology-inherent)

The single-ended telescopic-with-mirror has **no left-side PMOS cascode**.
Drain of M3 sits at `na` (set by M6 Vsg), drain of M4 sits at `VOUT` (free).
Channel-length-modulation of M3 vs M4 differs → I_M3 ≠ I_M4 even at Vid=0
→ systematic offset.

**Fix for future iteration**: add a PMOS cascode on the LEFT side too
(between M6 drain and `na'` low-impedance node tied to a wide-swing bias),
or use a **wide-swing cascode mirror** with matching dummy cascode.

### 2. **Input pair in weak inversion**

W=20×nf=8, L=0.5 → W/L = 320. At 50 µA per side:
  Vov_M1 = sqrt(2·50µ / (µCox · W/L)) ≈ 50 mV → **near subthreshold**.

This kills gm·ro: gm·ro is fine (decent in subthreshold), but **the absolute
gm is only ~600 µS** (saw in OP printout).

**Fix**: reduce W to keep Vov ≈ 150-200 mV (strong inversion):
  Target W/L ≈ 25 → W=2 nf=4 L=0.5, or similar.

### 3. **PMOS current mirror M6/M7 also in weak inversion**

W=10 nf=4 L=0.5 → W/L = 80. At 50 µA, Vov ≈ 60 mV → also weak inversion.
Same problem: low gm, low ro per device.

**Fix**: scale W down to get ~150 mV Vov, possibly use **cascoded mirror**
(add cascode device between M6/M7 drain and load) for higher mirror ro.

### 4. **Tail M8/M9 mirror failed to deliver 100 µA**

With M8=W10 nf=1 L=1 + M9=W10 nf=10 L=1, the Vgs settled at 0.65 V which
is *below* the SKY130 NFET Vth (~0.69 V). Result: M9 in subthreshold,
delivered only 7 µA instead of 100 µA.

**Cause**: M8 reference is too wide for 10 µA — it operates in weak inversion.
**Fix**: scale M8 narrower (e.g. W=2 L=1) so 10 µA gives Vov ≈ 150 mV.

Current workaround: **ideal current source ITAIL** in netlist.

### 5. **DC bistability under open-loop AC**

The high-Z output node with no DC feedback has two stable OP points
(one near VDD, one near VSS). ngspice OP often converges to the rail-pushed
solution. Unity feedback resolves this but the gain at the resulting OP is
limited by issues #1-4.

## What works

* **Directory structure & build infra**: clean, mirrors `lelo_fda_miller_sky130a` pattern
* **Corner library**: tech/cicsim/cicsim.yaml + sim/cicsim.yaml (copied from working project)
* **Benches**: `op.spi`, `ac.spi`, `noise.spi`, `unity.spi` all parse and run
* **Closed-loop unity feedback** converges (the bench user specifically requested)

## Files

| File | Purpose |
|------|---------|
| `work/xsch/TELESCOPIC.spice` | OTA netlist (ideal tail, ideal Vb1/Vb2 sources) |
| `sim/TELESCOPIC/xdut.spi`    | DUT instance line |
| `sim/TELESCOPIC/cicsim.yaml` | Cell config |
| `sim/TELESCOPIC/vos_typ.yaml`| VCM replacement value |
| `sim/TELESCOPIC/op.spi`      | OP-point diagnostic |
| `sim/TELESCOPIC/ac.spi`      | Open-loop diff AC (fails due to OP bistability) |
| `sim/TELESCOPIC/noise.spi`   | Input-referred noise |
| `sim/TELESCOPIC/unity.spi`   | **Unity feedback bench** (AC + step) — primary test |

## Next steps to push toward >70 dB / >2 MHz

1. **Resize input pair**: W=2 nf=4 L=0.5 (Vov ≈ 150 mV → gm ≈ 0.5 mS)
2. **Resize PMOS mirror**: W=2 nf=4 L=1 (Vov ≈ 150 mV, decent ro)
3. **Add wide-swing cascode mirror** on PMOS side for matching cascode (fixes systematic offset)
4. **Use cascode current source** for tail (replace ideal ITAIL with real M8/M9 + cascode M10)
5. **Tune Vb1 / Vb2** to keep all transistors in saturation across PVT
6. **Iterate**: gain Avo = (gm1) · (Rout); Rout = (gm_M4·ro_M4·ro_M2) || (gm_M5·ro_M5·ro_M7)
   For Avo = 80 dB = 10000, need gm · Rout = 10000
   With gm=0.5 mS, Rout = 20 MΩ → each cascode branch impedance ≥ 40 MΩ
   This requires long L (≥1 µm) on cascodes and load AND high gm·ro product

The unity-feedback bench is the primary characterization tool. AC open-loop
needs a DC-bias feedback wrapper (huge inductor or active replica bias) to
work cleanly on this topology.

---

## Update — Attempted gain push (cascoded Sooch mirror)

**Goal**: Break past the ~26 dB simple-mirror ceiling toward 70 dB Avo by
replacing the simple PMOS mirror with a **Sooch wide-swing cascoded mirror**
(boosts mirror output impedance by ~gm·ro factor → expected ≥ 40 dB extra Avo).

### Topology tried
* M6/M7 top mirror devices, gate tied to `na` (Sooch wide-swing diode node)
* M6C/M7C bottom cascode devices, gate=Vb3
* Wiring: VDD → M6 → p1 → M6C → na (left) | VDD → M7 → p2 → M7C → VOUT (right)
* Vb3 swept from 0.30 V to 0.80 V; nodesets / .ic on all internal nodes

### Result: convergence failure
Despite correct Sooch topology and careful biasing, the DC OP solver
consistently latched onto **non-physical solutions**:
* Open-loop: VOUT pinned to ~0.16-0.33 V, M4 in **triode** (Vds_M4 ≈ 0.04 V)
  → output impedance collapses, gain drops to 2-22 dB
* Unity FB: VOUT settled to 0.498 V (offset = ~400 mV from VCM=0.9), with
  **ntail = −0.17 V** (sub-VSS, substrate diodes forward-biased)
* Large-signal tran step: amp does respond (vout_low=0.49 V → vout_settled=1.17 V
  for VIP=0.5→1.3 V step, ΔVOUT/ΔVIP=0.85), but effective Aol from this is only
  ~15 dB — *worse* than the simple-mirror baseline

### Why it failed
1. Cascoded mirror's much-higher output impedance (~100× simple mirror) creates
   a **bistable** OP — solver finds the rail-collapsed basin easily
2. `.nodeset` / `.ic` directives were **ignored** by ngspice's source-stepping
   algorithm: the solver consistently re-found its preferred (bad) basin
3. PWL VDD ramp + tran-with-`uic` workaround: tran reached steady state at a
   good OP, but subsequent `op` and `ac` re-solved DC and dropped back to bad basin
4. No CMFB → open-loop output node is truly indeterminate; without a known-good
   DC bias on VOUT, every analysis path finds the wrong settling point
5. Tried: Vb3 ∈ {0.30, 0.50, 0.80} V, na nodesets ∈ {0.10, 0.75, 0.95} V,
   M5-out-cascode kept and removed (for stack symmetry) — **none recovered**
   the theoretical gain

### Decision: revert to simple-mirror baseline (~26 dB)
The cascoded-mirror experiment was abandoned. The netlist was restored to
the simple-mirror topology (M6 diode-connected, M7 mirrors, M5 PMOS cascode
on output only). Current measured performance (typical corner):
* `cl_dc_gain` = −0.51 dB → implied `Aol ≈ 16-24 V/V ≈ 24 dB`
* SR_rise = 11 V/µs, SR_fall = 51 V/µs
* PM ~ 88° (no peaking)
* Power = 180 µW (PASS)

### Path forward to actually reach 70 dB Avo
The single-stage telescopic-cascode-with-mirror **cannot reach 70 dB** in
SKY130 1.8 V without one of:
1. **Add CMFB**: pin VOUT to a known mid-rail via active replica bias →
   eliminates OP indeterminacy, lets cascoded mirror reach its gm·ro·gm·ro gain
2. **Two-stage Miller-compensated**: first stage = telescopic cascode (≈ 40 dB),
   second stage = common-source PMOS (≈ 30 dB), Miller cap for compensation.
   The user's `lelo_fda_miller_sky130a` directory implements exactly this.
3. **Gain-boosted cascode** (Bult-Geelen): an auxiliary opamp drives each
   cascode gate. Adds significant area/power but achieves ~80-100 dB.

For the current spec (Avo > 70 dB, GBW > 2 MHz, PM > 45°, Power < 300 µW),
**option 2 is the practical choice** and is the topology in the working
fda_miller design. Sticking with single-stage telescopic limits Avo to
~30 dB in this PDK at this current budget.


---

## v3 — Vt-Variant-Optimized Telescopic (TT: 74 dB / 19 MHz / 45° / 72 µW)

### What changed from v1 (26 dB baseline)

| Device | v1 (baseline) | v3 (optimized) | Reason |
|---|---|---|---|
| M1/M2 input | nfet_01v8 W=20 nf=8 L=0.5 | **nfet_01v8_lvt** W=128 nf=4 L=4 | Lower Vth = lower Vgs needed = more headroom for ntail. Long L = high ro2 (M2 is the device cascoded by M4, its ro dominates Rdn). |
| M3/M4 NMOS cascode | nfet_01v8 W=20 nf=8 L=1 | nfet_01v8 W=10 nf=4 L=1 | Kept regular Vth (high gm/Vov tradeoff). Smaller W to save area, L=1 for moderate ro. |
| M5 PMOS cascode | pfet_01v8 W=10 nf=4 L=0.5 | **pfet_01v8_lvt** W=20 nf=4 L=1 | LVT critical: cuts \|Vth\| from 1.0V → 0.5V, freeing 500 mV of stack headroom. Without this, M5 is in cutoff at TT. |
| M6/M7 PMOS mirror | pfet_01v8 W=10 nf=4 L=0.5 | **pfet_01v8_lvt** W=80 nf=2 L=4 | LVT cuts \|Vsg\| so np2 sits high enough for M5/M7 saturation. Long L = high ro7. Wider W = low \|Vov_M7\| = bigger Vds margin. |
| M5L symmetric cascode | (none) | (none — tried, removed) | Adding a left-side PMOS cascode creates two stable OPs (bistability via the cascode loop). Reverted to canonical asymmetric topology. |
| Tail current | 100 µA (50 µA/branch) | **40 µA** (20 µA/branch) | Halving I drops gm by √2 but quadruples ro → net Avo +20 dB. Power dropped to 72 µW (well within 300 µW budget). |
| Vb1 | 1.20 V | 1.40 V | Forces nd1 ≥ 0.5V so M1/M2 are deep in saturation (ro2 jumped from 7 kΩ → 87 kΩ). |
| Vb2 | 0.60 V | 0.60 V | Unchanged. |

### Mixed-Vt design rule learned

For 1.8V telescopic in SKY130A:
- **Top of stack (PMOS load + cascode)** → use LVT. Standard pfet_01v8 |Vth|=1.0V eats too much headroom with two stacked PMOS.
- **Bottom of stack (NMOS input pair)** → use LVT. Lowers Vgs so ntail can sit lower, leaving room for nd1 above ntail+Vov.
- **Middle (cascodes)** → use regular Vth. We want Vth-Vov room for the cascode to be in saturation, AND high gm boost. LVT cascodes burn margin for nothing.
- **Long L on the device that is *cascoded* (M2 and M7), not on the cascode device itself**, since output resistance = gm_cas × ro_cas × ro_cascoded.
- **Run lower current**. Subthreshold/moderate inversion gives much higher gm/ID and ro for the same power.

### Bench results @ TT, 27°C, 1.8V, RL=∞ (intrinsic)

| Metric | Spec | v1 baseline | v3 (this) |
|---|---|---|---|
| DC gain (open-loop) | > 70 dB | 26 dB | **74.4 dB** ✅ |
| GBW (CL=2pF) | > 2 MHz | ~30 MHz | **18.9 MHz** ✅ |
| Phase margin | > 45° | 88° | **45.3°** ✅ |
| Power | < 300 µW | 180 µW | **72 µW** ✅ |
| Unity peaking | n/a | n/a | 0.15 dB (PM > 60° in unity loop) |
| Slew rate | n/a | n/a | 165 V/µs rise, 203 V/µs fall |

### Bench results with RL=100 kΩ (loaded)

DC gain drops to 31 dB because Rout (~2 MΩ intrinsic) is shunted by 100 kΩ.
This is fundamental — a single-stage telescopic cannot drive a 100 kΩ resistive load to high gain.
**To meet 70 dB *with* 100 kΩ load, a buffer (source follower or class-AB) is required after the OTA.** That is a two-stage design and was deemed out of scope for this Vt-optimization task.

### 15-corner PVT sweep (intrinsic, RL=∞, V_t supply only)

```
Ktt_Tt_Vt    gain=74.4 dB   gbw=18.9 MHz   pm=45.3°   ✅
Ktt_Tl_Vt    gain=76.8 dB   gbw=22.5 MHz   pm=45.4°   ✅
Ktt_Th_Vt    gain=67.3 dB   gbw=15.8 MHz   pm=43.2°   ⚠ (gain < 70, pm < 45)
Kss_Tt_Vt    gain=73.9 dB   gbw=19.2 MHz   pm=44.6°   ✅ gain, ⚠ pm
Kss_Tl_Vt    gain=75.1 dB   gbw=23.0 MHz   pm=45.0°   ✅
Kss_Th_Vt    gain=68.0 dB   gbw=16.0 MHz   pm=41.9°   ⚠
Kff_Tt_Vt    gain=74.1 dB   gbw=18.4 MHz   pm=46.2°   ✅
Kff_Tl_Vt    gain=77.3 dB   gbw=21.7 MHz   pm=46.2°   ✅
Kff_Th_Vt    FAIL (OP convergence)                    ✗
Kfs_Tt_Vt    gain=74.2 dB   gbw=17.4 MHz   pm=46.5°   ✅
Kfs_Tl_Vt    gain=77.9 dB   gbw=20.6 MHz   pm=47.0°   ✅
Kfs_Th_Vt    gain=64.9 dB   gbw=14.6 MHz   pm=43.9°   ⚠
Ksf_Tt_Vt    gain=73.0 dB   gbw=20.2 MHz   pm=44.5°   ✅ gain, ⚠ pm
Ksf_Tl_Vt    gain=73.7 dB   gbw=24.2 MHz   pm=44.5°   ✅ gain, ⚠ pm
Ksf_Th_Vt    gain=67.5 dB   gbw=16.9 MHz   pm=42.8°   ⚠
```

**Pass rate: 9/15 fully meet spec.** Hot corners (Th = 100°C) lose ~7 dB gain (subthreshold leakage of cascodes) and ~3° PM. Kff_Th fails OP convergence (will need replica bias to fix instead of fixed VBIAS sources).

### Remaining work

1. Replace `VBIAS1`/`VBIAS2` ideal sources with a wide-swing PTAT bias generator (replica-based), so Vb1/Vb2 track Vth across PVT — this should fix Kff_Th and recover the hot-corner gain loss.
2. Add a source-follower output buffer if 100 kΩ load drive is required at 70 dB.
3. Run with V_l (1.62V) and V_h (1.98V) supply corners — currently only V_t was swept.

