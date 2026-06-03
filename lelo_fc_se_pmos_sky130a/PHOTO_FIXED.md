# Analysis of the hand-drawn folded cascode (photo) + robust modified version

## Part 1 — What the photo actually shows

Four columns, left → right:

| col | label                | what's drawn                                                         |
|-----|----------------------|----------------------------------------------------------------------|
| 1   | P-side bias gen      | `VP1` (PMOS diode at VDD) over `VP2` (PMOS cascode), `Rp` to current sink (to VSS). Sooch-style P bias. |
| 2   | N-side bias gen      | PMOS mirror at top (gate=`VP1`), `RN` resistor, then NMOS Sooch stack producing `VN1`, `VN2`. |
| 3   | Input pair           | `VP1`-biased PMOS tail at top → node `Vtail` → PMOS diff pair (gates `Vinp`/`Vinn`) → drains labelled `Vmidn` (left) and `Vmidp` (right). **Drains go nowhere visible below — there is no NMOS sink under col-3.** |
| 4   | Output column        | `VP1`-biased PMOS load at top → `VP2`-biased PMOS cascode → output tap `Voutp` → `VN2`-biased NMOS cascode → **two NMOS in parallel at the bottom**: left one gate = `Vmidn`, right one gate = `Vmidp`, both drains tied to the cascode source, both sources to VSS. |

## Part 2 — Why this does not work / will not converge

### Issue A (fatal) — Col-3 input pair has no DC current path

The PMOS tail current `I_TAIL` enters col-3 from the top, splits into
`MP_inp` and `MP_inn`, and arrives at drains `Vmidn`, `Vmidp`. From
there those wires go *only* to NMOS gates in col-4. **NMOS gates draw
zero DC current**, so KCL at `Vmidn` and `Vmidp` cannot balance.

ngspice will either fail to converge or land on a degenerate solution
with the input PMOS pushed into triode and `Vmidn`, `Vmidp` slammed to
VSS.

### Issue B (fatal) — Col-4 bottom NMOS pair cancels the differential signal

The two bottom NMOS in col-4 have **separate gates** (`Vmidn`, `Vmidp`)
but their **drains are tied together** at the source of the `VN2`
cascode. Sources are at VSS. Currents sum at the common drain:

```
   I_sum  =  gm_n · (Vmidn − Vt)  +  gm_n · (Vmidp − Vt)
          =  gm_n · (Vmidn + Vmidp − 2·Vt)
```

If the input is differential, `Vmidn` and `Vmidp` move *oppositely*
(`Vmidn = Vcm + vd/2`, `Vmidp = Vcm − vd/2`), so:

```
   I_sum  =  gm_n · (2·Vcm − 2·Vt)         ← only common-mode survives
```

The differential signal **cancels at the summing node**. Only common-mode
voltage at `Vmidn`/`Vmidp` reaches `Voutp`. This is mathematically
guaranteed regardless of bias.

### Issue C — `Voutp` DC is undefined → dual-equilibrium risk

Even ignoring A and B, the output column has no feedback or mirror to
set the DC voltage of `Voutp`. The PMOS load pushes a constant `I_FOLD`
current down, the NMOS pair pulls some PVT-dependent current up. Unless
the two match within ~1 %, `Voutp` rails to VDD or VSS. This is the
classic startup-latch failure mode of high-gain single-stage nodes with
no DC regulation loop.

### Issue D — Stage-2 NMOS gates DC-biased by a signal node

`Vmidn` and `Vmidp` are *signal* nodes — their DC level is set by
whatever the (broken) input stage happens to land on. The NMOS bottoms
in col-4 therefore have an undefined `V_GS` → undefined quiescent
current → undefined `Voutp` DC. Slow corners: cutoff. Fast corners:
deep triode. Either way: broken.

### Summary table

| issue | severity | symptom in ngspice                                |
|-------|----------|---------------------------------------------------|
| A     | fatal    | `singular matrix` / `Newton iteration failed`    |
| B     | fatal    | If A is fixed, AC gain ≈ 0 for differential input |
| C     | fatal    | OP found but Voutp = 0 V or VDD at every corner   |
| D     | fatal    | Stage-2 NMOS in cutoff or deep triode             |

**Verdict: the photo's circuit does not work as drawn.** It needs two
fundamental changes: (1) a DC current sink under col-3 drains, and
(2) a current-mirror diff-to-single conversion in col-4.

---

## Part 3 — Modified circuit (same look, works robustly)

Keep the photo's **4-column visual layout**. Make two surgical fixes:

1. Add **NMOS fold-sinks** under col-3 drains (`Vmidn`, `Vmidp`) so the
   input pair has a DC current path. These sinks deliver `I_FOLD` and
   the *signal* current `±gm·vid/2` then flows up through col-4 (the
   diff currents become *voltages* on the high-impedance fold nodes).
2. Make col-4's bottom two NMOS a **proper current mirror**:
   left = diode (gate=drain=`Vmidn`), right = mirror (gate=`Vmidn`,
   drain=cascode source). The *right* fold node `Vmidp` then drives
   the cascode column above directly.

This is exactly the canonical low-voltage SE folded cascode — laid out
to match the photo's visual style.

### Modified schematic (4 columns, same look as photo)

```
   COL-1               COL-2               COL-3              COL-4
   P-side bias         N-side bias         Input pair         Output column
   (gen VP1, VP2)      (gen VN1, VN2)      + fold sinks       (folded cascode SE)

       VDD                 VDD                 VDD                 VDD          VDD
   ════════════        ════════════        ════════════        ═══════════   ═══════════
        │                   │                   │                   │              │
     ┌──┴──┐             ┌──┴──┐             ┌──┴──┐             ┌──┴──┐       ┌──┴──┐
     │MPR  │          VP1│ MP3 │          VP1│ MTL │          VP1│ ML  │    VP1│ ML2 │
     │diode│         (mirr│    │          (tail│   │          (load│   │   (load│   │
     │VP1=g│             │    │             │   │             │   │       │   │
     └──┬──┘             └──┬──┘             └──┬──┘             └──┬──┘       └──┬──┘
        ● VP1               │ pcas-leg          ● Vtail              │              │
        │                ┌──┴──┐         ┌──────┴──────┐             │              │
     ┌──┴──┐          VP2│ MP8 │      ┌──┴──┐       ┌──┴──┐       VP2●           VP2●
     │MP_C │         Sooch│aux  │  inp►│MP_in│       │MP_in│◄inn   ┌──┴──┐       ┌──┴──┐
     │P-cas│             │     │      │PMOS │       │PMOS │    VP2│ MC1 │    VP2│ MC2 │
     │VP2=g│             └──┬──┘      │ LVT │       │ LVT │       │P-cas│       │P-cas│
     └──┬──┘                ● VP2     └──┬──┘       └──┬──┘       └──┬──┘       └──┬──┘
        ● VP2               │            ● Vmidn       ● Vmidp       ● node A      ● Voutp
        │                ┌──┴──┐         │              │            │ (mirror)    │ (output,
     ┌──┴──┐             │ Rp2 │         │              │            │  tap)       │  high-Z)
     │ Rp  │             │drops│         │              │         ┌──┴──┐       ┌──┴──┐
     │drops│             │Vov_p│         │              │      VN2│ MN_C│    VN2│ MN2C│
     │Vov_p│             └──┬──┘         │              │         │N-cas│       │N-cas│
     └──┬──┘             ┌──┴──┐         │              │         └──┬──┘       └──┬──┘
        │                │ MN9 │      ┌──┴──┐        ┌──┴──┐         ● fold-L      ● fold-R
        ▼                │diode│      │MNF_L│        │MNF_R│         │ ( = Vmidn   │  ( = Vmidp
      ─┴─                └──┬──┘   VN1│fold │     VN1│fold │         │   when KCL  │    when KCL
      ─▼─ I1 sink to VSS ┌──┴──┐      │sink │        │sink │         │   solved)   │    solved)
        │  (bandgap)     │ MN10│      └──┬──┘        └──┬──┘         │              │
       VSS               │     │         │              │         ┌──┴──┐        ┌──┴──┐
                         └──┬──┘        VSS            VSS        │ MN1 │ diode  │ MN2 │ mirror
                            │                                     │g=d=A│        │ g=A │ ◄── gate from A
                           VSS                                    └──┬──┘        └──┬──┘
                                                                     │              │
                                                                    VSS            VSS
   ══════════════════════════════════════════════════════════════════════════════════════════
                                              VSS
```

### Net list of the working circuit

| node      | driven by                                          | drives                                              |
|-----------|----------------------------------------------------|-----------------------------------------------------|
| `VP1`     | `MPR` diode (col-1) — sized via IBGR `I1`          | every PMOS source: `MP3`, `MTL`, `ML`, `ML2`        |
| `VP2`     | between `Rp` and current sink (col-1)              | `MP_C` and **`MC1`, `MC2`** (P-cascodes in col-4)   |
| `VN1`     | top of `RN` Sooch stack (col-2)                    | **`MNF_L`, `MNF_R`** (fold sinks under col-3)       |
| `VN2`     | mid Sooch node (col-2)                             | `MN_C`, **`MN2C`** (N-cascodes in col-4)            |
| `Vtail`   | drain of `MTL`                                     | sources of `MP_in` PMOS pair                        |
| `Vmidn`   | drain of `MP_in(left)` + drain of `MNF_L` + drain of `MC1` (in col-4) | gate of `MN1` AND gate of `MN2` (mirror)  |
| `Vmidp`   | drain of `MP_in(right)` + drain of `MNF_R` + drain of `MC2` | (nothing — this is the right fold node only)  |
| `Voutp`   | drain of `MC2` + drain of `MN2C` + drain of `MN2`  | output                                              |

### What changed vs the photo

| photo feature                                       | fix in modified circuit                              |
|------------------------------------------------------|------------------------------------------------------|
| Col-3 drains (`Vmidn`, `Vmidp`) float — no DC sink   | Added `MNF_L`, `MNF_R` NMOS fold sinks (gate = `VN1`) |
| Col-4 bottom: two NMOS gates = `Vmidn`, `Vmidp`      | Replaced with **current mirror**: `MN1` diode (g=d=`Vmidn`), `MN2` mirror (g=`Vmidn`) |
| `Vmidp` had no role beyond cancelling signal at sum  | Now `Vmidp` is the right fold node, drives col-4 cascode column up to `Voutp` |
| Output `Voutp` DC undefined                          | Mirror enforces KCL → `Voutp` self-biases to wherever both `MC2` and `MN2` saturate (≈ VDD/2) |
| One output column only                               | Still one output column (col-4) — the diode `MN1` sits at the bottom of col-4, the mirror `MN2` to its right in the same column (visually adjacent) |

Importantly: the layout still has only the **4 columns from the photo**.
The diode-mirror pair `MN1`/`MN2` sits at the bottom of col-4 — exactly
where the two photo NMOS were — but **wired as a mirror** (one diode,
one mirror, gate connection horizontal between them) instead of as two
independent signal-driven sinks.

### Why this is robust

- **Convergence**: every node has a defined DC path. `Vmidn` is set by
  the diode `MN1` (`V_GS,N` ≈ 0.62 V at 40 µA, Vov ≈ 0.2 V). `Vmidp`
  sits at the same voltage by symmetry. `Voutp` is set by KCL with
  matched mirror.
- **No CMFB**: single-ended output, mirror does the diff→single.
- **No dual equilibrium**: only one DC solution because the mirror
  current is set by the diode `MN1`, not floating.
- **Wide-swing**: `VP2` is wide-swing (Sooch in col-1), `VN2` is
  wide-swing (Sooch in col-2). Output swing at VDD = 1.2 V:
  - Top limit: `VDD − 2·Vov_p ≈ 1.0 V`
  - Bottom limit: `2·Vov_n ≈ 0.2 V`
  - **Usable swing ≈ 0.8 V pp**.
- **PVT**: all bias currents tracked to single bandgap `I1` via the
  `VP1` rail (mirror-to-mirror). No absolute Vt or kp dependence.

### Signal-flow summary

```
   vid → MP_in(left)  drain current  (I_TAIL/2 + gm·vid/2)
                        ↓
                     Vmidn            ← MNF_L sinks the DC I_FOLD = I_TAIL/2
                        ↓ signal current = gm·vid/2 forced up through MC1
                        ↓
                     node A           ← MN1 diode sets V(A) = V_GS for I = I_TAIL/2 + gm·vid/2
                        │
                        ════════════ ► gate of MN2

   vid → MP_in(right) drain current  (I_TAIL/2 − gm·vid/2)
                        ↓
                     Vmidp            ← MNF_R sinks the DC I_FOLD = I_TAIL/2
                        ↓ signal current = −gm·vid/2 forced up through MC2
                        ↓
                     Voutp            ← MN2 pulls down (I_TAIL/2 + gm·vid/2)
                                       MC2 pushes down (I_TAIL/2 − gm·vid/2)
                                       Net: i_out = −gm·vid into the load
```

### Headroom at VDD = 1.2 V (Vov = 0.1 V)

```
   VDD = 1.20 V  ──────────────────────────
                   Vsd_ML  = 0.10
   1.10 V         (PMOS load Vov)
                   Vsd_MC2 = 0.10
   1.00 V  ────── Voutp_max
                   ↕ output swing ≈ 0.80 V
   0.20 V  ────── Voutp_min
                   Vds_MN2C = 0.10
   0.10 V
                   Vds_MN2  = 0.10
   VSS = 0  ───────────────────────────────
```

### Build / verify order

1. Bring up bias: `MPR`/`MP3` mirror → `VP1`, then `VP2` from col-1 Sooch,
   then `VN1`/`VN2` from col-2 Sooch. Confirm DC:
   - `VP1 = VDD − (Vt_p + Vov_p) ≈ 0.65 V`
   - `VP2 = VDD − (Vt_p + 2·Vov_p) ≈ 0.55 V`
   - `VN1 = Vt_n + Vov_n ≈ 0.52 V`
   - `VN2 = Vt_n + 2·Vov_n ≈ 0.62 V`
2. Add input pair + tail. Confirm `Vtail ≈ 1.10 V`, `Vmidn ≈ Vmidp ≈ 0.62 V`.
3. Add fold sinks `MNF_L`, `MNF_R` (gate=VN1). Sized so `I_FOLD = I_TAIL/2`.
4. Add col-4 output stack (`ML2`, `MC2`, `MN2C`, `MN2`) and diode `MN1`
   in col-4 bottom-left. Wire `Vmidn → MN1.gate=MN1.drain → MN2.gate`.
5. Sweep DC input CM, confirm `Voutp` self-biases near VDD/2. AC sim
   should give 60-80 dB gain, GBW = `gm_input / C_L`.

### One-line summary

The photo's circuit doesn't work because (a) the input pair drains float
and (b) tying two NMOS drains together cancels the differential signal.
The modified version adds **NMOS fold sinks** under col-3 and replaces
the col-4 bottom pair with a proper **current mirror** (diode + mirror).
Same 4-column visual layout, robust convergence, ~0.8 V output swing
at VDD = 1.2 V, 60-80 dB gain. No CMFB.
