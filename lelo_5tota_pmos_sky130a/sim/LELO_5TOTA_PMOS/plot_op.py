#!/usr/bin/env python3
"""
plot_op.py — Pretty-print operating-point results from an ngspice ASCII .raw file.
Vov values are looked up from the characterization CSV (VSB=0, no body effect).

Usage:
    python3 plot_op.py [path/to/op_*.raw]

If no argument is given the most-recent file in output_op/ is used.
"""

import sys
import os
import glob
import re
import csv as csvmod

# ---------------------------------------------------------------------------
# CSV paths (edit if moved)
# ---------------------------------------------------------------------------
NMOS_CSV = "/home/pavand96/pro/aicex/ip/lelo_modele_sky130a/sim/LELO_MODELE/characterize_2d_csvs/characterize_2d_tt.csv"
PMOS_CSV = "/home/pavand96/pro/aicex/ip/lelo_pmodele_sky130a/sim/LELO_PMODELE/characterize_2d_csvs/characterize_2d_tt.csv"

# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------
def load_csv(path):
    rows = []
    with open(path) as f:
        for r in csvmod.DictReader(f):
            try:
                rows.append({
                    'w':   float(r['W_um']),
                    'l':   float(r['L_um']),
                    'vgs': float(r['VGS_V']),
                    'vds': float(r['VDS_V']),
                    'vov': float(r['Vov_V']),
                    'id':  float(r['ID_measured_A']),
                    'gm':  float(r['gm_measured_uS']) * 1e-6,
                    'rds': float(r['rds_measured_Ohm']),
                })
            except (ValueError, KeyError):
                pass
    return rows

def csv_lookup(rows, W, L, VGS, VDS):
    """Bilinear interpolation in VGS x VDS at nearest W/L from the CSV."""
    # Find nearest W in the CSV
    avail_w = sorted(set(r['w'] for r in rows if abs(r['l'] - L) < 0.01))
    if not avail_w:
        return None
    nearest_w = min(avail_w, key=lambda w: abs(w - W))
    cands = [r for r in rows if abs(r['w'] - nearest_w) < 0.1 and abs(r['l'] - L) < 0.01]

    vgs_vals = sorted(set(r['vgs'] for r in cands))
    vds_vals = sorted(set(r['vds'] for r in cands))

    vgs_lo = max((v for v in vgs_vals if v <= VGS), default=min(vgs_vals))
    vgs_hi = min((v for v in vgs_vals if v >= VGS), default=max(vgs_vals))
    vds_lo = max((v for v in vds_vals if v <= VDS), default=min(vds_vals))
    vds_hi = min((v for v in vds_vals if v >= VDS), default=max(vds_vals))

    def get(vgs, vds):
        hits = [r for r in cands if abs(r['vgs'] - vgs) < 1e-6 and abs(r['vds'] - vds) < 1e-6]
        return hits[0] if hits else None

    corners = {
        (0, 0): get(vgs_lo, vds_lo),
        (1, 0): get(vgs_hi, vds_lo),
        (0, 1): get(vgs_lo, vds_hi),
        (1, 1): get(vgs_hi, vds_hi),
    }
    if any(v is None for v in corners.values()):
        return min(cands, key=lambda r: (r['vgs'] - VGS)**2 + (r['vds'] - VDS)**2)

    tx = (VGS - vgs_lo) / (vgs_hi - vgs_lo) if vgs_hi != vgs_lo else 0.0
    ty = (VDS - vds_lo) / (vds_hi - vds_lo) if vds_hi != vds_lo else 0.0
    result = {}
    for key in ('vov', 'id', 'gm', 'rds'):
        ll = corners[(0, 0)][key]
        hl = corners[(1, 0)][key]
        lh = corners[(0, 1)][key]
        hh = corners[(1, 1)][key]
        result[key] = (1 - tx) * (1 - ty) * ll + tx * (1 - ty) * hl + \
                      (1 - tx) * ty * lh + tx * ty * hh
    return result

nmos_rows = load_csv(NMOS_CSV)
pmos_rows = load_csv(PMOS_CSV)

# ---------------------------------------------------------------------------
# 1. Locate raw file
# ---------------------------------------------------------------------------

def find_raw():
    candidates = sorted(glob.glob("output_op/op_*.raw"))
    if not candidates:
        sys.exit("No raw file found in output_op/")
    return candidates[-1]

raw_path = sys.argv[1] if len(sys.argv) > 1 else find_raw()
print(f"Reading: {raw_path}\n")

# ---------------------------------------------------------------------------
# 2. Parse ASCII raw file
# ---------------------------------------------------------------------------

with open(raw_path) as f:
    lines = f.readlines()

# Split into header and values sections
header, values = [], []
in_values = False
for line in lines:
    if line.strip().lower().startswith("values:"):
        in_values = True
        continue
    if in_values:
        values.append(line.strip())
    else:
        header.append(line.strip())

# Parse variable names in order
variables = {}  # index -> (name, kind)
for line in header:
    m = re.match(r"(\d+)\s+(\S+)\s+(\S+)", line)
    if m:
        idx, name, kind = int(m.group(1)), m.group(2), m.group(3)
        variables[idx] = (name, kind)

n_vars = len(variables)

# Parse values — first value has index prefix ("0   <val>"), rest are plain
data = {}
raw_vals = []
for line in values:
    if not line:
        continue
    # Strip leading index number for point 0
    m = re.match(r"^\d+\s+([\deE+\-.]+)$", line)
    if m:
        raw_vals.append(float(m.group(1)))
    else:
        try:
            raw_vals.append(float(line))
        except ValueError:
            pass

for i, (name, kind) in variables.items():
    if i < len(raw_vals):
        data[name] = raw_vals[i]

# ---------------------------------------------------------------------------
# 3. Display helpers
# ---------------------------------------------------------------------------

SEP  = "─" * 58
SEP2 = "═" * 58

def v(name):
    return data.get(name, float("nan"))

def fmt_v(val):
    return f"{val*1e3:+10.3f} mV  ({val:+.6f} V)"

def fmt_i(val):
    if abs(val) >= 1e-3:
        return f"{val*1e3:+10.3f} mA  ({val:+.6e} A)"
    return f"{val*1e6:+10.3f} µA  ({val:+.6e} A)"

# ---------------------------------------------------------------------------
# 4. Node voltages
# ---------------------------------------------------------------------------

node_map = [
    ("VDD",         "v(vdd)"),
    ("VSS",         "v(vss)"),
    ("VINP",        "v(vinp)"),
    ("VINN",        "v(vinn)"),
    ("VOUT",        "v(vout)"),
    ("IBIAS",       "v(ibias)"),
    ("Vtail (net1)","v(xdut.net1)"),
    ("net2",        "v(xdut.net2)"),
]

print(SEP2)
print(f"  {'NODE VOLTAGES':^54}")
print(SEP2)
print(f"  {'Node':<18}  {'Value':>28}")
print(SEP)
for label, key in node_map:
    val = v(key)
    print(f"  {label:<18}  {fmt_v(val)}")

# ---------------------------------------------------------------------------
# 5. Branch currents
# ---------------------------------------------------------------------------

cur_map = [
    ("I(VDD)",   "i(vdd)"),
    ("I(VSS)",   "i(vss)"),
    ("I(VVINP)", "i(vvinp)"),
    ("I(VVINM)", "i(vvinm)"),
]

print()
print(SEP2)
print(f"  {'BRANCH CURRENTS':^54}")
print(SEP2)
print(f"  {'Source':<18}  {'Value':>28}")
print(SEP)
for label, key in cur_map:
    val = v(key)
    print(f"  {label:<18}  {fmt_i(val)}")

# ---------------------------------------------------------------------------
# 6. Device operating points
#   (W, L) used only for CSV lookup — not printed
#   PMOS: ngspice [vgs]=VSG, [vds]=VSD (source-referenced, positive)
#         CSV also characterizes with VSG/VSD positive → same lookup convention
# ---------------------------------------------------------------------------

# (label, type, W_um, L_um, csv_rows, connections)
devices = [
    ("XM1", "NMOS", 80.0, 0.8, nmos_rows, "G=VINP  D=net2  S=net1"),
    ("XM2", "NMOS", 80.0, 0.8, nmos_rows, "G=VINN  D=VOUT  S=net1"),
    ("XM3", "PMOS", 36.0, 0.8, pmos_rows, "G=D=net2  S=VDD  (diode)"),
    ("XM4", "PMOS", 36.0, 0.8, pmos_rows, "G=net2  D=VOUT  S=VDD  (mirror out)"),
    ("XM5", "NMOS", 36.0, 1.0, nmos_rows, "G=IBIAS D=net1  S=VSS  (tail)"),
    ("XM6", "NMOS", 36.0, 1.0, nmos_rows, "G=D=IBIAS  S=VSS  (bias diode)"),
]

print()
print(SEP2)
print(f"  {'DEVICE OPERATING POINTS':^54}")
print(SEP2)

for dev, typ, W, L, rows, conn in devices:
    pfx = dev.lower()
    vgs = v(f"{pfx}_vgs")
    vds = v(f"{pfx}_vds")

    lkp = csv_lookup(rows, W, L, vgs, vds)
    if lkp:
        vov_csv = lkp['vov']
        region  = "SAT  " if vds > vov_csv else "TRIODE"
        sat_margin = vds - vov_csv
    else:
        vov_csv = float('nan')
        region  = "?"
        sat_margin = float('nan')

    print(SEP)
    print(f"  {dev}  {typ}   {conn}")
    print(f"    VGS = {vgs:+.4f} V    VDS = {vds:+.4f} V")
    print(f"    Vov = {vov_csv:+.4f} V  (CSV, VSB=0)")
    print(f"    VDS - Vov = {sat_margin:+.4f} V  →  [{region}]")

print(SEP2)
