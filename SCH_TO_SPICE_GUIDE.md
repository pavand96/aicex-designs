# Schematic ↔ SPICE Conversion Guide

A practical reference for moving between **xschem `.sch`** files (human-friendly graphical schematics) and **`.spice` / `.spi` netlists** (what ngspice actually simulates).

---

## TL;DR — The Standard Tools

| Direction | Tool | Command |
|-----------|------|---------|
| **`.sch` → `.spice`** | xschem (CLI mode) | `xschem -q -x -b -s -n my_cell.sch` |
| **`.sch` → `.spice`** (this repo) | aicex Makefile | `make xsch` (run inside `<design>/work/`) |
| **`.spice` → `.sch`** | (no automated tool) | hand-translate, or import via Magic |

> **Reality check:** Going schematic → netlist is fully automated. The reverse direction is **not** — there's no robust tool that reconstructs visual placement from a flat netlist. People typically maintain the `.sch` as the source of truth and regenerate `.spice` from it.

---

## 1. `.sch` → `.spice` — How it actually works

### 1.1 Using xschem directly

```bash
xschem -q -x -b -s -n path/to/cell.sch
```

Flags:
| Flag | Meaning |
|------|---------|
| `-q` | quiet (no GUI splash) |
| `-x` | exit after netlisting |
| `-b` | batch mode (no Tk) |
| `-s` | SPICE format (vs. Verilog/VHDL) |
| `-n` | netlist now |

Output goes to `xsch/<cell>.spice` (configured in `xschemrc`).

### 1.2 Using the aicex Makefile (this repo)

Every aicex IP has a `work/` folder with a Makefile that wraps xschem and post-processes:

```bash
cd <design>/work
make xsch     # generates xsch/<CELL>.spice
make cdl      # generates cdl/<CELL>.cdl  (clean SPICE for LVS)
make lpe      # extract layout parasitics → lpe/<CELL>_lpe.spi
```

Internally `make xsch` runs:
```
xschem -q -x -b -s -n ../design/${LIB}/${CELL}.sch
cat xsch/${CELL}.spice.bak | perl ../tech/script/fixsubckt > xsch/${CELL}.spice
```
The `fixsubckt` step wraps the netlist in a `.subckt … .ends` and tidies the device names.

---

## 2. `.spice` → `.sch` — The Hard Direction

There is no general-purpose SPICE-to-xschem importer. Three workable approaches:

### Option A — Hand-edit the `.sch` text format
xschem files are **plain text**. Once you understand the syntax (next section), small edits like swapping NMOS↔PMOS or renaming a net are trivial with a text editor or `sed`. **This repo's `lelo_5tota_pmos_sky130a` was built this way.**

### Option B — Maintain symbol-level subcircuits
Keep your `.sch` as the *interface* (ports + a placeholder symbol). Drop the imported `.spice` body in the same directory and reference it via xschem's `spice_sym_def` attribute, or include it in your testbench. The schematic shows pins; the SPICE provides behaviour.

### Option C — Magic / Klayout import
For schematics that originated from a layout, you can extract a netlist from Magic (`extract`, then `ext2spice`) and re-draw the schematic in xschem to match. Tedious but works for small cells.

---

## 3. The xschem `.sch` File Format (Cheat Sheet)

xschem files are line-oriented ASCII. Each line starts with a **command character**:

| Char | Meaning | Example |
|------|---------|---------|
| `v` | Version header | `v {xschem version=3.4.7 file_version=1.2}` |
| `G` | Globals (params) | `G {}` |
| `K` | Tcl code | `K {}` |
| `V` | Verilog header | `V {}` |
| `S` | SPICE header | `S {}` |
| `E` | EDIF header | `E {}` |
| `N` | **Net (wire)** | `N x1 y1 x2 y2 {lab=NETNAME}` |
| `C` | **Component** | `C {symbol_path.sym} x y rot flip {properties}` |
| `T` | Text label | `T {text} x y rot flip size color` |
| `B` | Box / box-net | `B layer x1 y1 x2 y2 {props}` |
| `L` | Line | `L layer x1 y1 x2 y2 {props}` |

### Component (`C`) example — NMOS transistor

```
C {sky130_fd_pr/nfet_01v8.sym} 520 -360 0 0 {name=M1
W=80
L=0.8
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
…
model=nfet_01v8
spiceprefix=X
}
```

| Field | Meaning |
|-------|---------|
| `{sky130_fd_pr/nfet_01v8.sym}` | path to the symbol file (relative to `XSCHEM_LIBRARY_PATH`) |
| `520 -360` | placement (x, y) — note y-axis is **inverted** (smaller y = higher on screen) |
| `0 0` | rotation (0/1/2/3 = 0°/90°/180°/270°) and flip (0/1) |
| `{ … }` | property block — anything inside drives netlisting |
| `name=M1` | instance name → becomes `XM1` in SPICE (because `spiceprefix=X`) |
| `W=80 L=0.8` | dimensions (microns) — passed straight into the SPICE line |
| `model=nfet_01v8` | which model card to invoke |

### Net (`N`) example

```
N 540 -480 540 -390 {lab=#net2}
```
A wire from (540,-480) to (540,-390) labeled `#net2` (the `#` prefix marks an auto-generated internal net; named nets like `VDD`, `IBIAS` are visible at the SPICE level).

### Pins — IPin / OPin / IOPin

```
C {devices/ipin.sym} 650 -620 0 0 {name=p1 lab=VDD}
C {devices/opin.sym} 720 -440 0 1 {name=p3 lab=VOUT}
```
Pin labels become `.subckt` ports.

---

## 4. Recipe — Convert NMOS-Input → PMOS-Input 5T OTA

Concrete worked example (this is exactly what was done to create `lelo_5tota_pmos_sky130a`).

### Step 1 — Copy and rename the design
```bash
cp -r lelo_5tota_sky130a lelo_5tota_pmos_sky130a
cd lelo_5tota_pmos_sky130a
mv design/LELO_5TOTA_SKY130A design/LELO_5TOTA_PMOS_SKY130A
mv design/LELO_5TOTA_PMOS_SKY130A/LELO_5TOTA.sch \
   design/LELO_5TOTA_PMOS_SKY130A/LELO_5TOTA_PMOS.sch
mv sim/LELO_5TOTA sim/LELO_5TOTA_PMOS
```

### Step 2 — In the `.sch`: swap device types AND rails
A 3-step `sed` with a placeholder avoids double-substitution:

```bash
SCH=design/LELO_5TOTA_PMOS_SKY130A/LELO_5TOTA_PMOS.sch
sed -i \
  -e 's/nfet_01v8/__TMP__/g' \
  -e 's/pfet_01v8/nfet_01v8/g' \
  -e 's/__TMP__/pfet_01v8/g' \
  -e 's/lab=VDD/lab=__VDDTMP__/g' \
  -e 's/lab=VSS/lab=VDD/g' \
  -e 's/lab=__VDDTMP__/lab=VSS/g' \
  $SCH
```

This converts every NMOS to PMOS, every PMOS to NMOS, and flips VDD↔VSS labels — producing a topologically complementary OTA.

### Step 3 — Regenerate the SPICE netlist
```bash
cd work && make xsch
```
Or, if xschem is not available, hand-edit `work/xsch/<CELL>.spice` (see `lelo_5tota_pmos_sky130a/work/xsch/LELO_5TOTA_PMOS.spice` for the template).

### Step 4 — Update the testbenches
The `.spi` testbenches reference device models by name (e.g. `@m.xdut.xm1.msky130_fd_pr__nfet_01v8[id]`). Apply the same NMOS↔PMOS swap to every `*.spi` and `*.meas` file:

```bash
cd sim/LELO_5TOTA_PMOS
for f in *.spi *.meas; do
  sed -i -e 's/nfet_01v8/__T__/g' -e 's/pfet_01v8/nfet_01v8/g' -e 's/__T__/pfet_01v8/g' "$f"
done
```

### Step 5 — Flip the IBIAS source direction
The original NMOS topology drives the bias diode by **sourcing** current into `IBIAS`. The PMOS topology needs the opposite:

```spice
* NMOS bias (M6 diode at VSS):
IIBIAS  VSS    IBIAS  dc {ibias_val}     ; current INTO IBIAS

* PMOS bias (M6 diode at VDD):
IIBIAS  IBIAS  VSS    dc {ibias_val}     ; current OUT of IBIAS
```

### Step 6 — Update names in build config
```bash
sed -i 's/LELO_5TOTA/LELO_5TOTA_PMOS/g' Makefile work/Makefile sim/Makefile info.yaml
```

(Watch out for double-substitution if `LELO_5TOTA_SKY130A` becomes `LELO_5TOTA_PMOS_SKY130A` — apply the longer pattern first or use a placeholder.)

### Step 7 — Sanity check
```bash
cd sim/LELO_5TOTA_PMOS
make typical TB=op       # check operating point sanity
```

Look at `output_op/op_*.log`:
- All transistors should be in saturation
- Tail current `I(M5)` should equal `2 × I(M1)`
- Output node `VOUT` should sit near mid-rail

---

## 5. Common Gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| `*** model not found ***` | `.lib` corner file not included | Check `cicsim.yaml` and `.include` paths |
| All transistors in **triode** | Wrong rail polarity for the device type | Verify VDD/VSS connectivity matches NMOS/PMOS |
| `singular matrix` | No DC path to ground / floating node | Add `.nodeset`, or check unconnected pins |
| Bias current = 0 | Current source in wrong direction | For NMOS diode: source-to-diode; for PMOS: diode-to-source |
| Subcircuit name mismatch | `.subckt` line doesn't match the `XDUT … <name>` call | Re-run `make xsch` after renaming the cell |
| Devices appear duplicated in SPICE | xschem `mult=` and `m=` both set | Set only one |

---

## 6. Useful References

- xschem manual: <https://xschem.sourceforge.io/stefan/index.html>
- ngspice manual: <https://ngspice.sourceforge.io/docs.html>
- aicex framework: <https://analogicus.com/aicex/>
- SKY130 PDK device docs: <https://skywater-pdk.readthedocs.io/>
