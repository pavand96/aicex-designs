#!/usr/bin/env python3
"""
Verify AC gain prediction with DC-measured parameters
DC analysis → extract gm, gds at operating point → predict AC gain
"""

import csv
import numpy as np

VDD = 1.8
VGS_TARGET = 0.60
RL = 50e3  # 50 kΩ
W_UM = 40.0
L_UM = 0.8

print(f"\n{'='*100}")
print(f"AC GAIN VERIFICATION - Common Source with RL = {RL/1e3:.0f}kΩ")
print(f"{'='*100}\n")

# Load the CSV data
with open('characterize_2d_all_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    points_at_vgs = []
    for row in reader:
        if float(row['W_um']) == W_UM and float(row['L_um']) == L_UM and abs(float(row['VGS_V']) - VGS_TARGET) < 0.01:
            points_at_vgs.append(row)

points_at_vgs.sort(key=lambda x: float(x['VDS_V']))

print(f"VGS={VGS_TARGET}V sweep (from CSV):")
print(f"{'VDS (V)':<10} {'ID (µA)':<12} {'gm (µS)':<12} {'gds (nS)':<12}")
print("-" * 50)

for p in points_at_vgs:
    vds = float(p['VDS_V'])
    id_ua = float(p['ID_measured_A']) * 1e6
    gm = float(p['gm_measured_uS'])
    gds = float(p['gds_measured_uS']) * 1e3  # Convert to nS
    print(f"{vds:<10.3f} {id_ua:<12.3f} {gm:<12.3f} {gds:<12.3f}")

print(f"\n" + "="*100)
print(f"\nFINDING LOAD LINE INTERSECTION...")

# Find intersection: VDS_load = VDD - ID * RL intersects device curve
min_error = float('inf')
operating_point = None

for p in points_at_vgs:
    vds_device = float(p['VDS_V'])
    id_device = float(p['ID_measured_A'])
    
    # Where load line would be at this current
    vds_load = VDD - id_device * RL
    
    # Error from intersection
    error = abs(vds_device - vds_load)
    
    if error < min_error:
        min_error = error
        operating_point = p.copy()
        operating_point['vds_load'] = vds_load
        operating_point['error'] = error

if operating_point:
    vds_op = float(operating_point['VDS_V'])
    id_op = float(operating_point['ID_measured_A'])
    gm_op = float(operating_point['gm_measured_uS']) * 1e-6  # Convert to S
    gds_op = float(operating_point['gds_measured_uS']) * 1e-6  # Convert to S
    
    ro = 1.0 / gds_op if gds_op > 0 else 1e9
    
    # Parallel impedance
    rl_parallel_ro = (RL * ro) / (RL + ro)
    
    # AC gain
    ac_gain_vv = gm_op * rl_parallel_ro
    ac_gain_db = 20 * np.log10(abs(ac_gain_vv))
    
    print(f"\n✅ OPERATING POINT (Load line intersection):")
    print(f"   VGS = {VGS_TARGET:.2f}V")
    print(f"   VDS = {vds_op:.3f}V (from device curve)")
    print(f"   ID = {id_op*1e6:.3f} µA")
    print(f"\n→ SMALL-SIGNAL PARAMETERS (measured from DC):")
    print(f"   gm = {gm_op*1e6:.3f} µS")
    print(f"   gds = {gds_op*1e9:.3f} nS")
    print(f"   ro = 1/gds = {ro/1e6:.2f} MΩ")
    print(f"\n→ CIRCUIT ANALYSIS:")
    print(f"   RL = {RL/1e3:.1f} kΩ")
    print(f"   RL || ro = {rl_parallel_ro/1e3:.2f} kΩ")
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ AC GAIN: {ac_gain_vv:.1f} V/V")
    print(f"✅ AC GAIN: {ac_gain_db:.2f} dB")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\nWith 0.01V AC input: VOUT_AC = {ac_gain_vv * 0.01:.3f}V peak")
    print(f"Output swing range: VDS ± {ac_gain_vv * 0.01:.3f}V")
    print(f"\nHeadroom:")
    print(f"   VDS,min (ground) = 0V")
    print(f"   VDS,bias = {vds_op:.3f}V")
    print(f"   VDS,max (VDD) = {VDD:.2f}V")
    print(f"   Available for AC swing: {vds_op:.3f}V down, {VDD - vds_op:.3f}V up")
    print(f"   Symmetry: Limited by {min(vds_op, VDD-vds_op):.3f}V")
