#!/usr/bin/env python3
"""
Parse AC .raw file and plot gain
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import re

fname = "output_ac/ac_SchGtKttTtVt.raw"

freq = []
vin = []
vout = []

with open(fname, "r") as f:
    lines = f.readlines()

# Find "Values:" section
in_values = False
i = 0

while i < len(lines):
    line = lines[i].strip()
    
    if line == "Values:":
        in_values = True
        i += 1
        continue
    
    if in_values and line and not line.startswith("Title") and not line.startswith("Date"):
        # Try to parse a data block
        
        # First line should be point index with frequency
        if re.match(r"^\s*\d+\s+", lines[i]):
            # Parse frequency line
            parts = lines[i].strip().split()
            idx = int(parts[0])
            freq_data = parts[1]
            freq_real = float(freq_data.split(",")[0])
            freq.append(freq_real)
            
            # Next line: V(vin)
            i += 1
            vin_data = lines[i].strip()
            if "," in vin_data:
                vin_real, vin_imag = map(float, vin_data.split(","))
                vin.append(complex(vin_real, vin_imag))
            
            # Next line: V(vout)
            i += 1
            vout_data = lines[i].strip()
            if "," in vout_data:
                vout_real, vout_imag = map(float, vout_data.split(","))
                vout.append(complex(vout_real, vout_imag))
    
    i += 1

freq = np.array(freq)
vin = np.array(vin)
vout = np.array(vout)

print(f"Parsed {len(freq)} frequency points")
print(f"Frequency range: {freq[0]:.1e} Hz to {freq[-1]:.1e} Hz")
print(f"Max |V(in)|: {np.max(np.abs(vin)):.3e} V")
print(f"Max |V(out)|: {np.max(np.abs(vout)):.3e} V")

# Calculate gain
gain = np.abs(vout / vin)
gain_db = 20 * np.log10(gain)

print(f"Max gain: {np.max(gain):.1f} V/V = {np.max(gain_db):.2f} dB")
print(f"Gain @ 1MHz: {gain_db[np.argmin(np.abs(freq-1e6))]:.2f} dB")

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Magnitude
ax1.semilogx(freq, gain_db, 'b-', linewidth=2)
ax1.grid(True, which="both", ls="--", alpha=0.5)
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("Gain (dB)")
ax1.set_title("AC Gain Magnitude: 20log10|Vout/Vin|")

# Phase
phase = np.angle(vout, deg=True)
ax2.semilogx(freq, phase, 'r-', linewidth=2)
ax2.grid(True, which="both", ls="--", alpha=0.5)
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Phase (degrees)")
ax2.set_title("AC Phase Response")

plt.tight_layout()
plt.savefig('ac_gain_plot.png', dpi=150, bbox_inches='tight')
print("Plot saved to ac_gain_plot.png")
# Don't show - saves to file instead
# plt.show()

