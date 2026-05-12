# Cherry-Hooper Design — Context & Convergence Log

This document records every design decision, debug step, and "gotcha" that came up while bringing up the `lelo_cherry_hooper_sky130a` Cherry-Hooper amplifier on **SKY130A + ngspice + cicsim**. It is meant as a recipe so that future amplifier designs in this repo do not have to rediscover the same pitfalls.

---

## 1. Repo & Tooling Layout

```
~/pro/aicex/ip/<lib>_sky130a/         <-- WORKING COPY (run sims here, has tech/ symlink)
   design/<LIB>/<CELL>.sch
   work/xsch/<CELL>.spice              <-- ngspice netlist (regenerated from .sch by `make typical`)
   sim/<CELL>/{op,ac,dc,tran,slew}.spi <-- testbenches
   tech -> ../tech_sky130A             <-- symlink, MUST resolve for cicsim runs
~/pro/aicex_designs/<lib>_sky130a/    <-- SNAPSHOT for git (no tech/, design files only)
```

**Critical**: simulations only work in the `~/pro/aicex/ip/...` tree because the `tech/` symlink resolves there. The `~/pro/aicex_designs/` copy is the git mirror; sync the netlist + TB files back after any change.

### Tools
- `xschem 3.4.7` — schematic editor (text-based `.sch` format)
- `ngspice-42` — simulator
- `cicsim` (`/opt/eda/python3/bin/cicsim`) — wraps ngspice with corner libs and produces yaml/csv summaries
- SKY130A PDK at `/opt/pdk/share/pdk/sky130A/`

### Standard run command
```bash
cd sim/<CELL>
make typical TB=op           # regenerates netlist via xschem then runs cicsim
# or, when bypassing xschem (hand-written netlist):
cicsim run --name Sch_typical op Sch Gt Ktt Tt Vt
```

`Sch` = schematic view, `Gt`/`Ktt`/`Tt`/`Vt` = global typical / process typical / temperature typical / voltage typical.

---

## 2. Decision: Hand-written netlist instead of xschem

For a brand-new topology you can either (a) draw the schematic in xschem, or (b) hand-write the `.spice` netlist directly in `work/xsch/`.

For Cherry-Hooper we picked (b) because:
- Faster iteration (no GUI)
- Deterministic node names
- Easier to diff and version
- Avoids re-learning xschem's per-component property syntax

**Trade-off**: `make typical` will overwrite a hand-written netlist by re-running xschem netlister. Workaround:
```bash
# Run cicsim directly, skipping the netlist regeneration step:
cicsim run --name Sch_typical op Sch Gt Ktt Tt Vt
```

If you need the `make` flow to coexist, draw a stub `.sch` whose only purpose is to keep `make typical` happy, and arrange your subckt to be includable from the testbench (which is how the existing aicex IPs work).

---

## 3. SKY130A Device Gotchas

### 3.1 Multi-finger devices break ngspice device-access strings
`@m.<inst>.<model>[id]` — used in op.spi to print transistor-level DC operating data — only works for **single-finger** devices. If you set `nf=2` or higher, ngspice splits the device internally and the access string fails:
```
Error: no such device or model name m.xdut.xmt1.msky130_fd_pr__nfet_01v8
```
**Always use `nf=1`**. To get larger effective W, increase the `W` parameter or use `m=N` (a true multiplier; access string still works).

### 3.2 Model bins limit individual W and L
The SKY130A NMOS/PMOS models are binned. The `nfet_01v8` family is bounded by `W ≤ 100 µm` (`wmax = 1e-4`) and `L` between 0.15 µm and ~100 µm. Going outside any bin raises:
```
could not find a valid modelname
```
Pick W and L that sit *inside* a bin (e.g. `W=80 L=1.0`, not `W=100 L=1.0`). For larger devices use `m=2,3,…` to multiply.

### 3.3 Submicron L kills intrinsic gain
Lowering input-pair `L` from 0.5 µm → 0.15 µm raises `gm` by ~15 % but raises `gds` by ~10 ×. Result: intrinsic gain `gm/gds` drops from ~25 to <2. **For non-RF amps stick to L ≥ 0.5 µm.**

### 3.4 Substrate / body must be tied
A floating body causes:
```
Warning: singular matrix:  check node m.xdut.xm2.msky130_fd_pr__nfet_01v8#body
```
The 4th terminal in the `.subckt` instance line is the body. Tie NFET bodies to `VSS` and PFET bodies to `VDD`.

---

## 4. ngspice Convergence Recipe

Order of attack when DC OP refuses to converge or sits at a degenerate point (all transistors barely on):

1. **Add `.nodeset` lines** for every internal node (drain of input pair, tail node, output, bias node). Numbers don't have to be exact — they just guide Newton.
2. Use **lowercase node names** in `.nodeset` — ngspice lowercases node names internally and a `.nodeset v(VOUT)` will silently fail with "Nodeset on non-existent node — voutp, ignored".
3. If still failing, **temporarily replace current sources with voltage sources** on bias pins. A hard voltage gives Newton a fixed boundary condition and almost always converges. Once the OP is good, you can swap back and re-add the diode-mirror that produces the bias voltage.
4. Drop `.option reltol`, `gmin`, and `srcsteps=` overrides — the defaults are good. Heavy non-default options can actually *worsen* convergence with the SKY130A bin model.
5. If you see one branch carry all the current and another branch carry zero, you have a **direction error on a current source**. Remember ngspice convention: `I<name> N+ N- ... dc Ival` means current flows *from N+ to N- through the source*, i.e. the source pulls current *out of N+ and into N-*. For a diode-connected NMOS at `IBIAS`, you want current flowing *into* the IBIAS pin (drain), so write `IIBIAS VSS IBIAS dc Ival`.

### Pattern that finally worked for Cherry-Hooper
We abandoned the diode-mirror bias entirely and exposed `VBIASN` and `VBIASP` as additional pins of the subckt, driving them with voltage sources from the testbench. Trade-off: less self-consistent over PVT, but rock-solid bring-up.

---

## 5. Topology Choice: Why Cherry-Hooper for Bandwidth

For a single high-impedance node OTA, GBW ≈ `gm_in / (2π · Cload_eff)` where `Cload_eff` is dominated by the Miller-multiplied `Cgd` of the gain-stage devices. A 2-stage Cherry-Hooper breaks this by inserting **shunt feedback** (`RF`) from each output back to the gate of its own second-stage CS device:

- The intermediate node impedance collapses from `r_o` to roughly `1/gm3 + RF/(1+gm3·RF)` ≈ tens to hundreds of ohms.
- The pole at the intermediate node moves to `1/(R_inter · C_inter)` — typically **10–100 × the original frequency**.
- The remaining output pole sets the closed-loop bandwidth.

**Midband closed-loop gain** (small-signal, ignoring loading):
$$
A_v \approx -g_{m1} \cdot R_F \cdot \frac{g_{m3} R_F}{1 + g_{m3} R_F}
\;\xrightarrow{g_{m3} R_F \gg 1}\; -g_{m1} \cdot R_F
$$

This makes `RF` the **primary gain knob** — sweep it to hit your target.

---

## 6. Cherry-Hooper Sizing Convergence Log

Sized iteratively. Each row is a single change from the previous row.

| Step | Change | Result | Comment |
|------|--------|--------|---------|
| 0 | First netlist with diode-mirror bias (W=100, nf=4) | OP fails: "could not find a valid modelname" | W=100 hits model bin upper boundary |
| 1 | Drop W to 80, force nf=1 | OP runs; partial bias, MT2 sees only 0.5 µA, M3/M4 starved | Bias mirror leg too weak |
| 2 | Tie tail gates directly to `IBIAS` (no separate `nbias_n`) | Mirror works but VOUT pinned at ground | `IIBIAS` wired wrong direction |
| 3 | Replace IIBIAS source with two voltage sources `VBIASN`, `VBIASP` (+ expose pins on subckt) | OP solves cleanly. `VBIASN=0.7`, `VBIASP=0.4` gives 105 µA per branch, VOUT=1.14 V | All devices saturated |
| 4 | `RF = 2 kΩ`, `L_m1 = 0.5 µm` | **DC gain = 7.3 dB, GBW = 2.34 GHz** | Bandwidth great, gain too low |
| 5 | Try `L_m1 = L_m3 = 0.15 µm`, `RF = 1 kΩ` | DC gain drops to **−0.85 dB** (<1 V/V) | gds explodes faster than gm rises at L=0.15 |
| 6 | Revert to `L = 0.5 µm`. Sweep RF for ~20 dB target: |
| 6a | `RF = 10 kΩ` | DC gain = 24.98 dB, f3dB = 887 MHz, GBW = 2.97 GHz | Above target |
| 6b | `RF = 5 kΩ` | DC gain = 18.18 dB, f3dB = 1.21 GHz, GBW = 2.86 GHz | Below target |
| 6c | `RF = 6 kΩ` | **DC gain = 20.04 dB, f3dB = 1.12 GHz, GBW = 2.90 GHz** | ✓ done |

### Key insight from the sweep
| RF | A_DC | f3dB | GBW |
|----|------|------|-----|
| 2 kΩ | 7.3 dB | 1.67 GHz | 2.34 GHz |
| 5 kΩ | 18.2 dB | 1.21 GHz | 2.86 GHz |
| 6 kΩ | 20.0 dB | 1.12 GHz | 2.90 GHz |
| 10 kΩ | 25.0 dB | 0.89 GHz | 2.97 GHz |

`A_DC ≈ 20·log10(gm1·RF) − ε`, so **doubling RF adds ~6 dB of gain at the cost of dividing f3dB by ~2** — but **GBW stays roughly constant** (the canonical "gain–BW trade-off"). This is the textbook Cherry-Hooper signature.

---

## 7. Final Sizing (committed)

| Device | Type | W (µm) | L (µm) | nf | m |
|--------|------|--------|--------|----|---|
| M1, M2 | NFET | 60 | 0.5 | 1 | 1 |
| M3, M4 | NFET | 15 | 0.5 | 1 | 1 |
| MT1, MT2 (tails) | NFET | 80 | 1.0 | 1 | 1 |
| MI1–MI4 (PMOS loads) | PFET | 20 | 1.0 | 1 | 1 |
| RF1, RF2 | resistor | 6 kΩ | – | – | – |

Bias: `VBIASN = 0.7 V`, `VBIASP = 0.4 V`, supply `1.8 V`, room temp.

| Spec | Value |
|------|-------|
| Branch current | 105 µA |
| Total IDD | 850 µA |
| `gm1` | 2.0 mS |
| `gm3` | 1.25 mS |
| **DC differential gain** | **20.0 dB** |
| **f3dB** | **1.12 GHz** |
| **GBW** | **2.90 GHz** |

---

## 8. Standard Workflow for the Next Amplifier

When starting any new aicex amplifier IP, follow this checklist:

1. **Clone an existing IP folder** with `cp -a` (preserves the `tech` symlink). Rename the inner `design/<LIB>` and `sim/<CELL>` folders to match.
2. **Update** `info.yaml`, `cicsim.yaml`, `Makefile`, `sim/Makefile`, `sim/<CELL>/Makefile`, `sim/<CELL>/xdut.spi`, `work/Makefile` — search-and-replace old `<LIB>` and `<CELL>` strings.
3. **Hand-write the netlist** in `work/xsch/<CELL>.spice` for fast iteration. Use `nf=1` everywhere. Keep `W` and `L` inside SKY130A model bins.
4. **Write `op.spi` first**:
   - Bias all gates with explicit voltage sources during bring-up
   - Add `.nodeset` for every internal node (lowercase!)
   - Print transistor-level `id`, `gm`, `gds`, `vds`, `vdsat` for each device
5. **Iterate** the OP until all devices show `|VDS| > VDSAT` (saturation).
6. **Write `ac.spi`**:
   - Use `vp(node) * 180/PI` to get phase in degrees (vp returns radians!)
   - Define `gain_mag_db = 20*log10(abs(vodiff)) − 20*log10(abs(vidiff))`
   - Use `meas ac fgbw WHEN gain_mag_db = 0` for unity-gain frequency
7. **Bypass `make typical`** when using a hand-written netlist:
   ```bash
   cicsim run --name Sch_typical op Sch Gt Ktt Tt Vt
   cicsim run --name Sch_typical ac Sch Gt Ktt Tt Vt
   ```
8. **Sweep one knob at a time**. Log each sim's headline numbers (gain, f3dB, GBW, PM, IDD) in a markdown table — this is the design's lab notebook.
9. **Sync to the git repo** at `~/pro/aicex_designs/<lib>_sky130a/` via `cp -a` (excluding `tech`, `output_*`, `__pycache__`, `*.run`, `summary.yaml`). Commit with a message that includes the headline number.

---

## 9. Common Error Messages — Quick Reference

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `could not find a valid modelname` | W or L outside SKY130A bin | Pick a value inside a bin (W≤80) or use `m=` to scale |
| `no such device or model name m.xdut.xmN.<model>` | Multi-finger device | Set `nf=1` |
| `singular matrix: check node #body` | Floating body | Tie 4th subckt terminal to VSS (NFET) or VDD (PFET) |
| `Nodeset on non-existent node` | Node name uppercase or typo | Use lowercase node names in `.nodeset` |
| `out of interval` from `meas` | Gain crosses 0 dB outside swept range | Widen `ac dec N fmin fmax` |
| All branch currents zero | Reversed current source or wrong VBIAS polarity | Flip `IIBIAS` direction or adjust VBIAS values |
| Phase reported as exactly ±180° | Differential phase wraps with vp() | Use phase computed from individual nodes; or ignore the wrap |

---

## 10. To-Do for Future Iterations

- Replace voltage-source biases with a real diode-connected NMOS + PMOS reference + 1:k mirrors (and document the convergence trick: nodeset every mirror leg).
- Add tran TB to extract slew rate and settling.
- Add corner sweep (`make tfs`) for ss/ff verification.
- Add Monte-Carlo (`make mc`) for `RF` mismatch sensitivity.
- Investigate whether substituting an active load + Cherry-Hooper hybrid (e.g. cascoded loads on stage 2) raises gain past 30 dB without losing >0.5 GHz of GBW.
