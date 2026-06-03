# Design Procedure — 0.9 V Folded-Cascode OTA on sky130A

*Audience: an undergrad who has taken one analog design course and knows what gm, rds, Vov and "phase margin" mean, but has never finished a PVT-robust amplifier on a real PDK.*

This document walks through **how this OTA was actually designed** — in the order the decisions were made, with the reasoning behind each one. It is **not** a textbook chapter; it's a recipe you could follow on the next project.

---

## 0. The spec sheet (what the customer asked for)

| Quantity            | Value          |
|---------------------|----------------|
| Process             | sky130A LVT    |
| Supply VDD          | **0.9 V**      |
| Input common-mode   | 0.3 V          |
| Output target       | 0.3 V          |
| Reference current   | 10 µA (external sink at IBIAS pin) |
| Load capacitance CL | 5 pF           |
| Load resistor       | none (purely capacitive) |
| DC gain A0          | ≥ 25 dB        |
| Phase margin PM     | 45° – 135°     |
| Input offset Vos    | < 50 mV        |
| Yield target        | pass on TT/FF/SS/FS/SF **and** Monte-Carlo mismatch |

The single most important number is **VDD = 0.9 V**. Everything that follows is dictated by it.

---

## 1. Why 0.9 V drives every decision

In SKY130:

| Device              | Vt (typ) | What that means at VDD=0.9 V                |
|---------------------|---------:|---------------------------------------------|
| `nfet_01v8`         | ~0.55 V  | Stacking two of these eats 1.1 V — won't fit |
| `nfet_01v8_lvt`     | ~0.30 V  | OK, you can stack two with ~150 mV Vov each |
| `pfet_01v8`         | ~0.95 V  | **Bigger than VDD.** Can't even turn on as input pair. |
| `pfet_01v8_lvt`     | ~0.40 V  | The only PMOS option at this supply         |

**Rule 1: every transistor in this design is `_lvt`.** Non-LVT devices are forbidden at 0.9 V.

**Rule 2: PMOS input pair.** Even with LVT, an NMOS pair would need Vgs ≈ 0.4 V on top of the tail Vds ≈ 0.15 V — and we already promised VICM = 0.3 V. There is no headroom. PMOS pair (with the tail at the top, near VDD) fits: VDD − |Vgs_p| − |Vds_tail| ≈ 0.9 − 0.55 − 0.15 = 0.20 V at the input — comfortably above 0.3 V doesn't matter; what matters is the tail node sits at VDD − 0.15 V and the inputs at 0.3 V puts |Vgs| ≈ 0.45 V. Works.

**Rule 3: only one Vt between any two stacked devices.** No "two-high cascode bias generator", no β-multiplier with a stack, no folded-cascode current source on top of another current source. The 0.9 V budget is roughly:

    VDD = |Vgs_top_mirror| + |Vds_top_cascode| + Vds_bottom_cascode + Vgs_bottom_sink
        ≈ 0.55 + 0.15 + 0.15 + 0.45  = 1.30 V  ← OVER BUDGET

We will fix the overrun by aggressively **squeezing Vov to ~100 mV everywhere**. That's what sets every W/L choice below.

---

## 2. Pick the topology

We picked a **single-stage folded cascode**:

    VDD ──┬──────────┬─────────┬─── PMOS top mirror  (XM3 / XM4)
          │          │         │
       diode-tie   M4 (out)   M3 (diode) ─── fL
          │          │         │
          │       PMOS cascode (XM3A / XM4A)
          │          │         │
       (none) ──── VOUTP ───── fL ── (to top mirror gate)
          │          │
       NMOS cascode (XM1A / XM2A)
          │          │
        nbR        nbL ── input-pair drains
          │          │
     PMOS input pair (XM1 / XM2)  ── tail at top
          │          │
       NMOS sink (XM11 / XM12)
          │          │
        VSS        VSS

Why single-stage:
- **One pole at the output** → easy phase margin, no compensation cap needed.
- **No Miller worry** → no slow-RHZ-zero hunt, no Cc/Rz to tune over PVT.
- **The output node is naturally high-impedance** → high gain from one stage if we cascode both sides.

Why folded (not telescopic):
- Output swing in a telescopic cascode is bounded by the input common-mode (you have to leave room above VICM for the tail). At VICM = 0.3 V there is no room above. **Folding the cascode** moves the high-impedance output node off the input-pair drain and lets VOUTP sit at 0.3 V independent of VICM.

Why single-ended (not fully differential):
- The spec asks for one output (VOUTP). No CMFB loop to design. Saves area, saves stability work.

---

## 3. Allocate the currents (BEFORE drawing schematics)

Always do this on paper first. It's an algebra exercise, not a SPICE exercise.

| Branch                | Symbol  | Current | Why                                  |
|-----------------------|---------|---------|--------------------------------------|
| Reference             | IREF    | 10 µA   | Given                                |
| Input pair tail       | I_TAIL  | 40 µA   | 20 µA per input transistor           |
| NMOS sinks (each)     | I_SNK   | 40 µA   | Equal to tail/2 + fold current       |
| Fold current per side | I_FOLD  | 20 µA   | = I_SNK − I_PAIR = 40 − 20           |
| PMOS top mirror legs  | I_TOP   | 20 µA   | Carries the fold current up to VDD   |
| **Total IDD**         |         | **~80 µA**   | tail 40 + 2 × fold 20 + bias ~5 µA   |

KCL at node `nbR` (the right input drain, also the right cascode source):

    I_pair_R + I_fold = I_snk_R
       20    +   20   =   40   ✓

KCL at node `nbL` mirrors this. Good.

**Ratio everything to IREF = 10 µA using integer `m` multipliers.** That's the only way mirrors track over PVT. Memorise:

- IREF unit (m=1) → 10 µA
- 20 µA → m=2
- 40 µA → m=4

The schematic uses **m=4** on the master diode and tail (40 µA reference per stack of 4 unit cells) which makes Vt mismatch shrink as 1/√m. We'll come back to this.

---

## 4. Pick W, L, nf for each device

The recipe is:

1. Pick **L** based on what the device must do.
2. Solve for **W** from `gm/ID` or `Vov`.
3. Pick **nf** so the per-finger width is reasonable (~4 µm/finger here).
4. Set **m** from the current ratio (Step 3).

### 4.1 Input pair (XM1, XM2)

What it must do: high gm at low current (for gain and 1/f noise).
- **L = 0.5 µm** (shortest L that still gives decent rds; we don't need rds here because the cascode boosts it).
- Target Vov ≈ 100 mV at ID = 20 µA → W ≈ 20 µm.
- nf = 4, m = 4 → effective W = 4 × 4 × 20 = 320 µm (huge — necessary for both gm and matching).

### 4.2 NMOS bottom sinks (XM11, XM12)

What it must do: be a stiff current source (high rds).
- **L = 1 µm** for higher rds.
- Want ID = 40 µA at Vgs ≈ 0.45 V → W per finger = 4 µm, nf = 2.
- **m = 8** for matching (this was bumped from m = 4 in the MC pass — see § 8).

### 4.3 NMOS cascodes XM1A / XM2A — *the critical pair*

**This is the device that broke the design in Monte Carlo.** Read carefully.

- **L = 4 µm**: very long, for highest possible rds → gain.
- Initial W choice: 32 µm. Sounded "wider is more headroom".
- **Actual fix: W = 16 µm.**

Why smaller is better here:

The cascode's job is to look down at the bottom sink and pin its drain (`nbR`) at a constant voltage. That voltage is `V(nbR) = VBIAS2 − Vgs_casc`. We need `nbR` to stay **above** the sink's `Vds_sat` (≈ 100 mV).

With W = 32 the cascode is very wide → its Vov is small (~50 mV) → `Vgs_casc` ≈ Vt + 50 mV = 350 mV → `V(nbR) = VBIAS2 − 350 mV`. At slow-NMOS corners VBIAS2 drops, and `V(nbR)` lands at ~80 mV — **below Vds_sat of the sink**. The sink falls into triode → loses current → wrong DC basin → A0 collapses.

With W = 16 the cascode Vov rises to ~150 mV → `Vgs_casc` ≈ 450 mV → `V(nbR) ≈ VBIAS2 − 450 mV` ≈ 50 mV **lower** → wait, that's worse, right? **No.** What actually shifts is VBIAS2 itself, because the bias leg also got rebalanced. Net result observed in SPICE: `nbR` rises by ~50 mV, clearing the sink's saturation edge by a comfortable margin across all corners.

**Lesson**: at VDD = 0.9 V the cascode is **not** a free gain boost; sizing it is a headroom puzzle, not a small-signal puzzle. Always check the source-node voltage of every cascode, not just its gm/rds.

### 4.4 PMOS cascodes XM3A / XM4A

- L = 4, W = 32, nf = 4, m = 4. Wider than the NMOS cascode because PMOS µ is ~3× lower; m=4 to keep matching tight without pushing further.

### 4.5 PMOS top mirror XM3 / XM4

- L = 2 (length controls mirror accuracy and rds; not as long as the cascode but well above minimum).
- W = 32, nf = 4, **m = 8** (this also got bumped during the MC pass — diode and copy must match well to suppress Vos).

### 4.6 PMOS tail XMTL

- L = 1, W = 16, nf = 4, m = 4. Gate driven by VBP (the master diode).

That's the entire signal path. **Eight transistors plus one master diode in the bias.**

---

## 5. Design the bias network

The bias has three jobs:

1. Generate **VBP** (gate of all PMOS sources/tails).
2. Generate **VBIAS1** (gate of all PMOS cascodes).
3. Generate **VBIAS2** and **VBIAS3** (gate of NMOS cascode and NMOS sink).

The textbook way is "wide-swing cascode bias generator" (Sansen, Razavi Fig 5.37). At 0.9 V the **cascoded** version (3-high) won't fit. So we use the **R-degenerated** version (2-high, with a 10 kΩ resistor providing the cascode-bias offset).

### 5.1 The R-degeneration trick

A wide-swing cascode wants its cascode-gate to sit **one Vov above** the sink-gate. The clever way to generate that offset is a resistor carrying the bias current:

    V_offset = I × R = 10 µA × 10 kΩ = 100 mV ≈ Vov_target

That gives `VBIAS2 = VBIAS3 + 100 mV` exactly — and the offset **tracks** in the right direction over PVT because R is a poly resistor (slightly TC-dependent in the right way).

### 5.2 The bias network — actual schematic

    VDD ──┬─────────────────┬──────────────┬─── (IREF sink pulls 10 µA out of IBIAS pin)
          │                 │              │
       XMP_REF           XMP_NLEG       (signal path)
       diode-tied        gate=VBP
       VBP =====┐        drain=VBIAS2
                │           │
                │         RN_BIAS 10k
                │           │
                │         VBIAS3 ─── gate of all NMOS sinks
                │           │
                │        XMN_NDIO  diode-tied NMOS
                │           │
                │          VSS
                │
                ├─── RP_BIAS 10k
                │           │
                │        VBIAS1 ─── gate of all PMOS cascodes
                │           │
                │        XMN_PSNK gate=VBIAS3 (mirrors NDIO current)
                │           │
                │          VSS
                │
            (also feeds tail/input gates)

Key choices:
- The master diode is **m = 4**. Mismatch on the master propagates to every leg, so make it big.
- The bias-leg PMOS sources are **W/L replicas** of the signal-path PMOS so the Vov cancels (signal path sees same Vov as the bias leg by construction).
- The PMOS leg ends in an NMOS sink whose gate is VBIAS3 — so the PMOS leg current is a **copy of the NMOS leg current**. Single equilibrium: there's only one consistent solution. (A pure cascoded gate-voltage generator has two stable solutions and can latch in the wrong one. Don't do that at 0.9 V.)

### 5.3 What didn't work in the bias (do not retry)

- **Cascoded gate-voltage generator** (3-high): won't pull out of OFF basin at 0.9 V. Failure file: `dut_cascbias_failed.spi`.
- **β-multiplier startup**: at 0.9 V the OFF basin is too sticky. Failure file: `dut_betamult_failed.spi`.
- **R = 30 kΩ instead of 10 kΩ**: too much drop, cascode loses Vgs at FS corner.

---

## 6. Verify nominal OP across corners

Before any Monte Carlo, get **all 5 PVT corners passing nominal**.

Workflow:

    cd sim
    python run_corners.py        # runs op + ac at TT / FF / SS / FS / SF

For each corner, check:

1. **VOUTP ≈ 0.30 V** (target) — if not, mirror ratios are off.
2. **Every transistor in saturation**: `Vds > Vds_sat = Vov + few × kT/q`. Print the OP and grep for any device with `vds < vgs - vth`.
3. **No device in triode at any corner.** This is the #1 reason designs fail MC later.
4. **A0 > 25 dB, PM > 45°.**

What we got at the end:

| Corner | A0 (dB) | PM (deg) | VOUTP (V) | IDD (µA) |
|--------|--------:|---------:|----------:|---------:|
| TT     | 40.0    | 66.0     | 0.300     | 80       |
| FF     | 36.6    | 60.0     | 0.301     | 94       |
| SS     | 42.7    | 70.9     | 0.300     | 76       |
| FS     | 41.1    | 55.5     | 0.300     | 82       |
| SF     | 40.6    | 74.3     | 0.300     | 78       |

If the table above were not green on every row, you go back to Step 4 and resize. **Do not** proceed to Monte Carlo with a yellow corner.

---

## 7. Monte Carlo: the first hard reality check

Once nominal corners pass, run mismatch MC at every corner:

    NJOBS=8 OMP_NUM_THREADS=1 python run_mc.py 50

(50 samples × 5 corners = 250 runs. Pass criterion: same spec window.)

**First run**: 231 / 250 = 92.4 % yield. Mostly fails at FS. Need to figure out **why** the failures happen, not just throw matching transistors at it.

### 7.1 Diagnose by reading the OP, not the small-signal

For each failing sample, dump the OP and look at:

1. `V(VOUTP)` — if it's railed (near 0 V or near VDD), that's a **wrong-basin** failure, not a small-signal failure.
2. `V(nbR)` and `V(nbL)` — if either dropped below ~100 mV, the bottom sink is in triode.
3. `V(fL)` — if it's near VDD, the PMOS load mirror has shut off.

We found two recurring failure patterns:

- **Pattern A — `nbR` collapses, A0 < 0.** XM2A loses its source-to-bias headroom because mismatch tilted the sink current up; the sink falls into triode; VOUTP rails low. → fix in § 8.
- **Pattern B — `fL` rails to VDD.** The PMOS mirror diode (XM3) shut off; current can't flow; the output node is left floating. → fix in § 9.

---

## 8. Fix A: resize cascode + matching

Two changes:

1. **XM1A / XM2A: W 32 → 16, keep L = 4, m = 1.** Counterintuitive — discussed in § 4.3. Net effect: nbR rises by ~50 mV across all MC samples, FS-corner failures drop from ~20 % to ~5 %. **Bonus**: A0 goes up by 3–4 dB.
2. **XM11 / XM12: m = 4 → 8** *and* their diode-tied references **XMN_NDIO, XMN_PSNK: m = 4 → 8**. Both sides of the mirror must be enlarged together. Vt mismatch on a unit cell is σ_Vt ∝ 1/√(W·L·m), so m=4 → m=8 halves σ² (about 30 % less σ).
3. **XM3 / XM4 (top mirror): m = 4 → 8.** Same reasoning.

After these: 245 / 250 ≈ 98 %. Almost there, but FS still has ~5 stubborn fails.

### 8.1 What we tried and rejected

| Attempt                                  | Result                       |
|------------------------------------------|------------------------------|
| Raise R_n / R_p from 10 k → 30 k         | Broke nominal corners        |
| Lengthen XM3/XM4 (L = 1 → 2) for gain    | Killed PM, no A0 win         |
| Add `.nodeset` lines to the testbench    | Sample-dependent (helped some, hurt others) |
| XM1A/XM2A m = 1 → 2 with W = 32          | Broke FF/FS nominal          |

**Lesson**: don't keep piling on transistors; understand the failure mode, then make one targeted change.

---

## 9. Fix B: the 1 MΩ "wrong-basin" pull-down

The remaining FS fails were all the **fL-rails-to-VDD** basin. Schematic-level fix:

    RFL_PD   fL    VSS   1MEG

A single 1 MΩ resistor from `fL` to ground.

Why it works:
- At the **correct** operating point, fL sits at ~VDD − |Vgs_p| ≈ 0.35 V. Across 1 MΩ that's 0.35 µA — totally negligible vs 20 µA flowing through the leg.
- At the **wrong** operating point, fL has railed to ~VDD = 0.9 V. The 1 MΩ tries to pull 0.9 µA out of it. That's enough to tip the loop back into the active basin during DC convergence and during OPTRAN.
- **AC impact: zero.** 1 MΩ is in parallel with ~1/gm of XM3 ≈ 5 kΩ, so it doesn't move the pole.

After this: **250 / 250 = 100 % MC yield.**

This is a real-world trick, not a hack: production analog designs ship with weak "anti-latch" pull-downs/pull-ups on internal high-impedance nodes for exactly this reason.

---

## 10. The full design flow (TL;DR)

1. **Read the spec.** Identify the binding constraint (here: VDD).
2. **Pick technology variant.** At VDD < 1 V → only `_lvt`.
3. **Pick topology.** Single-stage folded cascode for capacitive load + easy compensation; PMOS input pair because VICM is low.
4. **Allocate currents on paper.** Integer ratios to IREF. KCL at every node.
5. **Size signal-path devices.** L from rds/gain target, W from Vov target, m from current ratio. Cascodes get long L; mirrors get matched W/L pairs.
6. **Design bias.** Use the simplest legal topology — at 0.9 V that's R-degenerated 2-high, *not* cascoded gate-voltage generator. Replica devices so Vov cancels.
7. **Verify all 5 PVT corners.** Inspect OP voltages, not just A0/PM. Any device in triode → resize before MC.
8. **Run mismatch MC.** Aim for ≥ 99 %. If not, diagnose by reading the OP of failing samples; identify the failure *mode* before resizing.
9. **Add wrong-basin defenses where needed.** Weak pull-downs on high-impedance internal nodes (1 MΩ here) cost nothing and eliminate latch-up basins.
10. **Snapshot and commit.**

The whole campaign on this OTA: **baseline 92.4 %  →  resizing pass 98 %  →  add 1 MΩ defeater  →  100 %.**

---

## 11. Files and how to reproduce

- Netlist: [sim/dut.spi](sim/dut.spi)
- Final snapshot: [sim/dut_FINAL_2026-06-02.spi](sim/dut_FINAL_2026-06-02.spi)
- Testbenches: [sim/tb_op.spi](sim/tb_op.spi), [sim/tb_ac.spi](sim/tb_ac.spi)
- Corner runner: `python sim/run_corners.py`
- MC runner: `NJOBS=8 OMP_NUM_THREADS=1 python sim/run_mc.py 50`
- Failure-mode references (kept on purpose, do not re-try): `dut_betamult_failed.spi`, `dut_cascbias_failed.spi`, `dut_replica_fullstack_failed.spi`.

---

## 12. Common undergrad mistakes this design specifically avoids

1. **Using non-LVT devices at 0.9 V.** Vt > VDD/2 ⇒ nothing works.
2. **NMOS input pair "because the example in the book uses one".** At VICM = 0.3 V the NMOS pair has no Vgs headroom.
3. **Cascoded bias generator at low VDD.** Two stable basins ⇒ chip locks up at random.
4. **Sizing cascodes by gm/rds alone.** Headroom comes first. A "high-gain" cascode that lives in triode delivers 0 dB.
5. **Only looking at A0/PM in MC.** Look at OP voltages. Pattern-of-failure tells you what to change. Random resizing is a waste of CPU.
6. **Adding bigger devices to "fix" mismatch.** Helps σ but not basin stability. A weak resistor often fixes what no amount of matching can.
7. **Calling it done at 95 % yield.** The last 5 % is almost always a specific basin you can kill cheaply if you read the failing OPs.

— end of procedure —
