#!/usr/bin/env python3
"""
Corner sweep for LELO_FDA_MILLER.
Runs op + ac + tran for each corner; collects key metrics into CSV.
"""
import argparse, glob, os, re, subprocess, csv

# Corner combos: (label, args)
CORNERS = [
    ("typ",     ["Sch", "Gt", "Ktt", "Tt", "Vt"]),
    ("ss_tl_vl",["Sch", "Gt", "Kss", "Tl", "Vl"]),
    ("ss_th_vl",["Sch", "Gt", "Kss", "Th", "Vl"]),
    ("ss_th_vh",["Sch", "Gt", "Kss", "Th", "Vh"]),
    ("ff_tl_vl",["Sch", "Gt", "Kff", "Tl", "Vl"]),
    ("ff_tl_vh",["Sch", "Gt", "Kff", "Tl", "Vh"]),
    ("ff_th_vh",["Sch", "Gt", "Kff", "Th", "Vh"]),
    ("sf_tt_vt",["Sch", "Gt", "Ksf", "Tt", "Vt"]),
    ("fs_tt_vt",["Sch", "Gt", "Kfs", "Tt", "Vt"]),
]

VOS_REPLACE = "vos_typ.yaml"   # use Vos=0.9 (vcm); offset assumed 0 for sweep

def cicsim_run(name, tb, args, replace=None):
    cmd = ["cicsim", "run", "--name", name]
    if replace:
        cmd += ["--replace", replace]
    cmd += [tb] + args
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-500:])
    return r.stdout

def latest_log(tb):
    files = sorted(glob.glob(f"output_{tb}/{tb}_*.log"), key=os.path.getmtime)
    return files[-1] if files else None

def parse(log, key):
    if not log or not os.path.exists(log):
        return None
    rgx = re.compile(rf"^{re.escape(key)}\s*=\s*([\-\d\.eE+]+)", re.IGNORECASE | re.MULTILINE)
    val = None
    with open(log) as f:
        for line in f:
            m = rgx.search(line)
            if m:
                val = m.group(1)
    return val

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tt", action="store_true")
    args = ap.parse_args()

    corners = [CORNERS[0]] if args.tt else CORNERS

    rows = []
    for label, cargs in corners:
        print(f"\n=== {label} ===")
        # OP
        cicsim_run(f"Sch_{label}", "op", cargs)
        op_log = latest_log("op")
        # AC
        cicsim_run(f"Sch_{label}", "ac", cargs, replace=VOS_REPLACE)
        ac_log = latest_log("ac")
        # TRAN
        cicsim_run(f"Sch_{label}", "tran", cargs)
        tr_log = latest_log("tran")

        row = {
            "corner": label,
            "vocm":      parse(op_log, "v(voutp)"),
            "id_m1":     parse(op_log, "id_m1"),
            "id_m5p":    parse(op_log, "id_m5p"),
            "id_m6p":    parse(op_log, "id_m6p"),
            "gain_db":   parse(ac_log, "dc_gain_db"),
            "gbw":       parse(ac_log, "fgbw"),
            "pm":        parse(ac_log, "pm"),
            "vod_step":  parse(tr_log, "vod_pos"),
            "sr":        parse(tr_log, "sr_rise"),
            "sr_fall":   parse(tr_log, "sr_fall"),
        }
        print("  ", row)
        rows.append(row)

    # Write CSV
    fields = ["corner", "vocm", "id_m1", "id_m5p", "id_m6p",
              "gain_db", "gbw", "pm", "vod_step", "sr", "sr_fall"]
    with open("corner_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("\nWrote corner_summary.csv")

if __name__ == "__main__":
    main()
