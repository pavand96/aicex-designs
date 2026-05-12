#!/usr/bin/env python3
"""Monte-Carlo wrapper for LELO_FDA_MILLER.

Uses cicsim's built-in --count flag with the *mm* (mismatch) corner
to run N AC simulations with different random draws on the per-device
sigma parameters.  Reports gain/GBW/PM stats and counts spec violations.

Usage:
    python3 run_mc.py [-n 30] [--corner Kttmm]
"""
import argparse
import glob
import os
import re
import statistics
import subprocess
import sys

SPEC_GAIN = 60.0      # dB
SPEC_GBW  = 120e6     # Hz
SPEC_PM   = 60.0      # deg

def run(cmd):
    print("$ " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-500:])
    return r.returncode

def parse(log, key):
    if not log or not os.path.exists(log):
        return None
    rgx = re.compile(rf"^{re.escape(key)}\s*=\s*([\-\d.eE+]+)",
                     re.IGNORECASE | re.MULTILINE)
    with open(log) as f:
        for line in f:
            m = rgx.search(line)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    return None
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n-runs", type=int, default=30)
    ap.add_argument("--corner", default="Kttmm",
                    help="cicsim corner with mismatch (Kttmm, Kssmm, Kffmm, ...)")
    args = ap.parse_args()

    # Wipe prior AC outputs so we don't mix old runs
    for f in glob.glob("output_ac/ac_SchGt*"):
        os.remove(f)

    # Single cicsim invocation does N seeds via --count
    corner_args = ["Sch", "Gt", args.corner, "Tt", "Vt"]
    cmd = ["cicsim", "run", "--count", str(args.n_runs),
           "--replace", "vos_typ.yaml", "ac"] + corner_args
    run(cmd)

    logs = sorted(glob.glob(f"output_ac/ac_SchGt{args.corner}TtVt*.log"))
    rows = []
    for log in logs:
        rows.append({
            "log": os.path.basename(log),
            "gain": parse(log, "dc_gain_db"),
            "gbw":  parse(log, "fgbw"),
            "pm":   parse(log, "pm"),
        })

    # Print summary
    valid = [r for r in rows if r["gain"] and r["gbw"] and r["pm"]]
    print(f"\nMC corner={args.corner} valid runs: {len(valid)}/{len(rows)}\n")

    def stats(name, vals, spec_low):
        m = statistics.mean(vals)
        s = statistics.stdev(vals) if len(vals) > 1 else 0
        fails = sum(1 for v in vals if v < spec_low)
        print(f"  {name:8s} mean={m:8.3g}  std={s:8.3g}  "
              f"min={min(vals):8.3g}  max={max(vals):8.3g}  "
              f"fail<{spec_low:g}: {fails}/{len(vals)}")

    if valid:
        stats("gain_dB", [r["gain"] for r in valid], SPEC_GAIN)
        stats("GBW(Hz)", [r["gbw"]  for r in valid], SPEC_GBW)
        stats("PM(deg)", [r["pm"]   for r in valid], SPEC_PM)

    # Per-run CSV
    out = "mc_summary.csv"
    with open(out, "w") as f:
        f.write("log,gain_db,gbw,pm\n")
        for r in rows:
            f.write(f"{r['log']},{r['gain']},{r['gbw']},{r['pm']}\n")
    print(f"\nWrote {out}")

if __name__ == "__main__":
    main()
