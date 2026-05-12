#!/usr/bin/env python3
"""
Final 2D characterization script
- Updates xschem schematic source file for M2
- Runs Make/CICSIM flow
- Uses DC sweep results to find valid bias points
- Uses AC sims at each bias point to extract gm, gds, and caps

Important:
- This edits the xschem schematic source file (.sch text from xschem), not a hand-edited .spice file
- Source and bulk are tied together in this bench, so Cgs/Cgb/Csb cannot all be separated independently
"""

import csv
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

# xschem schematic source file to edit
SCH_PATH = Path(
    "~/pro/aicex/ip/lelo_modele_sky130a/design/LELO_MODELE_SKY130A/LELO_MODELE.sch"
).expanduser()

SCH_BACKUP_PATH = SCH_PATH.with_suffix(SCH_PATH.suffix + ".orig")

# transistor instance inside the schematic
TARGET_INSTANCE = "M2"

# Make/CICSIM flow
TB_DC = "op"       # existing DC sweep testbench
TB_NETLIST_DIR = Path("output_op")

CORNER_MAP = {
    "tt": "typical",
    "ss": "slow",
    "ff": "fast",
    "sf": "etc",
    "fs": "etc",
    "typical": "typical",
    "slow": "slow",
    "fast": "fast",
}

# names used in DC raw extraction
DC_GATE_NODE = "VIN"
DC_DRAIN_NODE = "VOUT"
DC_DRAIN_CURRENT_SOURCE = "VDS"

# names used by AC wrapper
# Drain source is known from your earlier script: i(VDS)
AC_DRAIN_SOURCE = "VDS"

# You may need to change this depending on your testbench.
# Common possibilities: VIN, VGS
AC_GATE_SOURCE = "VIN"

# AC characterization frequency
# Low enough that gm/gds appear in real current; caps in imag current
AC_FREQ_HZ = 1e6

# CSV output
CSV_PREFIX = "characterize_2d"

# Saturation filter only for selecting useful points from DC sweep
DEFAULT_VTH = 0.410


# =============================================================================
# HELPERS
# =============================================================================

def run_cmd(cmd, timeout=None, text=True, capture_output=True, check=False):
    return subprocess.run(
        cmd,
        timeout=timeout,
        text=text,
        capture_output=capture_output,
        check=check
    )


def ensure_backup():
    if not SCH_PATH.exists():
        raise FileNotFoundError(f"Schematic file not found: {SCH_PATH}")
    if not SCH_BACKUP_PATH.exists():
        shutil.copy2(SCH_PATH, SCH_BACKUP_PATH)


def restore_schematic():
    if SCH_BACKUP_PATH.exists():
        shutil.copy2(SCH_BACKUP_PATH, SCH_PATH)


def update_m2_in_schematic(w_um: float, l_um: float) -> bool:
    """
    Update only the M2 block inside the xschem schematic text file.
    Your file format is multi-line, so we replace W=... and L=... inside the block.
    """
    content = SCH_PATH.read_text()

    pattern = re.compile(
        r'(C \{sky130_fd_pr/nfet_01v8\.sym\}.*?\{name=' + re.escape(TARGET_INSTANCE) +
        r'\b.*?^W=)([^\n]+)(.*?^L=)([^\n]+)(.*?^\})',
        re.DOTALL | re.MULTILINE
    )

    def repl(m):
        return f"{m.group(1)}{w_um:.2f}{m.group(3)}{l_um:.4f}{m.group(5)}"

    new_content, count = pattern.subn(repl, content, count=1)

    if count == 0:
        return False

    SCH_PATH.write_text(new_content)
    return True


def run_make_flow(corner_make: str, tb_name: str):
    result = run_cmd(["make", corner_make, f"TB={tb_name}"], timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"Make flow failed: make {corner_make} TB={tb_name}\n\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )


def find_latest_file(root: Path, pattern: str) -> Path:
    files = list(root.rglob(pattern))
    if not files:
        raise FileNotFoundError(f"No file matching {pattern} found under {root}")
    return max(files, key=lambda p: p.stat().st_mtime)


def strip_control_and_end(netlist_text: str) -> str:
    """
    Remove existing .control/.endc block and trailing .end
    so we can append our own control block safely.
    Also comments out explicit top-level analyses to avoid accidental reruns.
    """
    txt = re.sub(r'(?is)\.control\b.*?\.endc\b', '', netlist_text)

    # comment out top-level analyses / prints / saves
    lines = []
    for line in txt.splitlines():
        s = line.strip().lower()
        if s.startswith((".op", ".dc", ".ac", ".tran", ".save", ".print", ".plot", ".meas")):
            lines.append(f"* {line}")
        else:
            lines.append(line)
    txt = "\n".join(lines)

    txt = re.sub(r'(?im)^\s*\.end\s*$', '', txt)
    return txt.strip() + "\n"


def extract_dc_from_raw(raw_file: Path):
    """
    Load raw file with ngspice and print:
      v(VIN) v(VOUT) i(VDS)
    """
    deck = f"""
.control
load {raw_file}
print v({DC_GATE_NODE}) v({DC_DRAIN_NODE}) i({DC_DRAIN_CURRENT_SOURCE})
quit
.endc
.end
"""
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False) as tf:
        tf.write(deck)
        temp_path = tf.name

    try:
        result = run_cmd(["ngspice", "-b", temp_path], timeout=60)
        if result.returncode != 0:
            raise RuntimeError(
                f"ngspice raw extraction failed\n\n"
                f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            )

        dc_points = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if (
                not line
                or "Index" in line
                or "---" in line
                or "ngspice" in line.lower()
                or "Note:" in line
            ):
                continue

            if re.match(r"^\d+", line):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        vgs = float(parts[1])
                        vds = float(parts[2])
                        ids = abs(float(parts[3]))
                    except ValueError:
                        continue

                    dc_points.append({
                        "vgs": vgs,
                        "vds": vds,
                        "id": ids,
                    })

        return dc_points

    finally:
        os.unlink(temp_path)


def is_probably_saturated(vgs: float, vds: float, vth: float = DEFAULT_VTH) -> bool:
    vov = vgs - vth
    return (vov > 0.0) and (vds >= 0.95 * vov)


def build_ac_wrapper(base_netlist_text: str, vgs: float, vds: float) -> str:
    """
    Build a wrapper around the generated netlist.
    Case 1: excite gate, drain ac=0
      - gm from Re(I(VDS))
      - Cgg from Im(I(gate source))/w
      - Cgd from Im(I(VDS))/w

    Case 2: excite drain, gate ac=0
      - gds from Re(I(VDS))
      - Cdd from Im(I(VDS))/w
      - another view of Cgd from Im(I(gate source))/w
    """
    f = AC_FREQ_HZ
    w = 2.0 * math.pi * f

    base = strip_control_and_end(base_netlist_text)

    wrapper = f"""{base}

.control
set noaskquit

* set DC operating point
alter {AC_GATE_SOURCE} dc={vgs}
alter {AC_DRAIN_SOURCE} dc={vds}

echo "__CASE1__"
* Gate excitation: Vg_ac = 1, Vd_ac = 0
alter {AC_GATE_SOURCE} ac=1
alter {AC_DRAIN_SOURCE} ac=0
ac lin 1 {f} {f}
print real(i({AC_DRAIN_SOURCE})) imag(i({AC_DRAIN_SOURCE})) imag(i({AC_GATE_SOURCE}))

echo "__CASE2__"
* Drain excitation: Vd_ac = 1, Vg_ac = 0
alter {AC_GATE_SOURCE} ac=0
alter {AC_DRAIN_SOURCE} ac=1
ac lin 1 {f} {f}
print real(i({AC_DRAIN_SOURCE})) imag(i({AC_DRAIN_SOURCE})) imag(i({AC_GATE_SOURCE}))

quit
.endc
.end
"""
    return wrapper


def parse_ac_output(stdout: str):
    """
    Expected numeric lines after CASE markers:
      CASE1 print -> real(i(VDS)) imag(i(VDS)) imag(i(VGATE))
      CASE2 print -> real(i(VDS)) imag(i(VDS)) imag(i(VGATE))
    """
    current_case = None
    case_data = {}

    for line in stdout.splitlines():
        s = line.strip()

        if s == "__CASE1__":
            current_case = "case1"
            continue
        if s == "__CASE2__":
            current_case = "case2"
            continue

        if not current_case:
            continue

        if (
            not s
            or "Index" in s
            or "---" in s
            or "ngspice" in s.lower()
            or "Note:" in s
        ):
            continue

        if re.match(r"^\d+", s):
            parts = s.split()
            # index + 3 printed values
            if len(parts) >= 4:
                try:
                    real_ids = float(parts[1])
                    imag_ids = float(parts[2])
                    imag_igate = float(parts[3])
                except ValueError:
                    continue

                case_data[current_case] = {
                    "real_ids": real_ids,
                    "imag_ids": imag_ids,
                    "imag_igate": imag_igate,
                }
                current_case = None

    if "case1" not in case_data or "case2" not in case_data:
        raise RuntimeError(
            "Could not parse AC output cleanly.\n"
            "Check AC_GATE_SOURCE / AC_DRAIN_SOURCE names."
        )

    return case_data


def ac_extract_one(netlist_path: Path, point: dict):
    """
    Returns gm, gds, and AC-derived caps for one bias point.
    """
    base_text = netlist_path.read_text()
    deck = build_ac_wrapper(base_text, point["vgs"], point["vds"])

    with tempfile.NamedTemporaryFile("w", suffix=".spice", delete=False) as tf:
        tf.write(deck)
        temp_path = tf.name

    try:
        result = run_cmd(["ngspice", "-b", temp_path], timeout=120)
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"ngspice AC failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            }

        parsed = parse_ac_output(result.stdout)

        w = 2.0 * math.pi * AC_FREQ_HZ

        # CASE1: gate excitation
        gm = abs(parsed["case1"]["real_ids"])
        cgd_1 = abs(parsed["case1"]["imag_ids"]) / w
        cgg = abs(parsed["case1"]["imag_igate"]) / w

        # CASE2: drain excitation
        gds = abs(parsed["case2"]["real_ids"])
        cdd = abs(parsed["case2"]["imag_ids"]) / w
        cgd_2 = abs(parsed["case2"]["imag_igate"]) / w

        cgd = 0.5 * (cgd_1 + cgd_2)
        cdb_eff = max(cdd - cgd, 0.0)
        cgs_eff = max(cgg - cgd, 0.0)

        return {
            "success": True,
            "vgs": point["vgs"],
            "vds": point["vds"],
            "id": point["id"],
            "gm": gm,
            "gds": gds,
            "cgg": cgg,
            "cgd": cgd,
            "cgs_eff": cgs_eff,
            "cdb_eff": cdb_eff,
            "csb": 0.0,  # not separately measurable in this tied-source/body bench
        }

    finally:
        os.unlink(temp_path)


def ac_worker(args):
    netlist_path_str, point = args
    return ac_extract_one(Path(netlist_path_str), point)


def save_csv(csv_path: Path, corner: str, w_um: float, l_um: float, rows):
    wl = w_um / l_um if l_um > 0 else 0.0
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="") as f:
        fieldnames = [
            "Corner",
            "W_um",
            "L_um",
            "WL_ratio",
            "VGS_V",
            "VDS_V",
            "ID_A",
            "gm_S",
            "gds_S",
            "gm_ID_S_per_A",
            "ro_Ohm",
            "Cgg_F",
            "Cgd_F",
            "Cgs_eff_F",
            "Cdb_eff_F",
            "Csb_F",
            "Notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for r in rows:
            if not r["success"]:
                continue

            gm_id = r["gm"] / r["id"] if r["id"] > 1e-18 else 0.0
            ro = 1.0 / r["gds"] if r["gds"] > 1e-18 else 1e18

            writer.writerow({
                "Corner": corner,
                "W_um": f"{w_um:.2f}",
                "L_um": f"{l_um:.4f}",
                "WL_ratio": f"{wl:.4f}",
                "VGS_V": f"{r['vgs']:.6f}",
                "VDS_V": f"{r['vds']:.6f}",
                "ID_A": f"{r['id']:.6e}",
                "gm_S": f"{r['gm']:.6e}",
                "gds_S": f"{r['gds']:.6e}",
                "gm_ID_S_per_A": f"{gm_id:.6f}",
                "ro_Ohm": f"{ro:.6e}",
                "Cgg_F": f"{r['cgg']:.6e}",
                "Cgd_F": f"{r['cgd']:.6e}",
                "Cgs_eff_F": f"{r['cgs_eff']:.6e}",
                "Cdb_eff_F": f"{r['cdb_eff']:.6e}",
                "Csb_F": f"{r['csb']:.6e}",
                "Notes": "gm/gds/caps from AC; Cgs_eff includes any gate-to-ground residual; source/body tied",
            })


# =============================================================================
# MAIN
# =============================================================================

def main():
    w_um = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
    l_um = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
    corner = sys.argv[3].lower() if len(sys.argv) > 3 else "tt"
    corner_make = CORNER_MAP.get(corner, corner)

    print("=" * 100)
    print("FINAL 2D CHARACTERIZATION")
    print(f"W={w_um:.2f} um, L={l_um:.4f} um, corner={corner} -> make {corner_make}")
    print(f"Schematic source file: {SCH_PATH}")
    print(f"Target transistor: {TARGET_INSTANCE}")
    print(f"AC gate source name: {AC_GATE_SOURCE}")
    print(f"AC drain source name: {AC_DRAIN_SOURCE}")
    print("=" * 100)

    t0 = time.time()

    ensure_backup()
    restore_schematic()

    updated = update_m2_in_schematic(w_um, l_um)
    if not updated:
        raise RuntimeError(f"Could not find/update {TARGET_INSTANCE} in {SCH_PATH}")

    print("✓ Updated schematic source file for M2")

    # Run DC sweep through Make/CICSIM
    run_make_flow(corner_make, TB_DC)
    print("✓ DC Make/CICSIM run complete")

    raw_file = find_latest_file(TB_NETLIST_DIR, "*.raw")
    print(f"✓ Found DC raw file: {raw_file}")

    # Also grab the generated netlist that ngspice can run for AC wrapper
    # Adjust pattern if your flow uses another extension
    try:
        netlist_file = find_latest_file(TB_NETLIST_DIR, "*.spice")
    except FileNotFoundError:
        netlist_file = find_latest_file(TB_NETLIST_DIR, "*.cir")

    print(f"✓ Found generated netlist: {netlist_file}")

    dc_points = extract_dc_from_raw(raw_file)
    print(f"✓ Extracted {len(dc_points)} DC points")

    sat_points = [p for p in dc_points if is_probably_saturated(p["vgs"], p["vds"])]
    print(f"✓ Saturated/useful DC points: {len(sat_points)}")

    # AC extraction at each point
    nproc = max(1, cpu_count() - 1)
    print(f"✓ Running AC extraction on {nproc} cores")

    jobs = [(str(netlist_file), p) for p in sat_points]

    with Pool(nproc) as pool:
        results = pool.map(ac_worker, jobs)

    ok = [r for r in results if r["success"]]
    bad = [r for r in results if not r["success"]]

    print(f"✓ AC success: {len(ok)} / {len(results)}")
    if bad:
        print(f"⚠ AC failed for {len(bad)} points")
        print("  First failure:")
        print(bad[0]["error"][:1200])

    csv_path = Path(f"{CSV_PREFIX}_{corner}.csv")
    save_csv(csv_path, corner, w_um, l_um, ok)

    dt = time.time() - t0
    print(f"✓ Saved CSV: {csv_path}")
    print(f"Done in {dt:.1f} s")
    print("=" * 100)


if __name__ == "__main__":
    main()