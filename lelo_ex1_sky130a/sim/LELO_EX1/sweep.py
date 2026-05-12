import itertools
import math
import os
import re
import subprocess
import csv

W_LIST = [5, 10, 20, 40, 60]
R_LIST = [1e3, 2e3, 5e3, 10e3, 15e3, 20e3]
VIN_LIST = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

LELO_TEMPLATE = """\
.subckt LELO_EX1 VOUT VSS VDD VIN
XM2 VOUT VIN VSS VSS sky130_fd_pr__nfet_01v8 L=0.8 W={WVAL} nf=1 ad=17.4 as=17.4 pd=120.58 ps=120.58 nrd=0.00483333333333333
+ nrs=0.00483333333333333 sa=0 sb=0 sd=0 mult=1 m=1
V1 net1 VOUT 0
.save i(v1)
R1 VDD net1 {RVAL} m=1
.ends
.end
"""

TB_TEMPLATE = """\
.include "lelo_generated.spice"

VSS VSS 0 dc 0
VDD VDD 0 dc 1.8
VIN VIN 0 dc {VIN_DC} ac 1

XDUT VOUT VSS VDD VIN LELO_EX1

.save all

.control
set filetype=ascii
op
write op.raw
ac dec 100 1 1e9
write ac.raw
quit
.endc

.end
"""

def run_ngspice(netlist_path: str) -> None:
    result = subprocess.run(
        ["ngspice", "-b", netlist_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ngspice failed:\\nSTDOUT:\\n{result.stdout}\\nSTDERR:\\n{result.stderr}")

def parse_op_raw(path: str):
    with open(path, "r") as f:
        text = f.read()

    values_match = re.search(r"Values:\\s*0\\s+([\\deE+\\-.]+)\\s+([\\deE+\\-.]+)\\s+([\\deE+\\-.]+)\\s+([\\deE+\\-.]+)", text)
    if not values_match:
        raise ValueError(f"Could not parse OP raw file: {path}")

    vss = float(values_match.group(1))
    vin = float(values_match.group(2))
    vout = float(values_match.group(3))
    ivdd = float(values_match.group(4))

    return {
        "vss": vss,
        "vin": vin,
        "vout": vout,
        "ivdd": ivdd,
        "idd_abs": abs(ivdd),
    }

def parse_ac_raw(path: str):
    freq = []
    vin = []
    vout = []

    with open(path, "r") as f:
        lines = f.readlines()

    in_values = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("Values:"):
            in_values = True
            i += 1
            continue

        if in_values:
            parts = re.split(r"\\s+", line)
            if len(parts) >= 2 and parts[0].isdigit():
                f_real = float(parts[1].split(",")[0])
                freq.append(f_real)

                i_line = lines[i + 1].strip()   # current, skip
                vin_line = lines[i + 2].strip()
                vout_line = lines[i + 3].strip()

                vin_real, vin_imag = map(float, vin_line.split(","))
                vout_real, vout_imag = map(float, vout_line.split(","))

                vin.append(complex(vin_real, vin_imag))
                vout.append(complex(vout_real, vout_imag))

                i += 4
                continue
        i += 1

    if not freq:
        raise ValueError(f"Could not parse AC raw file: {path}")

    gain_db = [20 * math.log10(abs(vo / vi)) for vo, vi in zip(vout, vin)]

    max_idx = max(range(len(gain_db)), key=lambda k: gain_db[k])

    return {
        "gain_max_db": gain_db[max_idx],
        "gain_max_freq": freq[max_idx],
        "gain_db_at_1st": gain_db[0],
    }

def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)

def main():
    rows = []

    for w, r, vin_dc in itertools.product(W_LIST, R_LIST, VIN_LIST):
        write_file("lelo_generated.spice", LELO_TEMPLATE.format(WVAL=w, RVAL=r))
        write_file("tb_generated.spice", TB_TEMPLATE.format(VIN_DC=vin_dc))

        try:
            run_ngspice("tb_generated.spice")
            op_data = parse_op_raw("op.raw")
            ac_data = parse_ac_raw("ac.raw")

            rows.append({
                "W_um": w,
                "R_ohm": r,
                "vin_dc_V": vin_dc,
                "vout_op_V": op_data["vout"],
                "idd_op_A": op_data["idd_abs"],
                "gain_max_db": ac_data["gain_max_db"],
                "gain_max_freq_Hz": ac_data["gain_max_freq"],
                "gain_firstpoint_db": ac_data["gain_db_at_1st"],
            })
            print(f"OK: W={w}, R={r}, vin={vin_dc}")
        except Exception as e:
            rows.append({
                "W_um": w,
                "R_ohm": r,
                "vin_dc_V": vin_dc,
                "vout_op_V": "",
                "idd_op_A": "",
                "gain_max_db": "",
                "gain_max_freq_Hz": "",
                "gain_firstpoint_db": "",
                "error": str(e),
            })
            print(f"FAIL: W={w}, R={r}, vin={vin_dc} -> {e}")

    with open("sweep_results.csv", "w", newline="") as f:
        fieldnames = [
            "W_um", "R_ohm", "vin_dc_V",
            "vout_op_V", "idd_op_A",
            "gain_max_db", "gain_max_freq_Hz",
            "gain_firstpoint_db", "error"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()
