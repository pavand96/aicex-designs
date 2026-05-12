#!/usr/bin/env python3
"""
plot_ac.py  —  Plot gain (dB) and phase (deg) vs frequency for LELO_5TOTA AC analysis.

Usage:
    python3 plot_ac.py [raw_file]

If no raw_file is given, the most recently modified ac_*.raw in output_ac/ is used.
"""

import sys
import os
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")   # non-interactive — works without a display
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── 1. Locate raw file ──────────────────────────────────────────────────────
if len(sys.argv) > 1:
    raw_path = sys.argv[1]
else:
    pattern = os.path.join(os.path.dirname(__file__), "output_ac", "ac_*.raw")
    candidates = sorted(glob.glob(pattern), key=os.path.getmtime)
    if not candidates:
        sys.exit("ERROR: no ac_*.raw found in output_ac/. Run: make typical TB=ac")
    raw_path = candidates[-1]

print(f"Loading: {raw_path}")

# ── 2. Parse ngspice ASCII raw file ─────────────────────────────────────────
def parse_raw(path):
    """
    Parse ngspice ASCII complex raw file.
    Returns: (var_names, data) where data[i] is a 1-D complex array for variable i.
    """
    with open(path) as f:
        lines = f.readlines()

    # --- header ---
    var_names = []
    n_vars = 0
    n_points = 0
    in_vars = False
    data_start = 0

    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("No. Variables:"):
            n_vars = int(s.split(":")[-1].strip())
        elif s.startswith("No. Points:"):
            n_points = int(s.split(":")[-1].strip())
        elif s == "Variables:":
            in_vars = True
        elif in_vars:
            parts = s.split()
            if len(parts) >= 2 and parts[0].isdigit():
                var_names.append(parts[1])
            if len(var_names) == n_vars:
                in_vars = False
        elif s == "Values:":
            data_start = i + 1
            break

    # --- values ---
    # Each time point: one "idx  real,imag" line for var 0,
    #                  then (n_vars-1) lines of "real,imag"
    data = np.zeros((n_vars, n_points), dtype=complex)
    point = 0
    var   = 0

    for line in lines[data_start:]:
        s = line.strip()
        if not s:
            continue
        # Line for variable 0 starts with the point index: "0   real,imag"
        if var == 0:
            parts = s.split()
            val_str = parts[-1]          # last token = real,imag
        else:
            val_str = s

        re_s, im_s = val_str.split(",")
        data[var, point] = complex(float(re_s), float(im_s))

        var += 1
        if var == n_vars:
            var = 0
            point += 1
            if point == n_points:
                break

    return var_names, data


var_names, data = parse_raw(raw_path)

# ── 3. Extract vectors ───────────────────────────────────────────────────────
freq_idx     = var_names.index("frequency")
gain_db_idx  = var_names.index("gain_mag_db")
phase_idx    = var_names.index("gain_ph_deg")

freq     = data[freq_idx].real          # Hz
gain_db  = data[gain_db_idx].real       # dB
phase    = data[phase_idx].real         # degrees

# ── 4. Key metrics ───────────────────────────────────────────────────────────
dc_gain_db  = gain_db[0]
f3db_target = dc_gain_db - 3

# f3dB: first frequency where gain drops to dc_gain_db - 3
cross3 = np.where(np.diff(np.sign(gain_db - f3db_target)))[0]
f3db  = float(np.interp(0, gain_db[cross3[0]:cross3[0]+2][::-1] - f3db_target,
                           freq[cross3[0]:cross3[0]+2][::-1]))  if len(cross3) else np.nan

# Unity-gain crossover
crossUGF = np.where(np.diff(np.sign(gain_db)))[0]
fgbw  = float(np.interp(0, gain_db[crossUGF[0]:crossUGF[0]+2][::-1],
                           freq[crossUGF[0]:crossUGF[0]+2][::-1])) if len(crossUGF) else np.nan
phase_at_ugf = float(np.interp(fgbw, freq, phase)) if not np.isnan(fgbw) else np.nan
pm    = phase_at_ugf + 180 if not np.isnan(phase_at_ugf) else np.nan

print(f"  DC gain   : {dc_gain_db:.2f} dB  ({10**(dc_gain_db/20):.0f} V/V)")
print(f"  f-3dB     : {f3db/1e3:.1f} kHz")
print(f"  GBW       : {fgbw/1e6:.2f} MHz")
print(f"  Phase@GBW : {phase_at_ugf:.1f}°")
print(f"  PM        : {pm:.1f}°")

# ── 5. Plot ──────────────────────────────────────────────────────────────────
fig, (ax_gain, ax_phase) = plt.subplots(
    2, 1, figsize=(9, 6), sharex=True,
    gridspec_kw={"height_ratios": [3, 2], "hspace": 0.08}
)
fig.suptitle("LELO_5TOTA — AC Bode Plot (sky130, TT)", fontsize=12, fontweight="bold")

# ── Gain ──
ax_gain.semilogx(freq, gain_db, color="#1f77b4", linewidth=1.8, label=r"$|A_v(j\omega)|$")
ax_gain.axhline(0,            color="gray",   linewidth=0.8, linestyle="--")
ax_gain.axhline(f3db_target,  color="#ff7f0e",linewidth=0.8, linestyle=":")
ax_gain.axvline(f3db,  color="#ff7f0e", linewidth=0.8, linestyle=":", label=f"$f_{{3dB}}$ = {f3db/1e3:.0f} kHz")
ax_gain.axvline(fgbw,  color="#2ca02c", linewidth=0.8, linestyle="--", label=f"GBW = {fgbw/1e6:.1f} MHz")
ax_gain.scatter([1], [dc_gain_db], color="#1f77b4", s=30, zorder=5)

# annotation: DC gain
ax_gain.annotate(f"$A_0$ = {dc_gain_db:.1f} dB",
                 xy=(1, dc_gain_db), xytext=(3, dc_gain_db - 5),
                 fontsize=9, color="#1f77b4",
                 arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=0.8))

ax_gain.set_ylabel("Gain (dB)", fontsize=10)
ax_gain.set_ylim(bottom=min(gain_db.min() - 5, -10))
ax_gain.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.7)
ax_gain.legend(fontsize=9, loc="lower left")
ax_gain.yaxis.set_minor_locator(ticker.AutoMinorLocator())

# ── Phase ──
ax_phase.semilogx(freq, phase, color="#d62728", linewidth=1.8, label=r"$\angle A_v(j\omega)$")
ax_phase.axhline(-180, color="gray",   linewidth=0.8, linestyle="--")
ax_phase.axvline(fgbw,  color="#2ca02c", linewidth=0.8, linestyle="--")

# PM annotation
if not np.isnan(pm):
    ax_phase.annotate("",
                      xy=(fgbw, -180), xytext=(fgbw, phase_at_ugf),
                      arrowprops=dict(arrowstyle="<->", color="purple", lw=1.2))
    ax_phase.text(fgbw * 1.15, (-180 + phase_at_ugf) / 2,
                  f"PM = {pm:.1f}°", color="purple", fontsize=9, va="center")

ax_phase.set_ylabel("Phase (°)", fontsize=10)
ax_phase.set_xlabel("Frequency (Hz)", fontsize=10)
ax_phase.set_ylim(-200, 10)
ax_phase.set_yticks([-180, -135, -90, -45, 0])
ax_phase.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.7)
ax_phase.legend(fontsize=9, loc="lower left")

# ── x-axis formatting ──
ax_phase.xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: (f"{x/1e6:.0f}M" if x >= 1e6 else
                  f"{x/1e3:.0f}k" if x >= 1e3 else f"{x:.0f}")
))
ax_phase.set_xlim(freq[0], freq[-1])

plt.tight_layout()
out_png = os.path.join(os.path.dirname(raw_path), "bode_plot.png")
fig.savefig(out_png, dpi=150, bbox_inches="tight")
print(f"\nSaved: {out_png}")
plt.show()
