#!/usr/bin/env python3
"""
Parametric sweep using make-based cicsim approach.
Modifies LELO_EX1.sch and tb files, then runs make commands to extract gain data.
"""

import itertools
import math
import os
import re
import subprocess
import csv
import shutil

W_LIST = [20]
R_LIST = [5e3]
VIN_LIST = [0.8]

# File paths
SCH_FILE = "../../design/LELO_EX1_SKY130A/LELO_EX1.sch"
OP_SPI_FILE = "op.spi"
AC_SPI_FILE = "ac.spi"


def backup_file(filepath):
    """Create a backup of the file before modification."""
    if os.path.exists(filepath):
        backup_path = filepath + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(filepath, backup_path)
        return backup_path
    return None


def restore_file(filepath):
    """Restore file from backup."""
    backup_path = filepath + ".bak"
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filepath)


def modify_sch_file(w_val, r_val):
    """Modify LELO_EX1.sch to set W and R values."""
    with open(SCH_FILE, 'r') as f:
        lines = f.readlines()

    # Find and modify W value in M2 transistor (line 26)
    for i, line in enumerate(lines):
        if 'W=' in line and 'W=60' in line:
            lines[i] = re.sub(r'W=[\d.]+', f'W={w_val}', line)
            break

    # Find and modify R value in R1 resistor (line 44)
    for i, line in enumerate(lines):
        if 'name=R1' in line:
            # R value should be in the next line
            if i + 1 < len(lines) and 'value=' in lines[i + 1]:
                r_str = format_resistance(r_val)
                lines[i + 1] = re.sub(r'value=[\d.kmΩMeg]+', f'value={r_str}', lines[i + 1])
            break

    with open(SCH_FILE, 'w') as f:
        f.writelines(lines)


def format_resistance(r_ohms):
    """Convert resistance in ohms to string format (e.g., 5k, 1.5k)."""
    if r_ohms >= 1e6:
        return f"{r_ohms / 1e6:.4g}Meg"
    elif r_ohms >= 1e3:
        return f"{r_ohms / 1e3:.4g}k"
    else:
        return f"{r_ohms:.4g}"


def modify_spi_file(spi_file, vin_val):
    """Modify ac.spi or op.spi to set VIN value."""
    with open(spi_file, 'r') as f:
        content = f.read()

    # Modify the vin_dc or vin_val parameter
    if 'vin_dc' in content:
        content = re.sub(r'\.param vin_dc = [\d.]+',
                        f'.param vin_dc = {vin_val}', content)
    elif 'vin_val' in content:
        content = re.sub(r'\.param vin_val = [\d.]+',
                        f'.param vin_val = {vin_val}', content)

    with open(spi_file, 'w') as f:
        f.write(content)


def run_make_command(tb_name):
    """Run make command with cicsim."""
    result = subprocess.run(
        ["make", f"TB={tb_name}", "typical"],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"make failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


def parse_op_raw():
    """Parse OP raw output file."""
    raw_file = "output_op/op_SchGtKttTtVt.raw"

    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"OP raw file not found: {raw_file}")

    with open(raw_file, 'r') as f:
        lines = f.readlines()

    # Find the Variables section to understand ordering
    var_indices = {}
    in_vars = False
    for line in lines:
        if line.strip() == "Variables:":
            in_vars = True
            continue
        if in_vars:
            if line.startswith("Values:"):
                break
            if line.strip() and not line.startswith("Values:"):
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    idx = int(parts[0])
                    var_name = parts[1]
                    var_indices[var_name] = idx

    # Find Values section
    values_start = None
    for i, line in enumerate(lines):
        if line.strip() == "Values:":
            values_start = i + 1
            break

    if values_start is None:
        raise ValueError(f"Could not find Values section in {raw_file}")

    # Parse values
    values = []
    for i in range(values_start, len(lines)):
        line = lines[i].strip()
        if line and not line.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            continue
        if line:
            try:
                val = float(line)
                values.append(val)
            except ValueError:
                pass

    # Extract values by index
    vin = values[var_indices.get('v(vin)', 1)] if 'v(vin)' in var_indices else values[1]
    vout = values[var_indices.get('v(vout)', 2)] if 'v(vout)' in var_indices else values[2]
    ivdd = values[var_indices.get('i(vdd)', 3)] if 'i(vdd)' in var_indices else values[3]

    return {
        "vout": vout,
        "idd": abs(ivdd),
    }


def parse_ac_raw():
    """Parse AC raw output file."""
    raw_file = "output_ac/ac_SchGtKttTtVt.raw"

    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"AC raw file not found: {raw_file}")

    with open(raw_file, 'r') as f:
        lines = f.readlines()

    # Find Variables section
    var_indices = {}
    in_vars = False
    for line in lines:
        if line.strip() == "Variables:":
            in_vars = True
            continue
        if in_vars:
            if line.startswith("Values:"):
                break
            if line.strip() and not line.startswith("Values:"):
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    idx = int(parts[0])
                    var_name = parts[1]
                    var_indices[var_name] = idx

    # Find Values section
    values_start = None
    for i, line in enumerate(lines):
        if line.strip() == "Values:":
            values_start = i + 1
            break

    if values_start is None:
        raise ValueError(f"Could not find Values section in {raw_file}")

    freq = []
    vin_vals = []
    vout_vals = []

    i = values_start
    while i < len(lines):
        line = lines[i].strip()

        # Look for point index
        if line and line[0].isdigit() and ',' in line:
            parts = line.split(',')
            if len(parts) == 2:
                freq_real = float(parts[0])
                freq.append(freq_real)

                # Skip current line (index 1)
                i += 2

                # Read vin (index 2)
                if i < len(lines):
                    vin_line = lines[i].strip()
                    parts = vin_line.split(',')
                    if len(parts) == 2:
                        vin_real = float(parts[0])
                        vin_imag = float(parts[1])
                        vin_vals.append(complex(vin_real, vin_imag))
                    i += 1

                # Read vout (index 3)
                if i < len(lines):
                    vout_line = lines[i].strip()
                    parts = vout_line.split(',')
                    if len(parts) == 2:
                        vout_real = float(parts[0])
                        vout_imag = float(parts[1])
                        vout_vals.append(complex(vout_real, vout_imag))
                    i += 1

                continue

        i += 1

    if not freq:
        raise ValueError(f"Could not parse any data from {raw_file}")

    # Calculate gain
    gain_db = []
    for vo, vi in zip(vout_vals, vin_vals):
        if abs(vi) > 1e-12:
            gain_db.append(20 * math.log10(abs(vo / vi)))
        else:
            gain_db.append(0)

    max_idx = max(range(len(gain_db)), key=lambda k: gain_db[k])

    return {
        "gain_max_db": gain_db[max_idx],
        "gain_max_freq": freq[max_idx],
        "gain_db_at_1Hz": gain_db[0] if gain_db else 0,
    }


def main():
    rows = []

    print("Starting parametric sweep using make-based approach...")
    print(f"Parameters: W={W_LIST}, R={R_LIST}, VIN={VIN_LIST}")
    print(f"Total combinations: {len(W_LIST) * len(R_LIST) * len(VIN_LIST)}\n")

    # Backup original files
    backup_file(SCH_FILE)
    backup_file(OP_SPI_FILE)
    backup_file(AC_SPI_FILE)

    try:
        for w_idx, (w, r, vin_dc) in enumerate(itertools.product(W_LIST, R_LIST, VIN_LIST), 1):
            print(f"[{w_idx}/{len(W_LIST)*len(R_LIST)*len(VIN_LIST)}] W={w}, R={r/1e3:.1f}k, VIN={vin_dc}V", end=" ")

            try:
                # Modify schematic
                modify_sch_file(w, r)

                # Modify testbench files for VIN
                modify_spi_file(OP_SPI_FILE, vin_dc)
                modify_spi_file(AC_SPI_FILE, vin_dc)

                # Run OP analysis
                run_make_command("op")
                op_data = parse_op_raw()

                # Run AC analysis
                run_make_command("ac")
                ac_data = parse_ac_raw()

                row = {
                    "W_um": w,
                    "R_ohm": r,
                    "vin_dc_V": vin_dc,
                    "vout_op_V": f"{op_data['vout']:.6e}",
                    "idd_op_A": f"{op_data['idd']:.6e}",
                    "gain_max_db": f"{ac_data['gain_max_db']:.4f}",
                    "gain_max_freq_Hz": f"{ac_data['gain_max_freq']:.6e}",
                    "gain_1Hz_db": f"{ac_data['gain_db_at_1Hz']:.4f}",
                }
                rows.append(row)
                print(f"✓ Gain={ac_data['gain_max_db']:.2f}dB")

            except Exception as e:
                rows.append({
                    "W_um": w,
                    "R_ohm": r,
                    "vin_dc_V": vin_dc,
                    "vout_op_V": "",
                    "idd_op_A": "",
                    "gain_max_db": "",
                    "gain_max_freq_Hz": "",
                    "gain_1Hz_db": "",
                    "error": str(e),
                })
                print(f"✗ {str(e)[:50]}")

        # Write results to CSV
        with open("sweep_results_make.csv", "w", newline="") as f:
            fieldnames = [
                "W_um", "R_ohm", "vin_dc_V",
                "vout_op_V", "idd_op_A",
                "gain_max_db", "gain_max_freq_Hz",
                "gain_1Hz_db", "error"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✓ Results saved to sweep_results_make.csv")

    finally:
        # Restore original files
        print("Restoring original files...")
        restore_file(SCH_FILE)
        restore_file(OP_SPI_FILE)
        restore_file(AC_SPI_FILE)


if __name__ == "__main__":
    main()
