# PMOS-input single-ended folded cascode — low-VDD, wide-swing cascode bias

**One file, consistent end-to-end. `IBGR` polarity matches the photo:
off-chip bandgap is a current SINK to VSS.**

---

## 1. Conventions

| symbol      | meaning                                              |
|-------------|------------------------------------------------------|
| `IBGR`      | off-chip bandgap current sink (arrow → VSS)          |
| `pb_tail`   | rail = gate of every PMOS current source             |
| `pcas`      | rail = gate of every PMOS cascode device             |
| `ncas`      | rail = gate of every NMOS cascode device             |
| `X`, `Y`    | fold nodes (drains of input pair MP1, MP2)           |
| `A`         | mirror reference node (diode tap)                    |
| `outp`      | single-ended output (high-impedance node)            |
| `Vov`       | overdrive voltage, target 100 mV at VDD = 1.2 V      |

All cascodes are biased **wide-swing (Sooch)** — each cascode device
burns only one `Vov` of headroom (not `Vt + Vov`). That is what makes
the 4-transistor stack fit under VDD = 1.2 V.

---

## 2. Reference current polarity (matches the photo)

```
                  VDD
                   │
                ┌──┴──┐
                │ MPR │   PMOS diode at VDD (defines pb_tail)
                │     │
                └──┬──┘
                   ● pb_tail rail  ──► gate of every PMOS source
                   │
                   │  IBGR pad
                   ▼
                  ─┴─    off-chip bandgap sinks I1 to VSS
                   ▼
                  VSS (off-chip)
```

**Only one current crosses the IBGR pin** — the bandgap reference `I1`.
Every on-chip bias current is a mirrored copy of that, taken via
`pb_tail`.

---

## 3. Full schematic (5 columns, left → right)

```
   COL-1            COL-2            COL-3           COL-4           COL-5
   N-bias (Sooch)   P-bias (Sooch)   Input pair      Diode column    Output column
   → makes ncas     → makes pcas     PMOS diff       (mirror master) (signal out)

         VDD              VDD              VDD             VDD             VDD
     ════════════     ════════════     ════════════    ════════════    ════════════
          │                │                │               │               │
       ┌──┴──┐          ┌──┴──┐          ┌──┴──┐         ┌──┴──┐         ┌──┴──┐
  pb_t►│MP_N │     pb_t►│ MP7 │     pb_t►│ MTL │    pb_t►│MP3L │    pb_t►│MP3R │
       │mirr │          │mirr │          │tail │         │load │         │load │
       └──┬──┘          └──┬──┘          └──┬──┘         └──┬──┘         └──┬──┘
          ● ncas           │                ● tail          │               │
          │                │             ┌──┴──┐            │               │
       ┌──┴──┐          ┌──┴──┐       ┌──┴──┐ ┌──┴──┐    pcas●          pcas●
       │ MN7 │      pcas│ MP8 │   inp►│ MP1 │ │ MP2 │◄inn  │               │
       │diode│          │Sooch│       │PMOS │ │PMOS │   ┌──┴──┐         ┌──┴──┐
       └──┬──┘          │ aux │       │ LVT │ │ LVT │pcas►│MP4L│    pcas►│MP4R│
       ┌──┴──┐          └──┬──┘       └──┬──┘ └──┬──┘   │P-cas│         │P-cas│
       │ Rb1 │             ● pcas        │ X    Y│      └──┬──┘         └──┬──┘
       │drops│          ┌──┴──┐          │       │         ● A (diode      ● outp
       │Vov_n│          │ Rb2 │          │       │         │   tap)        │  (high-Z)
       └──┬──┘          │drops│          │       │      ┌──┴──┐         ┌──┴──┐
       ┌──┴──┐          │Vov_p│          │       │  ncas►│MN4L│    ncas►│MN4R│
  ncas►│ MN8 │          └──┬──┘          │       │      │N-cas│         │N-cas│
       │Sooch│          ┌──┴──┐          │       │      └──┬──┘         └──┬──┘
       │ aux │          │ MN9 │          │       │         ● fold-L (X)    ● fold-R (Y)
       └──┬──┘          │diode│          │       │         │               │
          │             └──┬──┘          │       │         │               │
         VSS           ┌──┴──┐           │       │      ┌──┴──┐         ┌──┴──┐
                   ncas►│MN10│           │       │      │ MN1 │ diode   │ MN2 │ mirror
                       │     │           │       │      │g=d=A│         │ g=A │
                       └──┬──┘           │       │      └──┬──┘         └──┬──┘
                          │              │       │         │               │
                         VSS             │       │        VSS             VSS
                                         │       │
                                         │       └──── drain of MP2 wires DOWN to fold-R (Y)
                                         └──────────── drain of MP1 wires DOWN to fold-L (X)

                  ════════════════════════════════════════════════════════════
                                            VSS
```

### THE critical wire (the one missing in the hand-drawn photo)

```
          A  ════════════════════════════════════════════════►  gate of MN2
       (left)              long horizontal wire                  (right)
```

Node `A` is the mirror reference (drain of MN4L meeting drain of MN1).
That node sets `V_GS` of MN1 (diode, gate=drain=A) AND of MN2 (mirror,
gate=A). MN2 therefore sinks the *same* current at `outp` that MN4L
delivered at `A`. **Without this wire there is no diff-to-single
conversion**, and `vid` never reaches `outp`.

---

## 4. IBGR feeds every PMOS source from ONE diode

```
                                       VDD
       ══════════════════════════════════════════════════════════════════════
            │       │           │           │           │           │
         ┌──┴──┐ ┌──┴──┐      ┌──┴──┐    ┌──┴──┐    ┌──┴──┐    ┌──┴──┐
         │ MPR │ │MP_N │      │ MP7 │    │ MTL │    │MP3L │    │MP3R │
         │diode│ │mirr │      │mirr │    │mirr │    │mirr │    │mirr │
         └──┬──┘ └──┬──┘      └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘
            │      │             │          │          │          │
            ●═════●═════════════●══════════●══════════●══════════● pb_tail rail
            │
            ▼  IBGR pad
            │
            ▼  off-chip bandgap (sinks I1 to VSS)
           VSS
```

- `MPR` is the *only* diode-connected PMOS. Every other PMOS on the
  `pb_tail` rail is a pure mirror (gate = `pb_tail`, source = VDD).
- Internal currents set by mirror W/L ratios:
  - `MTL`  = 16×  → tail = 160 µA
  - `MP3L` = `MP3R` = 4× → fold load = 40 µA each
  - `MP_N` = `MP7`  = 1× → bias-leg current = 10 µA each
- `ncas` is generated below `MP_N` by the N-Sooch stack (COL-1).
- `pcas` is generated below `MP7` by the P-Sooch stack (COL-2).

---

## 5. Signal flow

```
 vid → MP1 drain current  (I_TAIL/2 + gm·vid/2)
            ↓ lands at fold-L (X)
            ↓ flows up through MN4L cascode (source=X, drain=A)
            ↓
        node A  ── sets V_GS of MN1 (diode) and MN2 (mirror)
            │
            └────► MN2 sinks the SAME current at outp


 vid → MP2 drain current  (I_TAIL/2 − gm·vid/2)
            ↓ lands at fold-R (Y)
            ↓ flows up through MN4R cascode
            ↓
        outp  ← simultaneously sees MN2 pulling down
                AND MP4R/MP3R pushing down

 i_outp = (I/2 + gm·vid/2)  −  (I/2 − gm·vid/2)  =  gm · vid  ──►  C_L
```

---

## 6. Headroom budget at VDD = 1.2 V (Vov = 100 mV everywhere)

```
  VDD = 1.20 V  ────────────────────────────────
                      │  Vsd_MP3R = 0.10  (PMOS load Vov)
  1.10 V              │
                      │  Vsd_MP4R = 0.10  (PMOS cascode Vov)
  1.00 V  ──────── outp_max
                      │
                      │  USABLE OUTPUT SWING ≈ 0.80 V pp
                      │
  0.20 V  ──────── outp_min
                      │  Vds_MN4R = 0.10  (NMOS cascode Vov)
  0.10 V              │
                      │  Vds_MN2  = 0.10  (NMOS mirror Vov)
  VSS = 0   ─────────────────────────────────────
```

4 cascoded devices → `4·Vov = 0.4 V` total headroom → **0.8 V output
swing** at VDD = 1.2 V.

Classical (low-swing) cascode bias would cost `Vt + Vov ≈ 0.55 V` per
cascode device → stack ≈ 1.3 V → **zero swing at VDD = 1.2 V**. Wide-swing
Sooch bias is mandatory for low-VDD operation.

---

## 7. Sooch bias generators — corrected polarity

### COL-1 — N-side (generates `ncas`)

```
                  VDD
                   │
                ┌──┴──┐
           pb_t►│MP_N │   PMOS mirror (gate from pb_tail rail)
                │mirr │   delivers I1 down through the NMOS Sooch stack
                └──┬──┘
                   ● ncas  ──► gates of MN8, MN4L, MN4R, MN10
                   │
                ┌──┴──┐
                │ MN7 │   NMOS diode (carries I1, V_GS = Vt_n + Vov_n)
                └──┬──┘
                ┌──┴──┐
                │ Rb1 │   sized so I1 · Rb1 = Vov_n
                │     │   ⇒ top of Rb1 = Vt_n + 2·Vov_n = ncas
                └──┬──┘
                ┌──┴──┐
           ncas►│ MN8 │   Sooch aux NMOS (small W/L so its
                │ aux │   V_GS = Vt_n + 2·Vov_n with I1 flowing)
                └──┬──┘
                   │
                  VSS
```

Result: `ncas = Vt_n + 2·Vov_n`. Any main-column NMOS cascode biased
by `ncas` has its source at `Vov_n` → the NMOS *below* the cascode
sees `Vds = Vov_n` (edge of saturation, **zero wasted Vt**).

### COL-2 — P-side (generates `pcas`)

```
                  VDD
                   │
                ┌──┴──┐
           pb_t►│ MP7 │   PMOS mirror (delivers I1 down this leg)
                │mirr │
                └──┬──┘
                   ● top of MP8
                   │
                ┌──┴──┐
                │ MP8 │   Sooch aux PMOS (small W/L so V_SG = Vt_p + 2·Vov_p)
                │ aux │
                └──┬──┘
                   ● pcas  ──► gates of MP4L, MP4R
                   │
                ┌──┴──┐
                │ Rb2 │   sized so I1 · Rb2 = Vov_p
                │     │   ⇒ pcas = VDD − (Vt_p + 2·Vov_p)
                └──┬──┘
                ┌──┴──┐
                │ MN9 │   NMOS diode (current sink for the leg)
                └──┬──┘
                ┌──┴──┐
           ncas►│MN10 │   NMOS bottom (gate=ncas) — keeps leg at I1
                │mirr │
                └──┬──┘
                   │
                  VSS
```

Result: `pcas = VDD − (Vt_p + 2·Vov_p)`. Any PMOS cascode biased by
`pcas` has its source one Vov_p below VDD → minimum-headroom PMOS
cascode.

---

## 8. Node-by-node net list (verify against your drawing)

| node       | driven by                                                      | drives                                                  |
|------------|----------------------------------------------------------------|---------------------------------------------------------|
| `pb_tail`  | drain of `MPR` (PMOS diode at VDD)                             | every PMOS mirror: `MP_N`, `MP7`, `MTL`, `MP3L`, `MP3R` |
| `IBGR`     | off-chip bandgap (sink to VSS)                                 | sinks `I1` out of `pb_tail` rail through the IBGR pad   |
| `ncas`     | drain of `MP_N` (top of N-Sooch stack)                         | `MN8`, `MN10`, **`MN4L`, `MN4R`** (all N cascodes)      |
| `pcas`     | between `MP8` and `Rb2` (P-Sooch leg)                          | **`MP4L`, `MP4R`** (all P cascodes)                     |
| `tail`     | drain of `MTL`                                                 | sources of `MP1`, `MP2`                                 |
| `X` fold-L | drain of `MP1` + source of `MN4L` + drain of `MP4L`            | (KCL summing node)                                      |
| `Y` fold-R | drain of `MP2` + source of `MN4R` + drain of `MP4R`            | (KCL summing node)                                      |
| **`A`**    | drain of `MN4L` + drain of `MN1`                               | **gate of `MN1` AND gate of `MN2`** (the diff→single wire) |
| `outp`     | drain of `MN4R` + drain of `MN2`                               | output pin                                              |

---

## 9. Order of operations to build & verify

1. Build the **bias chain first** (`MPR`, `MP_N`, COL-1 N-Sooch, COL-2
   P-Sooch). Bring up `IBGR` from a 10 µA test source. Check
   `pb_tail`, `ncas`, `pcas` DC levels are exactly:
   - `pb_tail ≈ VDD − (Vt_p + Vov_p) = 1.2 − 0.55 = 0.65 V`
   - `ncas    ≈ Vt_n + 2·Vov_n        = 0.42 + 0.20 = 0.62 V`
   - `pcas    ≈ VDD − (Vt_p + 2·Vov_p) = 1.2 − 0.65 = 0.55 V`

2. Add the **input pair** (COL-3) with `MTL` from `pb_tail`. Sweep
   input CM, confirm `tail` ≈ 1.10 V and `X` = `Y` ≈ 0.55 V at balance.

3. Add **COL-4 diode column**. Confirm node `A` is at `Vt_n + Vov_n` ≈
   0.52 V and the column carries `I_TAIL/2 = 40 µA`.

4. Add **COL-5 output column** with the long mirror wire `A → MN2.g`.
   Confirm `outp` self-biases near VDD/2 ≈ 0.6 V at zero differential
   input.

5. AC: small-signal `gm·(r_o_p ∥ r_o_n)` should give ~60-80 dB DC gain.
   Add `C_L = 1 pF` at `outp`, expect `GBW = gm_input / C_L` ≈ 50 MHz
   with `gm_input ≈ 300 µA/V` at 40 µA per device.

---

## 10. Summary

- **5 columns**, current-sink convention matches the photo.
- **One PMOS diode (`MPR`)** at VDD sets the `pb_tail` rail; everything
  else is a copy.
- **Wide-swing Sooch bias** on both N and P sides (`ncas`, `pcas`)
  enables VDD = 1.2 V operation with 0.8 V output swing.
- **Two output columns** (COL-4 diode + COL-5 signal). The long
  horizontal wire `A → MN2.gate` is the diff-to-single mirror.
- **No CMFB** — the mirror enforces output DC by KCL.
