# Analog IC Designs — SKY130A PDK

Analog IC design work using the [aicex](https://analogicus.com/aicex/) framework on the open-source **SkyWater SKY130A** process. All schematics are drawn in [xschem](https://xschem.sourceforge.io/), simulated with [ngspice](http://ngspice.sourceforge.net/) via the [cicsim](https://github.com/wulffern/cicsim) automation framework.

**Author:** Pavan Devarasetti

---

## Designs at a Glance

| Design | Type | Simulations | Key Results |
|--------|------|-------------|-------------|
| [`lelo_ex_sky130a`](#1-lelo_ex_sky130a--current-mirror-exercise) | Current mirror | Transient | $I_{out}$ = 19.4 µA, $V_{GS}$ = 1.005 V |
| [`lelo_ex1_sky130a`](#2-lelo_ex1_sky130a--common-source-amplifier) | CS amplifier | AC, DC, OP, Tran, Sweep | Peak gain 23.47 dB, GBW up to 12.7 GHz |
| [`lelo_5tota_sky130a`](#3-lelo_5tota_sky130a--5-transistor-ota) | 5T OTA (NMOS input) | AC, DC (ICMR/OCMR), OP, Tran, Slew | Open-loop gain, phase margin, CMRR |
| [`lelo_5tota_pmos_sky130a`](lelo_5tota_pmos_sky130a/sim/LELO_5TOTA_PMOS/README.md) | 5T OTA (**PMOS input**) | Same as above | Complementary topology — low 1/f noise, ground-near input CMR |
| [`lelo_modele_sky130a`](#4-lelo_modele_sky130a--nmos-device-characterization) | NMOS char. | 2D DC sweep, multi-corner | 47k+ data points across tt/ss/ff corners |
| [`lelo_pmodele_sky130a`](#5-lelo_pmodele_sky130a--pmos-device-characterization) | PMOS char. | 2D DC sweep, multi-corner | Mirrors NMOS campaign for PMOS devices |

> **New:** See [`SCH_TO_SPICE_GUIDE.md`](SCH_TO_SPICE_GUIDE.md) for a practical guide to the xschem `.sch` ↔ ngspice `.spice` workflow, including a worked recipe for the NMOS→PMOS 5T OTA conversion.

---

## 1. `lelo_ex_sky130a` — Current Mirror Exercise

**Cell:** `LELO_EX` &nbsp;|&nbsp; **Ports:** `IBPS_5U`, `VSS`, `IBPS_20U`

A basic current mirror biasing exercise — the starting point of the aicex course. A 5 µA reference current is mirrored to produce a scaled output current.

### Simulation

| Analysis | What's measured |
|----------|----------------|
| **Transient** | Output current $I_{BN}$ and gate-source voltage $V_{GS}$ at steady state |

### Results (typical corner)

| Parameter | Spec | Measured |
|-----------|------|----------|
| Output current ($I_{BN}$) | 20 µA ± 5 % | **19.4 µA** |
| Gate-source voltage ($V_{GS}$) | 0.3 – 0.8 V | **1.005 V** |

### Files

```
lelo_ex_sky130a/
├── design/LELO_EX_SKY130A/LELO_EX.sch    # xschem schematic
├── sim/LELO_EX/
│   ├── tran.spi / tran.meas / tran.yaml  # testbench + measurement + spec
│   ├── results/tran_Sch_typical.*         # cicsim output (CSV, HTML, MD)
│   └── xdut.spi                           # auto-generated DUT instance
└── work/xsch/LELO_EX.spice               # extracted SPICE netlist
```

---

## 2. `lelo_ex1_sky130a` — Common-Source Amplifier

**Cell:** `LELO_EX1` &nbsp;|&nbsp; **Ports:** `VOUT`, `VSS`, `VDD`, `VIN`

A resistively loaded common-source NMOS amplifier. The design was explored through a **60-point parametric sweep** across transistor width ($W$), load resistance ($R$), and input bias ($V_{IN}$) to map the gain–bandwidth trade-off.

### Simulations

| Analysis | Purpose |
|----------|---------|
| **AC** | Small-signal gain (dB), $f_{3\text{dB}}$, GBW (1 Hz – 10 GHz, 1000 pts/decade) |
| **DC** | Transfer curve $V_{OUT}$ vs $V_{IN}$ (0 → $V_{DD}$) |
| **OP** | Quiescent operating point: $V_{OUT}$, $I_{DD}$, $V_{GS}$, $V_{DS}$ |
| **Transient** | Time-domain step / sine response |
| **Parametric sweep** | Automated 60-combination sweep (W × R × VIN) |

### Parametric Sweep Results

**Sweep space:** $W \in \{20, 40, 60\}$ µm, $R \in \{5, 10, 15, 20\}$ kΩ, $V_{IN} \in \{0.5 ... 0.9\}$ V

**12 out of 60** combinations achieved proper saturation ($0.3 < V_{OUT} < 1.5$ V).

#### Top performers

| Config | Peak Gain | $f_{3\text{dB}}$ | GBW | $V_{OUT}$ |
|--------|-----------|-----------|-----|-----------|
| W=40µm, R=10kΩ, VIN=0.7V | **23.47 dB** | 603 MHz | 8.99 GHz | 0.570 V |
| W=20µm, R=5kΩ, VIN=0.9V | 12.43 dB | 3.03 GHz | **12.7 GHz** | 0.315 V |
| W=20µm, R=10kΩ, VIN=0.7V | 18.09 dB | 1.38 GHz | **11.1 GHz** | 1.19 V |

#### Design insights

- **Gain–bandwidth trade-off confirmed:** Higher $R$ → more gain but lower bandwidth
- **Width dependency:** Smaller $W$ = higher GBW (less parasitic capacitance)
- **Sweet spot:** W=20µm, R=10kΩ — 18 dB gain with 11.1 GHz GBW at only 61 µA

### Files

```
lelo_ex1_sky130a/
├── design/LELO_EX1_SKY130A/LELO_EX1.sch
├── sim/LELO_EX1/
│   ├── ac.spi / dc.spi / op.spi / tran.spi   # four testbenches
│   ├── ac.meas / dc.meas / op.meas / tran.meas
│   ├── sweep.py / sweep_make.py               # parametric sweep automation
│   ├── results.md                             # full sweep results table
│   ├── results/tran_Sch_typical.*
│   └── xdut.spi
└── work/xsch/LELO_EX1.spice
```

---

## 3. `lelo_5tota_sky130a` — 5-Transistor OTA

**Cell:** `LELO_5TOTA` &nbsp;|&nbsp; **Ports:** `VDD`, `VSS`, `VOUT`, `IBIAS`, `VINP`, `VINN`

A classical **5-transistor operational transconductance amplifier**: NMOS differential pair (M1/M2), PMOS active load mirror (M3/M4), NMOS tail current source (M5) biased via diode-connected M6. Designed with $I_{BIAS}$ = 6.26 µA and 1 pF load capacitor.

### Simulations

| Analysis | What's extracted |
|----------|-----------------|
| **AC** | Open-loop gain, $f_{3\text{dB}}$, GBW, phase margin, gain margin, group delay |
| **DC — ICMR** | Input common-mode range (sweep $V_{CM}$ 0 → $V_{DD}$, check tail/pair saturation) |
| **DC — OCMR** | Output common-mode range (sweep $V_{OUT}$, check M2/M4 saturation margins) |
| **OP** | All device operating points: $V_{GS}$, $V_{DS}$, $V_{OV}$, $I_D$, $g_m$, $g_{ds}$, region |
| **Transient** | 1 kHz differential sine response, 10 periods |
| **Slew rate** | Large-signal step response |

### AC measurement extractions

The AC testbench computes:
- **DC gain** (at 1 Hz)
- **–3 dB bandwidth** ($f_{3\text{dB}}$)
- **Unity-gain bandwidth** (GBW)
- **Phase margin** at unity gain
- **Gain margin** at –180° phase crossing
- **Group delay** at low frequency

### Custom plotting

- `plot_ac.py` — Bode plot (gain + phase) from raw ngspice AC data
- `plot_op.py` — Operating point bar charts for all 5 transistors

### Files

```
lelo_5tota_sky130a/
├── design/LELO_5TOTA_SKY130A/LELO_5TOTA.sch
├── sim/LELO_5TOTA/
│   ├── ac.spi / dc.spi / op.spi / tran.spi / slew.spi
│   ├── ac.meas / dc.meas / op.meas
│   ├── plot_ac.py / plot_op.py        # custom visualization
│   ├── README.md                      # ngspice tips & device parameter guide
│   └── xdut.spi
└── work/xsch/LELO_5TOTA.spice
```

---

## 4. `lelo_modele_sky130a` — NMOS Device Characterization

**Cell:** `LELO_MODELE` &nbsp;|&nbsp; **Ports:** `VD`, `VS`, `VG`, `VB`

Comprehensive **2D characterization** of `sky130_fd_pr__nfet_01v8` across the full operating space. The goal: build a look-up table of measured device parameters for hand-design use.

### What was done

1. **2D nested DC sweep** — $V_{DS}$ (0.1 → 1.8 V) × $V_{GS}$ (0 → 1.8 V) = ~31,000 points per simulation
2. **Automated schematic W/L update** — Python script modifies the xschem `.sch`, regenerates the SPICE netlist, runs the simulation, and extracts parameters
3. **Multi-corner campaign** — Typical (tt), Slow (ss), Fast (ff) corners
4. **Multiple device geometries** — W: 5 µm to 100 µm, L: 0.8 µm to 1.0 µm

### Extracted parameters (per operating point)

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| Drain current | $I_D$ | Measured from DC sweep |
| Current density | $I_D / W$ | Normalized per-micron |
| Transconductance | $g_m$ | From ngspice OP |
| $g_m / I_D$ | — | Efficiency metric |
| $\mu_n C_{ox}$ | — | Back-extracted process parameter |
| Output resistance | $r_{ds}$ | $1 / g_{ds}$ |
| Capacitances | $C_{gs}$, $C_{gd}$, $C_{db}$, $C_{sb}$ | From AC extraction |

### Dataset

| Metric | Value |
|--------|-------|
| Total data points | **47,415** (across 3 CSV files) |
| Corners | tt, ss, ff |
| Saturation filter | $V_{DS} \geq 0.95 \times V_{ov}$ |
| Device widths | 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 80, 100 µm |
| Device lengths | 0.8, 0.9, 1.0 µm |

### Physics validation

- **$g_m/I_D$ constancy:** Verified $g_m/I_D = 2/V_{ov}$ — mean error < 0.1% for $V_{ov} > 0.12$ V
- **$A_{v0}$ accuracy:** Open-circuit gain $A_{v0} = 2/(\lambda V_{ov})$ with $\lambda = 0.05\ \text{V}^{-1}$ — mean error **0.03%**
- **W/L independence:** Same operating-point parameters confirmed across geometries (W: 5 → 40 µm, L: 0.15 → 0.8 µm)

### Files

```
lelo_modele_sky130a/
├── design/LELO_MODELE_SKY130A/LELO_MODELE.sch
├── sim/LELO_MODELE/
│   ├── op.spi                              # 2D nested DC sweep testbench
│   ├── ac.spi                              # AC characterization
│   ├── characterize_measured_corner.py      # automated extraction script
│   ├── characterize_all.sh                  # campaign automation wrapper
│   ├── characterize_2d_{tt,ss,ff}_vsb0p0.csv  # extracted data (summary)
│   ├── 2D_CHARACTERIZATION_README.md        # methodology documentation
│   ├── CHARACTERIZATION_CAMPAIGN.md         # campaign configuration
│   └── opvb{0p0,m0p3,m0p6,m0p9}.spi       # body-bias sweep testbenches
└── work/xsch/LELO_MODELE.spice
```

> **Note:** Full characterization CSVs in `characterize_2d_csvs/` (~1.4 GB) are excluded from this repo via `.gitignore` due to GitHub's 100 MB per-file limit. The summary CSVs (2.2 MB each) with the same data at reduced resolution are included.

---

## 5. `lelo_pmodele_sky130a` — PMOS Device Characterization

**Cell:** `LELO_PMODELE` &nbsp;|&nbsp; **Ports:** `VDD`, `VG`, `VB`, `VD`

Mirrors the NMOS characterization for `sky130_fd_pr__pfet_01v8`. Same 2D sweep methodology adapted for PMOS polarity:
- Source/body tied to $V_{DD}$ = 1.8 V
- $V_D$: 1.7 → 0 V (reversed sweep direction)
- $V_G$: 1.8 → 0 V
- $|V_{TH}|$ = 0.58 V (typical)

### Testbenches

| TB | Description |
|----|-------------|
| `op.spi` | 2D nested sweep ($V_D$ outer, $V_G$ inner) |
| `ac.spi` | AC parameter extraction |
| `opvb{0p0,m0p3,m0p6,m0p9}.spi` | Body-bias variations |

### Automation

- `characterize_measured_corner.py` — Same automated pipeline as NMOS, adapted for PMOS conventions
- `characterize_all.sh` — Multi-corner, multi-geometry campaign wrapper

### Files

```
lelo_pmodele_sky130a/
├── design/LELO_PMODELE_SKY130A/LELO_PMODELE.sch
├── sim/LELO_PMODELE/
│   ├── op.spi / ac.spi                     # testbenches
│   ├── characterize_measured_corner.py      # PMOS extraction script
│   ├── characterize_all.sh                  # campaign wrapper
│   └── opvb{0p0,m0p3,m0p6,m0p9}.spi       # body-bias sweeps
└── work/xsch/LELO_PMODELE.spice
```

---

## Tools & Setup

| Tool | Purpose |
|------|---------|
| [aicex](https://analogicus.com/aicex/) | Course framework & IP library |
| [xschem](https://xschem.sourceforge.io/) | Schematic capture |
| [ngspice](http://ngspice.sourceforge.net/) | SPICE simulation |
| [cicsim](https://github.com/wulffern/cicsim) | Simulation automation (corner sweeps, measurements, results) |
| [SkyWater SKY130A PDK](https://github.com/google/skywater-pdk) | Open-source 130nm process |

### Running a simulation

```bash
cd <design>/sim/<cell>
make typical TB=tran    # run transient analysis, typical corner
make typical TB=ac      # run AC analysis
make etc TB=op          # run OP analysis across all corners
```

---

## License

These designs build upon the [aicex](https://github.com/wulffern/aicex) framework by Carsten Wulff.
