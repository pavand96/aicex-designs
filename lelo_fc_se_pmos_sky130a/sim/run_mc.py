#!/usr/bin/env python3
"""
Monte Carlo across sky130 mismatch+process corners for fc_se_pmos.

For each corner (tt_mm, ff_mm, ss_mm, fs_mm, sf_mm), runs N samples of
the AC testbench (which also does an OP) with a different seed each run.
Aggregates mean / sigma / min / max of A0, GBW, PM, IDD, VOUTP offset.

Usage:
    python run_mc.py             # default 50 samples x 5 corners (parallel)
    python run_mc.py 100         # 100 samples per corner
    python run_mc.py 100 tt_mm   # only tt_mm corner

Output:
    run/mc/<corner>/sample_<NNN>.log   raw ngspice logs
    run/mc/<corner>/results.csv        per-sample parsed metrics
    stdout: summary table
"""
import os, re, sys, csv, pathlib, subprocess, statistics
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
PDK  = os.environ.get("PDK_ROOT", "/opt/pdk/share/pdk")
LIB  = f"{PDK}/sky130A/libs.tech/ngspice/sky130.lib.spice"
MM_CORNERS = ["tt_mm", "ff_mm", "ss_mm", "fs_mm", "sf_mm"]
NJOBS = int(os.environ.get("NJOBS", min(4, max(1, (os.cpu_count() or 4) // 2))))


def build_wrapper(corner: str, seed: int) -> pathlib.Path:
    work = HERE / "run" / "mc" / corner
    work.mkdir(parents=True, exist_ok=True)
    wrapper = work / f"sample_{seed:04d}.spi"
    with open(HERE / "tb_ac.spi") as f:
        body = f.read()
    body = body.replace(".include dut.spi", f'.include "{HERE}/dut.spi"')
    # Force single-thread ngspice (we parallelize at the process level instead).
    seed_set = (
        ".control\n"
        f"set rndseed={seed}\n"
        "set num_threads=1\n"
        ".endc\n"
    )
    with open(wrapper, "w") as f:
        f.write(f"* MC corner={corner} seed={seed}\n")
        f.write(f'.lib "{LIB}" {corner}\n')
        f.write(seed_set)
        f.write(body)
    return wrapper


_RE_NUM = r"([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"

def parse(text: str) -> dict:
    """Pull metrics from ngspice stdout."""
    def grab(label):
        m = re.search(rf"{label}\s*=\s*{_RE_NUM}", text)
        return float(m.group(1)) if m else float("nan")

    def grab_print(name):
        # `print` outputs `name = value` (case preserved)
        m = re.search(rf"^\s*{re.escape(name)}\s*=\s*{_RE_NUM}\s*$",
                      text, flags=re.MULTILINE)
        return float(m.group(1)) if m else float("nan")

    return {
        "A0_dB":   grab("dc_gain_db"),
        "GBW_Hz":  grab("fgbw"),
        "PM_deg":  grab("pm"),
        "IDD_uA":  grab_print("-i(vdd)") * 1e6,   # -i(vdd) is current out of VDD source
        "VOUTP_V": grab_print("v(voutp)"),
        "VBP_V":   grab_print("v(xdut.vbp)"),
        "VBIAS1":  grab_print("v(xdut.vbias1)"),
        "VBIAS2":  grab_print("v(xdut.vbias2)"),
    }


def run_one(args) -> tuple:
    corner, seed = args
    w = build_wrapper(corner, seed)
    try:
        r = subprocess.run(
            ["ngspice", "-b", str(w)],
            capture_output=True, text=True, cwd=w.parent, timeout=600,
        )
        out = r.stdout
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
    (w.parent / f"sample_{seed:04d}.log").write_text(out)
    return corner, seed, parse(out)


def summarize(vals, label, unit, fmt="{:>10.3f}"):
    vals = [v for v in vals if v == v]  # drop NaNs
    if not vals:
        return f"{label:>10s}  no valid samples"
    n = len(vals)
    mean = statistics.fmean(vals)
    sd   = statistics.pstdev(vals) if n > 1 else 0.0
    lo   = min(vals); hi = max(vals)
    return (f"  {label:<8s} [{unit:>4s}]   mean={fmt.format(mean)}   "
            f"sd={fmt.format(sd)}   min={fmt.format(lo)}   max={fmt.format(hi)}   "
            f"(n={n})")


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    corners = [sys.argv[2]] if len(sys.argv) > 2 else MM_CORNERS

    print(f"\nMC: N={N} samples/corner, corners={corners}, jobs={NJOBS}\n")

    # build job list
    jobs = [(c, s) for c in corners for s in range(1, N + 1)]
    results = {c: [] for c in corners}

    with ProcessPoolExecutor(max_workers=NJOBS) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}
        done = 0
        total = len(jobs)
        for fut in as_completed(futs):
            corner, seed, d = fut.result()
            results[corner].append(d)
            done += 1
            if done % 10 == 0 or done == total:
                print(f"  [{done:>4d}/{total}] done")

    # write CSV + print summary
    print("\n========================== MC SUMMARY ==========================")
    for c in corners:
        rows = results[c]
        csv_path = HERE / "run" / "mc" / c / "results.csv"
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

        print(f"\n--- {c}  (N={len(rows)})  csv: {csv_path.relative_to(HERE)}")
        for key, unit, fmt in [
            ("A0_dB",   "dB",  "{:>10.2f}"),
            ("GBW_Hz",  "Hz",  "{:>10.3e}"),
            ("PM_deg",  "deg", "{:>10.2f}"),
            ("IDD_uA",  "uA",  "{:>10.2f}"),
            ("VOUTP_V", "V",   "{:>10.4f}"),
            ("VBP_V",   "V",   "{:>10.4f}"),
            ("VBIAS1",  "V",   "{:>10.4f}"),
            ("VBIAS2",  "V",   "{:>10.4f}"),
        ]:
            print(summarize([r[key] for r in rows], key, unit, fmt))


if __name__ == "__main__":
    main()
