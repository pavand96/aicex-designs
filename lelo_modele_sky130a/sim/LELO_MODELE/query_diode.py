#!/usr/bin/env python3
"""
Diode-connected MOSFET sizing query.

For a diode-connected NMOS (VGS = VDS), finds all W/L combinations
where a given drain current ID flows at a given VGS target.

Usage:
  python3 query_diode.py                          # defaults: ID=20uA, VGS=0.6V, corner=tt
  python3 query_diode.py --id 20 --vgs 0.6        # explicit (ID in µA, VGS in V)
  python3 query_diode.py --id 20 --vgs 0.6 --corner ss
  python3 query_diode.py --id 20 --vgs 0.6 --tol 0.02      # VGS tolerance in V (default 0.01)
  python3 query_diode.py --id 20 --vgs 0.6 --id-tol 2.0    # max |ID error| in µA (default 2.0)
"""

import argparse, os, sys
import pandas as pd
import numpy as np

# ── argument parsing ──────────────────────────────────────────────────────────
p = argparse.ArgumentParser()
p.add_argument('--id',     type=float, default=20.0,  help='Target drain current in µA')
p.add_argument('--vgs',    type=float, default=0.6,   help='Target VGS in V')
p.add_argument('--tol',    type=float, default=0.01,  help='VGS lookup tolerance in V (default 0.01)')
p.add_argument('--corner', type=str,   default='tt',  help='Corner: tt, ss, ff')
p.add_argument('--csv',    type=str,   default=None,  help='Override CSV path')
p.add_argument('--id-tol', type=float, default=2.0,   help='Max |ID error| in µA to include in results (default 2.0)')
args = p.parse_args()

TARGET_ID_A  = args.id * 1e-6          # convert µA → A
TARGET_VGS   = args.vgs
TOL_VGS      = args.tol
ID_TOL_UA    = args.id_tol
CORNER       = args.corner.lower()

# ── locate CSV ────────────────────────────────────────────────────────────────
CSV_DIR = os.path.join(os.path.dirname(__file__), 'characterize_2d_csvs')
if args.csv:
    csv_path = args.csv
else:
    # Prefer the w1inc (1µm step) CSV, fall back to original
    w1inc = os.path.join(CSV_DIR, f'characterize_2d_{CORNER}_w1inc.csv')
    orig  = os.path.join(CSV_DIR, f'characterize_2d_{CORNER}.csv')
    if os.path.exists(w1inc):
        csv_path = w1inc
    elif os.path.exists(orig):
        csv_path = orig
        print(f"[info] w1inc CSV not found, using {os.path.basename(orig)}")
    else:
        sys.exit(f"[error] No CSV found for corner={CORNER} in {CSV_DIR}")

print(f"\n{'='*70}")
print(f"  Diode-connected NMOS query")
print(f"  Target ID  = {args.id:.1f} µA")
print(f"  Target VGS = {TARGET_VGS:.3f} V  (±{TOL_VGS:.3f} V)")
print(f"  Corner     = {CORNER}")
print(f"  ID tol     = ±{ID_TOL_UA:.1f} µA")
print(f"  CSV        = {os.path.basename(csv_path)}")
print(f"{'='*70}\n")

# ── load & filter ─────────────────────────────────────────────────────────────
print("Loading CSV...")
df = pd.read_csv(csv_path)
print(f"  {len(df):,} rows loaded\n")

# Diode-connected: VGS == VDS. Filter rows near target VGS.
# Use abs tolerance on both VGS and VDS.
mask = (
    ((df['VGS_V'] - TARGET_VGS).abs() <= TOL_VGS / 2 + 1e-6) &
    ((df['VDS_V'] - TARGET_VGS).abs() <= TOL_VGS / 2 + 1e-6)
)

if CORNER != 'all':
    mask = mask & (df['Corner'] == CORNER)

filtered = df[mask].copy()

if filtered.empty:
    sys.exit(f"[error] No rows found near VGS=VDS={TARGET_VGS}V. "
             f"Available VGS range: {df['VGS_V'].min():.2f}–{df['VGS_V'].max():.2f} V")

# For each W/L, take the row whose VGS is closest to target
filtered['vgs_err'] = (filtered['VGS_V'] - TARGET_VGS).abs()
best = (filtered
    .sort_values('vgs_err')
    .groupby(['W_um', 'L_um'], as_index=False)
    .first()
)

best = best.sort_values(['L_um', 'W_um'])

# Filter to rows within the absolute ID tolerance
best = best[((best['ID_measured_A'] * 1e6) - args.id).abs() <= ID_TOL_UA]

if best.empty:
    sys.exit(f"[info] No W/L combination found with |ID error| ≤ {ID_TOL_UA:.1f} µA at VGS={TARGET_VGS}V. "
             f"Try widening --id-tol or adjusting --vgs.")

print(f"  {len(best)} W/L combos found within ±{ID_TOL_UA:.1f} µA\n")

# ── interpolate exact W for each L ───────────────────────────────────────────
print(f"{'W (µm)':>8}  {'L (µm)':>6}  {'VGS (V)':>8}  {'VDS (V)':>8}  "
      f"{'ID (µA)':>10}  {'ID error':>10}  {'gm/ID':>8}  {'rds (kΩ)':>10}")
print("-"*80)

results = []
for _, row in best.iterrows():
    id_ua  = row['ID_measured_A'] * 1e6
    err_ua = id_ua - args.id
    gm_id  = row['gm_ID_S_A']
    rds_k  = row['rds_measured_Ohm'] / 1e3
    results.append({
        'W_um': row['W_um'], 'L_um': row['L_um'],
        'VGS_V': row['VGS_V'], 'VDS_V': row['VDS_V'],
        'ID_uA': id_ua, 'ID_error_uA': err_ua,
        'gm_ID': gm_id, 'rds_kOhm': rds_k
    })
    flag = ' ◄' if abs(err_ua) <= 1.0 else ''   # within 1µA
    print(f"{row['W_um']:>8.1f}  {row['L_um']:>6.2f}  {row['VGS_V']:>8.4f}  "
          f"{row['VDS_V']:>8.4f}  {id_ua:>10.2f}  {err_ua:>+10.2f}  "
          f"{gm_id:>8.2f}  {rds_k:>10.1f}{flag}")

# ── interpolate exact W for each L ───────────────────────────────────────────
print(f"\n{'─'*70}")
print(f"  Interpolated W for ID = {args.id:.1f} µA at VGS = {TARGET_VGS:.3f} V")
print(f"{'─'*70}")

res_df = pd.DataFrame(results)
for l_val, grp in res_df.groupby('L_um'):
    grp = grp.sort_values('W_um')
    ids = grp['ID_uA'].values
    ws  = grp['W_um'].values
    # find crossing point (where ID crosses target)
    crossings = np.where(np.diff(np.sign(ids - args.id)))[0]
    if len(crossings) == 0:
        closest_idx = np.argmin(np.abs(ids - args.id))
        print(f"  L={l_val:.2f} µm : no exact crossing — closest W={ws[closest_idx]:.1f} µm "
              f"(ID={ids[closest_idx]:.2f} µA)")
    else:
        for ci in crossings:
            w0, w1 = ws[ci], ws[ci+1]
            id0, id1 = ids[ci], ids[ci+1]
            w_interp = w0 + (args.id - id0) * (w1 - w0) / (id1 - id0)
            print(f"  L={l_val:.2f} µm : W ≈ {w_interp:.2f} µm  "
                  f"(between W={w0:.0f} µm [{id0:.2f} µA] and W={w1:.0f} µm [{id1:.2f} µA])")

print(f"\n  ◄ = within 1 µA of target ID\n")
