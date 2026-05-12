# Characterization Campaign Documentation

## Overview

Created automated wrapper scripts to generate 2D device characterization CSV files for multiple W/L combinations and process corners.

## Scripts Created

### 1. `characterize_measured_corner.py` (NEW)
Enhanced characterization script with **corner support**

**Usage:**
```bash
python3 characterize_measured_corner.py <W_um> <L_um> [corner]
```

**Parameters:**
- `W_um`: Device width in micrometers
- `L_um`: Device length in micrometers  
- `corner`: Process corner (default: "typical")
  - `tt`: Typical-Typical
  - `ss`: Slow-Slow (worst speed)
  - `ff`: Fast-Fast (worst power)
  - `sf`: Slow-Fast (asymmetric)
  - `fs`: Fast-Slow (asymmetric)

**Output:**
- Generates `characterize_2d_<corner>.csv` files
- Each corner gets its own CSV with 641 saturated points per W/L combination
- Added "Corner" column to identify corner in merged datasets

**Example:**
```bash
python3 characterize_measured_corner.py 40 0.8 tt
python3 characterize_measured_corner.py 60 1.0 ss
```

### 2. `characterize_all.sh` (NEW)
Automated campaign wrapper for bulk characterization

**Usage:**
```bash
./characterize_all.sh
```

**Features:**
- Runs all W/L/Corner combinations automatically
- Generates individual CSV files for each corner
- Creates progress log with timestamps
- Tracks success/failure rates
- Reports statistics at completion

**Configuration (edit in script):**
```bash
WIDTHS=(5 10 15 20 25 30 35 40 45 50 80 100)    # µm
LENGTHS=(0.8 0.9 1.0)                            # µm
CORNERS=(tt ss ff sf fs)                         # Process corners
```

**Output Structure:**
```
characterize_2d_csvs/
├── characterize_2d_tt.csv     (Typical corner)
├── characterize_2d_ss.csv     (Slow corner)
├── characterize_2d_ff.csv     (Fast corner)
├── characterize_2d_sf.csv     (Slow-Fast)
├── characterize_2d_fs.csv     (Fast-Slow)
└── campaign.log               (Execution log)
```

---

## Recommended Width/Length Matrix

### Suggested Widths (WITH rationale)

**NARROW (Low bias current):**
- `2 µm` - Reference circuits, current mirrors (if available)
- `5 µm` - Minimum bias design
- `10 µm` - Low power comparators

**MEDIUM (General purpose):**
- `15 µm` - Bias and cascode references ← SWEET SPOT
- `20 µm` - Medium current, medium gm
- `25 µm` - Input pair sizing
- `30 µm` - Common-mode feedback
- `40 µm` - **RECOMMENDED for max gain** ← Your choice
- `50 µm` - Output stages, mirror load

**LARGE (Power-critical):**
- `80 µm` - Rail-to-rail output buffers
- `100 µm` - Current mirrors with multiplier

**VERY LARGE (High current):**
- `200 µm` - Power output stages (optional)
- `500 µm` - Class AB output (optional)

### Current Setup (RECOMMENDED)

```bash
WIDTHS=(5 10 15 20 25 30 35 40 45 50 80 100)
LENGTHS=(0.8 0.9 1.0)
CORNERS=(tt ss ff sf fs)
```

**Total points:** 12 widths × 3 lengths × 5 corners = **180 simulations**
**Estimated time:** ~3 hours (0.7s per simulation + overhead)
**CSV size per corner:** ~9 KB each (641 points × 12 W values)
**Total data:** ~45 KB stored

---

## Campaign Execution

### Quick Test (Single device)
```bash
python3 characterize_measured_corner.py 40.0 0.8 tt
python3 characterize_measured_corner.py 40.0 0.8 ss
```

### Full Campaign
```bash
./characterize_all.sh
# Runs in background, monitor with:
tail -f characterize_2d_csvs/campaign.log
```

### Selective Campaign
Modify `characterize_all.sh` to run subset:
```bash
# Edit script and change:
WIDTHS=(40 50)           # Only W=40,50
LENGTHS=(0.8)            # Only L=0.8
CORNERS=(tt ss ff)       # Skip fs, sf
```

---

## Output Analysis

### Merge all corners into single CSV
```bash
cat characterize_2d_csvs/characterize_2d_*.csv | sort > characterize_2d_all_corners.csv
```

### Compare corners at specific W/L
```bash
# Find best bias (VGS) for W=40µm, L=0.8µm across all corners
for corner in tt ss ff sf fs; do
  echo "=== CORNER: $corner ==="
  awk -F, '$2=="40.00" && $3=="0.8000" {
    print $5, $9, $11, ($9/$11)
  }' characterize_2d_csvs/characterize_2d_${corner}.csv | \
  sort -k4 -rn | head -1
done
```

### Statistical analysis
```python
import pandas as pd
import glob

# Load all corners
dfs = []
for corner_file in glob.glob('characterize_2d_csvs/*.csv'):
    df = pd.read_csv(corner_file)
    dfs.append(df)

data = pd.concat(dfs)

# Group by W/L and corner
grouped = data.groupby(['Corner', 'W_um', 'L_um'])['gm_measured_uS'].agg(['mean', 'std', 'min', 'max'])
print(grouped)
```

---

## CSV Schema

All corner CSVs include:

| Column | Type | Notes |
|--------|------|-------|
| Corner | string | "tt", "ss", "ff", "sf", "fs" |
| W_um | float | Device width in µm |
| L_um | float | Device length in µm |
| WL_ratio | float | W/L ratio |
| VGS_V | float | Gate-source voltage (0-1.8V) |
| VDS_V | float | Drain-source voltage (0.1-1.8V) |
| Vov_V | float | Overdrive voltage (VGS - VTH) |
| ID_measured_A | float | Drain current (A) |
| ID_per_W_uA_um | float | Current normalized (µA/µm) |
| gm_measured_uS | float | Transconductance (µS) |
| gm_ID_S_A | float | Efficiency ratio (S/A) |
| gds_measured_uS | float | Output conductance (µS) |
| Cgs_measured_F | float | Gate-source capacitance (F) |
| Cgd_measured_F | float | Gate-drain capacitance (F) |
| Cdb_measured_F | float | Drain-bulk capacitance (F) |
| Csb_measured_F | float | Source-bulk capacitance (F) |

---

## Corner Descriptions

- **tt (Typical)**: Nominal device, nominal supply
- **ss (Slow)**: Slow devices, slow supply → Higher Vth, lower gm
- **ff (Fast)**: Fast devices, fast supply → Lower Vth, higher gm
- **sf (Slow-Fast)**: Slow NMOS, fast substrate (asymmetric)
- **fs (Fast-Slow)**: Fast NMOS, slow substrate (asymmetric)

**Why run all 5?**
- Design must work across all corners
- PVT (Process-Voltage-Temperature) margin analysis
- Monte Carlo yield prediction
- Worst-case gain/speed identification

---

## Notes

- Each simulation runs in parallel (19 cores)
- DC sweep: 0.05V steps (1,295 points)
- Saturated region: ~641 points per device
- Physics-based capacitance extraction (1 GHz reference)
- Total campaign time: ~3 hours for 180 simulations

## Next Steps

1. Verify corner support works with one device
2. Run full campaign
3. Analyze corner variations
4. Select optimal W/L for your design
5. Merge data for machine learning / design automation
