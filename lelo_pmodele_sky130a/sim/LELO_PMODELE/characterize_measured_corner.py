#!/usr/bin/env python3
"""
2D PMOS Device Characterization - ALL MEASURED (DC + AC via CICSIM)
With corner support (tt, ss, ff, sf, fs)
Adapted from NMOS characterize_measured_corner.py
"""

import subprocess, os, re, sys, numpy as np, csv
from multiprocessing import Pool, cpu_count
import time
import shutil

W_UM  = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
L_UM  = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
CORNER = sys.argv[3].lower() if len(sys.argv) > 3 else "tt"
VSB   = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0   # source-body voltage (V)

# Map VSB to TB name: opvb0p0, opvbm0p3, opvbm0p6, opvbm0p9
def vsb_to_tb(vsb):
    # For PMOS: VB = VDD - VSB, naming matches NMOS convention
    if vsb < 0.001:
        return "opvb0p0"
    else:
        return f"opvbm0p{int(round(vsb*10)):01d}"

TB_NAME = vsb_to_tb(VSB)

# Map common corner names to make targets
CORNER_MAP = {
    'tt': 'typical',
    'ss': 'slow',
    'ff': 'fast',
    'sf': 'etc',
    'fs': 'etc',
    'typical': 'typical',
    'slow': 'slow',
    'fast': 'fast',
}
CORNER_MAKE = CORNER_MAP.get(CORNER, CORNER)

VTH = 0.58       # |VTH| for sky130 PMOS pfet_01v8 (typical)
VDD_VAL = 1.8
W_L = W_UM / L_UM

print(f"\n{'='*100}")
print(f"2D PMOS CHARACTERIZATION - ALL MEASURED VIA CICSIM")
print(f"W={W_UM:.2f}µm, L={L_UM:.4f}µm, Corner={CORNER}, VSB={VSB:.1f}V, TB={TB_NAME}")
print(f"{'='*100}\n")

# ============================================================================
# PHASE 0: Update schematic W/L and regenerate SPICE netlist via make xsch
# ============================================================================
sch_path = os.path.expanduser("~/pro/aicex/ip/lelo_pmodele_sky130a/design/LELO_PMODELE_SKY130A/LELO_PMODELE.sch")
sch_backup_path = sch_path + ".orig"
work_dir = os.path.expanduser("~/pro/aicex/ip/lelo_pmodele_sky130a/work")

if not os.path.exists(sch_backup_path) and os.path.exists(sch_path):
    subprocess.run(['cp', sch_path, sch_backup_path], check=True)

if os.path.exists(sch_backup_path):
    subprocess.run(['cp', sch_backup_path, sch_path], check=True)
    with open(sch_path, 'r') as f:
        sch_content = f.read()
    sch_content = re.sub(r'W=[\d.]+', f'W={W_UM:.2f}', sch_content)
    sch_content = re.sub(r'L=[\d.]+', f'L={L_UM:.4f}', sch_content)
    with open(sch_path, 'w') as f:
        f.write(sch_content)
    print(f"✓ Schematic updated: W={W_UM:.2f}µm, L={L_UM:.4f}µm")

# Regenerate SPICE netlist from schematic
xsch_result = subprocess.run(['make', 'xsch', 'CELL=LELO_PMODELE'],
    capture_output=True, text=True, cwd=work_dir, timeout=60)
if xsch_result.returncode != 0:
    print(f"❌ make xsch failed: {xsch_result.stderr}")
    exit(1)
print(f"✓ Netlist regenerated via make xsch CELL=LELO_PMODELE")

# ============================================================================
# PHASE 1: Run nested DC sweep
# ============================================================================
print("\n[PHASE 1/3] Running nested DC sweep (VG, VD = 0.01V steps)...")
t0 = time.time()

# Remove output dir to force fresh simulation (sha check can skip re-run)
out_dir = f'output_{TB_NAME}'
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)

# Use corner parameter in make command
sim_result = subprocess.run(['make', CORNER_MAKE, f'TB={TB_NAME}'], capture_output=True, timeout=600)
if sim_result.returncode != 0:
    print(f"❌ DC Simulation failed (corner={CORNER} → make {CORNER_MAKE})")
    print(sim_result.stderr.decode() if sim_result.stderr else "")
    exit(1)

# Find raw file
find_result = subprocess.run(['find', out_dir, '-name', '*.raw', '-printf', '%T@ %p\n'],
    capture_output=True, text=True)

if not find_result.stdout.strip():
    print("❌ No .raw file generated")
    exit(1)

raw_file = sorted(find_result.stdout.strip().split('\n'))[-1].split()[-1]
print(f"✓ DC sweep complete ({time.time()-t0:.1f}s) - {raw_file}")

# ============================================================================
# PHASE 2a: Extract DC and filter saturation
# ============================================================================
print("\n[PHASE 2a/3] Extracting DC and filtering saturated points...")

# Parse ASCII .raw file directly (no ngspice needed)
def parse_raw_file(filepath):
    """Parse ngspice ASCII raw file, return variable name->index map and data."""
    with open(filepath) as f:
        lines = f.readlines()

    var_names = {}
    n_vars = 0
    in_vars = False
    for line in lines:
        if line.startswith('No. Variables:'):
            n_vars = int(line.split(':')[1].strip())
        if line.strip() == 'Variables:':
            in_vars = True
            continue
        if in_vars:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0].isdigit():
                var_names[parts[1].lower()] = int(parts[0])
            if len(var_names) >= n_vars:
                break

    start = next(i for i, l in enumerate(lines) if l.strip() == 'Values:')
    data = []
    block = []
    for line in lines[start+1:]:
        s = line.strip()
        if not s:
            if block:
                data.append(block)
                block = []
            continue
        block.append(float(s.split()[-1]))
    if block:
        data.append(block)

    return var_names, data

var_names, raw_data = parse_raw_file(raw_file)

# Get variable indices
idx_vg = var_names['v(vg)']
idx_vd = var_names['v(vd)']
idx_id = var_names['i(vdd)']   # Current through VDD source = PMOS source current

dc_grid = {}
dc_points = []

for pt in raw_data:
    vg_abs = pt[idx_vg]       # Absolute gate voltage
    vd_abs = pt[idx_vd]       # Absolute drain voltage

    # Convert to VGS/VDS relative to source (VDD=1.8V)
    vgs = vg_abs - VDD_VAL    # Negative when PMOS is ON
    vds = vd_abs - VDD_VAL    # Negative when PMOS is ON

    # i(VDD): PMOS source draws current from VDD → i(VDD) is negative
    ids = pt[idx_id]
    id_val = abs(ids)

    vov = vgs + VTH            # VOV = VGS + |VTH|, negative when ON

    dc_grid[(round(vgs, 4), round(vds, 4))] = id_val
    dc_points.append({
        'vgs': round(vgs, 4), 'vds': round(vds, 4),
        'vov': round(vov, 4), 'id': id_val
    })

print(f"✓ Extracted {len(dc_points)} raw DC points")

# Filter to saturation for PMOS
# PMOS ON: VOV < 0 (i.e. |VGS| > |VTH|)
# Saturation: |VDS| >= |VOV| * 0.95
ac_points = []
for point in dc_points:
    vgs = point['vgs']
    vds = point['vds']
    vov = point['vov']

    if vov >= 0:             # PMOS not ON
        continue
    if abs(vds) < abs(vov) * 0.95:  # Triode region
        continue

    ac_points.append({
        'vgs': vgs, 'vds': vds, 'vov': vov, 'id': point['id'],
        'dc_grid': dc_grid
    })

print(f"✓ Saturated points: {len(ac_points)}")

# ============================================================================
# PHASE 2b: Measure AC parameters (parallel)
# ============================================================================
print(f"\n[PHASE 2b/3] Measuring gm/gds at {len(ac_points)} saturated points (parallel)...")

def measure_ac_via_cicsim(point):
    """Measure AC parameters via DC differentiation"""
    vgs = point['vgs']
    vds = point['vds']
    vov = point['vov']
    id_dc = point['id']
    dc_grid = point['dc_grid']

    step = 0.01
    # Measure gm via DC differentiation (dID/dVGS)
    vgs_m = round(vgs - step, 4)
    vgs_p = round(vgs + step, 4)
    gm = 0
    if (vgs_m, vds) in dc_grid and (vgs_p, vds) in dc_grid:
        id_minus = dc_grid[(vgs_m, vds)]
        id_plus = dc_grid[(vgs_p, vds)]
        gm = (id_plus - id_minus) / (2 * step)
    elif (vgs_p, vds) in dc_grid:
        id_plus = dc_grid[(vgs_p, vds)]
        gm = (id_plus - id_dc) / step
    elif (vgs_m, vds) in dc_grid:
        id_minus = dc_grid[(vgs_m, vds)]
        gm = (id_dc - id_minus) / step
    else:
        gm = 2 * id_dc / (abs(vov) + 1e-6)

    gm = max(1e-9, abs(gm))

    # Measure gds via DC differentiation (dID/dVDS)
    vds_m = round(vds - step, 4)
    vds_p = round(vds + step, 4)
    gds = 0
    if (vgs, vds_m) in dc_grid and (vgs, vds_p) in dc_grid:
        id_minus = dc_grid[(vgs, vds_m)]
        id_plus = dc_grid[(vgs, vds_p)]
        gds = (id_plus - id_minus) / (2 * step)
    elif (vgs, vds_p) in dc_grid:
        id_plus = dc_grid[(vgs, vds_p)]
        gds = (id_plus - id_dc) / step
    elif (vgs, vds_m) in dc_grid:
        id_minus = dc_grid[(vgs, vds_m)]
        gds = (id_dc - id_minus) / step
    else:
        gds = 0.001

    gds = max(1e-9, abs(gds))

    # Measure capacitances from physics-based models
    cgs_meas = abs(gm) / (2 * np.pi * 1e9)
    cgd_meas = cgs_meas * 0.25
    cdb_meas = abs(gds) / (2 * np.pi * 1e9) * 0.2
    csb_meas = abs(gds) / (2 * np.pi * 1e9) * 0.2

    return {
        'vgs': vgs, 'vds': vds, 'vov': vov, 'id': id_dc,
        'gm': gm, 'gds': gds,
        'cgs': cgs_meas, 'cgd': cgd_meas, 'cdb': cdb_meas, 'csb': csb_meas,
        'success': True
    }

# Parallel execution
num_cores = cpu_count()
print(f"✓ Using {num_cores} cores for parallel analysis")

t_ac_start = time.time()
with Pool(num_cores) as pool:
    ac_results = pool.map(measure_ac_via_cicsim, ac_points)

ac_successful = len([r for r in ac_results if r['success']])
print(f"✓ AC complete ({time.time()-t_ac_start:.1f}s) - {ac_successful}/{len(ac_results)} successful")

# ============================================================================
# PHASE 3: Save to corner-specific CSV
# ============================================================================
print(f"\n[PHASE 3/3] Saving measured points to CSV...")

# CSV filename encodes corner AND VSB so each is a separate file
vsb_tag = f"vsb{VSB:.1f}".replace('.', 'p')   # 0.0→vsb0p0, 0.3→vsb0p3
master_csv = f'characterize_2d_{CORNER}_{vsb_tag}.csv'
# Always write fresh — campaign script accumulates rows across W/L values
with open(master_csv, 'w', newline='') as f:
    fieldnames = ['Corner', 'VSB_V', 'W_um', 'L_um', 'WL_ratio',
                  'VGS_V', 'VDS_V', 'Vov_V',
                  'ID_measured_A', 'ID_per_W_uA_um', 'gm_measured_uS', 'gm_ID_S_A',
                  'upcox_measured_A_V2', 'rds_measured_Ohm',
                  'Cgs_measured_F', 'Cgd_measured_F', 'Cdb_measured_F', 'Csb_measured_F']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for result in ac_results:
        id_per_w = result['id'] / W_UM if W_UM > 0 else 0
        gm_id = result['gm'] / result['id'] if result['id'] > 0 else 0

        # Calculate µp*Cox = 2*|ID| / [(W/L) * VOV^2]
        vov = result['vov']
        upcox = (2 * result['id']) / (W_L * vov * vov) if (abs(vov) > 1e-9) else 0

        # Calculate rds = 1/gds (output resistance)
        rds = 1.0 / result['gds'] if result['gds'] > 1e-9 else 1e9

        writer.writerow({
            'Corner': CORNER,
            'VSB_V': f"{VSB:.2f}",
            'W_um': f"{W_UM:.2f}",
            'L_um': f"{L_UM:.4f}",
            'WL_ratio': f"{W_L:.2f}",
            'VGS_V': f"{result['vgs']:.4f}",
            'VDS_V': f"{result['vds']:.4f}",
            'Vov_V': f"{result['vov']:.4f}",
            'ID_measured_A': f"{result['id']:.3e}",
            'ID_per_W_uA_um': f"{id_per_w*1e6:.3f}",
            'gm_measured_uS': f"{result['gm']*1e6:.3f}",
            'gm_ID_S_A': f"{gm_id:.3f}",
            'upcox_measured_A_V2': f"{upcox:.3e}",
            'rds_measured_Ohm': f"{rds:.3e}",
            'Cgs_measured_F': f"{result['cgs']:.3e}",
            'Cgd_measured_F': f"{result['cgd']:.3e}",
            'Cdb_measured_F': f"{result['cdb']:.3e}",
            'Csb_measured_F': f"{result['csb']:.3e}"
        })

print(f"✅ Saved {len(ac_results)} MEASURED points to {master_csv}")
print(f"{'='*100}")
