#!/usr/bin/env python3
"""
Load Line Analysis - Find operating point and gain for different RL values
For a given VGS and different RL, find where the load line intersects the I-V curve
"""

import csv
import numpy as np

# Parameters
VDD = 1.8
VGS_TARGET = 0.60
W_UM = 60.0
L_UM = 0.8

# Candidate load resistors (Ohms)
RL_candidates = [5e3, 10e3, 15e3, 20e3, 50e3, 100e3]

print(f"\n{'='*120}")
print(f"LOAD LINE ANALYSIS - Common Source Amplifier")
print(f"VDD = {VDD}V, VGS = {VGS_TARGET}V, Device: W={W_UM}µm, L={L_UM}µm")
print(f"{'='*120}\n")

# Read CSV
csv_points = []
with open('characterize_2d_all_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if float(row['W_um']) == W_UM and float(row['L_um']) == L_UM and abs(float(row['VGS_V']) - VGS_TARGET) < 0.01:
            csv_points.append({
                'vds': float(row['VDS_V']),
                'id': float(row['ID_measured_A']),
                'gm': float(row['gm_measured_uS']) * 1e-6,  # Convert to S
                'gds': float(row['gds_measured_uS']) * 1e-6,  # Convert to S
                'vov': float(row['Vov_V'])
            })

# Sort by VDS
csv_points.sort(key=lambda x: x['vds'])

print(f"Found {len(csv_points)} points at VGS={VGS_TARGET}V in CSV\n")

# For each RL candidate, find intersection
results = []

for RL in RL_candidates:
    # Load line: VDS_load = VDD - ID * RL
    # Find the point on the device curve closest to this load line
    
    min_error = float('inf')
    best_point = None
    best_vds_load = None
    
    for point in csv_points:
        # Calculate where load line would intersect at this ID
        vds_load = VDD - point['id'] * RL
        
        # Error: how far is the device curve point from the load line?
        error = abs(point['vds'] - vds_load)
        
        if error < min_error:
            min_error = error
            best_point = point.copy()
            best_vds_load = vds_load
    
    if best_point is None:
        continue
    
    # Operating point found
    vds_actual = best_point['vds']
    id_actual = best_point['id']
    gm_actual = best_point['gm']
    gds_actual = best_point['gds']
    
    # Calculate gain
    ro = 1 / gds_actual if gds_actual > 0 else 1e9
    rl_parallel_ro = (RL * ro) / (RL + ro) if ro > 0 else RL
    
    gain_vv = gm_actual * rl_parallel_ro
    gain_db = 20 * np.log10(abs(gain_vv)) if gain_vv > 0 else 0
    
    # Intrinsic gain (no RL effect)
    intrinsic_gain = gm_actual / gds_actual if gds_actual > 0 else 0
    
    results.append({
        'RL': RL,
        'VDS_actual': vds_actual,
        'VDS_load': best_vds_load,
        'ID_actual': id_actual,
        'gm': gm_actual,
        'gds': gds_actual,
        'ro': ro,
        'RL_parallel_ro': rl_parallel_ro,
        'gain_vv': gain_vv,
        'gain_db': gain_db,
        'intrinsic_gain': intrinsic_gain,
        'headroom': VDD - vds_actual,
        'error': min_error
    })

# Sort by gain to find best
results.sort(key=lambda x: x['gain_vv'], reverse=True)

print(f"{'RL (kΩ)':<10} {'VDS (V)':<10} {'ID (µA)':<10} {'gm (µS)':<12} {'gds (nS)':<12} {'ro (MΩ)':<12} {'Av (V/V)':<15} {'Av (dB)':<10} {'Headroom':<12} {'Error':<12}")
print("-" * 140)

for i, r in enumerate(results):
    rl_kohm = r['RL'] / 1e3
    id_ua = r['ID_actual'] * 1e6
    gm_us = r['gm'] * 1e6
    gds_ns = r['gds'] * 1e9
    ro_mohm = r['ro'] / 1e6
    headroom = r['headroom']
    error = r['error']
    
    marker = " ← MAX GAIN" if i == 0 else ""
    
    print(f"{rl_kohm:<10.2f} {r['VDS_actual']:<10.3f} {id_ua:<10.3f} {gm_us:<12.3f} {gds_ns:<12.3f} {ro_mohm:<12.3f} {r['gain_vv']:<15.0f} {r['gain_db']:<10.2f} {headroom:<12.3f} {error:<12.3e}{marker}")

print("\n" + "="*140)
print(f"\n✅ RECOMMENDATION: RL = {results[0]['RL']/1e3:.1f} kΩ")
print(f"   Operating point: VDS = {results[0]['VDS_actual']:.3f}V, ID = {results[0]['ID_actual']*1e6:.3f}µA")
print(f"   Gain: {results[0]['gain_vv']:.0f} V/V ({results[0]['gain_db']:.2f} dB)")
print(f"   Headroom: {results[0]['headroom']:.3f}V (output swing margin)")
print(f"   ro = {results[0]['ro']/1e6:.2f} MΩ, gm×ro = {results[0]['intrinsic_gain']:.0f} V/V")
print(f"\n")
