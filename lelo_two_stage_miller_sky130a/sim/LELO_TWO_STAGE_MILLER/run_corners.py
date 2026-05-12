#!/usr/bin/env python3
"""
Per-corner orchestrator for LELO_TWO_STAGE_MILLER.
For each corner combination:
  1. cicsim run dc.spi   -> parse Vos from log
  2. cicsim run ac.spi   --replace VOS={vos}  -> AC results
  3. cicsim run noise.spi --replace VOS={vos} -> noise results

Aggregates into a single corner_summary.csv.

Usage:
  python3 run_corners.py          # all corners + MC
  python3 run_corners.py --tt     # typical only
"""
import argparse, glob, os, re, subprocess, sys, tempfile, yaml

CORNERS = {
    "typical": ["Sch", "Gt", "Ktt",                "Tt",       "Vt"],
    "ss":      ["Sch", "Gt", "Kss",                "Th,Tl",    "Vl"],
    "ff":      ["Sch", "Gt", "Kff",                "Th,Tl",    "Vh"],
    "etc":     ["Sch", "Gt", "Kss,Kff,Ksf,Kfs",    "Th,Tl",    "Vl,Vh"],
}
MC_NAME = "mc"
MC_KEY  = ["Sch", "Gt", "Kttmm", "Tt", "Vt"]
MC_COUNT = 30

VOS_RE = re.compile(r"vos\s*=\s*([\d\.eE+\-]+)")

def parse_vos(log_path):
    with open(log_path) as f:
        for line in f:
            m = VOS_RE.search(line)
            if m:
                return float(m.group(1))
    return None

def cicsim_run(name, tb, args, replace_yaml=None):
    cmd = ["cicsim", "run", "--name", name, tb] + args
    if replace_yaml:
        cmd += ["--replace", replace_yaml]
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode

def write_replace(vos):
    fd, path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    with open(path, "w") as f:
        yaml.safe_dump({"VOS": float(vos)}, f)
    return path

def get_log(name, tb):
    """Find latest log for this run name/tb. cicsim stores under output_<tb>/."""
    pattern = f"output_{tb}/{tb}_*.log"
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None

def find_logs(tb):
    return sorted(glob.glob(f"output_{tb}/{tb}_*.log"))

def parse_metric(log_path, key):
    """Parse a 'key = value' line from log."""
    rgx = re.compile(rf"^{re.escape(key)}\s*=\s*([\-\d\.eE+]+)", re.IGNORECASE)
    val = None
    with open(log_path) as f:
        for line in f:
            m = rgx.search(line)
            if m:
                val = m.group(1)
    return val

def run_corner(corner_name, args):
    print(f"\n=== Corner: {corner_name}  args={args} ===")
    # 1. DC
    cicsim_run(f"Sch_{corner_name}", "dc", args)
    # parse vos from each generated log
    dc_logs = find_logs("dc")
    # find logs whose mtime > 5s ago belong to THIS run; simpler: keep them all
    results = []
    for dc_log in dc_logs:
        base = os.path.basename(dc_log)[:-4]   # strip .log
        # Only operate on logs whose name encodes the corner combo we just ran
        vos = parse_vos(dc_log)
        if vos is None:
            print(f"  ! {base}: no Vos extracted, skipping")
            continue
        print(f"  {base}: Vos = {vos:.6f} V")
        # corresponding ac/noise are run with same corner combo (extract code from name)
        # base format: dc_<combo>
        combo = base.replace("dc_", "")
        # rewrite the corner args from combo - skip; we'll just run ac/noise with same args
    return dc_logs

def run_one(combo_args, name_suffix, vos):
    """Run ac+noise for a single corner combo using --replace VOS=vos."""
    rpl = write_replace(vos)
    cicsim_run(f"Sch_{name_suffix}", "ac", combo_args, replace_yaml=rpl)
    cicsim_run(f"Sch_{name_suffix}", "noise", combo_args, replace_yaml=rpl)
    os.unlink(rpl)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tt", action="store_true", help="typical only")
    ap.add_argument("--mc", action="store_true", help="add MC sweep")
    args = ap.parse_args()

    runs = [("typical", CORNERS["typical"])]
    if not args.tt:
        runs.append(("etc", CORNERS["etc"]))

    for name, cargs in runs:
        # Step 1: dc per corner combo
        cicsim_run(f"Sch_{name}", "dc", cargs)
        # parse all dc logs from this run
        for dc_log in find_logs("dc"):
            base = os.path.basename(dc_log)[:-4]
            combo = base[len("dc_"):]
            # Re-derive corner args list from the combo string would be complex;
            # simpler: cicsim runs all combos in one invocation. Use the same cargs
            # but we'd run ac/noise per combo individually. The trick: cicsim --replace
            # applies to ALL combos in the run, but vos varies per combo. So we run
            # ac/noise separately per combo with single-combo args.
            # Decode combo: e.g. "SchGtKssThVl" -> [Sch, Gt, Kss, Th, Vl]
            tokens = re.findall(r"[A-Z][a-z]*", combo)
            vos = parse_vos(dc_log)
            if vos is None:
                continue
            print(f"\n  combo {combo}: Vos = {vos:.4f} -> running ac+noise")
            run_one(tokens, combo, vos)

    if args.mc:
        cicsim_run(f"Sch_{MC_NAME}", "dc", MC_KEY)
        # Each MC iteration creates its own log. Glob all latest dc mc logs.
        for dc_log in find_logs("dc"):
            base = os.path.basename(dc_log)[:-4]
            if "mm" not in base.lower() and "mc" not in base.lower():
                continue
            combo = base[len("dc_"):]
            tokens = re.findall(r"[A-Z][a-z]*", combo)
            vos = parse_vos(dc_log)
            if vos is None:
                continue
            print(f"  MC combo {combo}: Vos = {vos:.4f}")
            run_one(tokens, combo, vos)

if __name__ == "__main__":
    main()
