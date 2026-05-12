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

W_LIST = [20, 40, 60]
R_LIST = [5e3, 10e3, 15e3, 20e3]
VIN_LIST = [0.5, 0.6, 0.7, 0.8, 0.9]

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

    # Find and modify W value in transistor (look for W= pattern)
    w_found = False
    for i, line in enumerate(lines):
        if 'W=' in line and ('M=' in line or 'M2' in line or i < 50):  # Transistor lines typically early in file
            lines[i] = re.sub(r'W=[\d.]+', f'W={w_val}', line)
            w_found = True
            break

    # Find and modify R value in R1 resistor
    r_found = False
    for i, line in enumerate(lines):
        if 'name=R1' in line or 'R1' in line:
            # R value should be in the same or next line
            if 'value=' in line:
                r_str = format_resistance(r_val)
                lines[i] = re.sub(r'value=[^\s,;]+', f'value={r_str}', line)
                r_found = True
                break
            elif i + 1 < len(lines) and 'value=' in lines[i + 1]:
                r_str = format_resistance(r_val)
                lines[i + 1] = re.sub(r'value=[^\s,;]+', f'value={r_str}', lines[i + 1])
                r_found = True
                break

    if not w_found or not r_found:
        print(f"Warning: W found={w_found}, R found={r_found}")

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


def modify_ac_sweep(spi_file):
    """Modify ac.spi to use 1000 points from 1 Hz to 10G."""
    with open(spi_file, 'r') as f:
        lines = f.readlines()
    
    # Find and replace the ac line
    for i, line in enumerate(lines):
        if 'ac dec' in line or 'ac lin' in line:
            lines[i] = 'ac dec 1000 1 10G\n'
            break
    
    with open(spi_file, 'w') as f:
        f.writelines(lines)


def check_saturation(vout_op, vin_dc, vdd=1.8):
    """Check if MOS is in saturation.
    For simplicity: if Vout is between roughly 0.3V and VDD-0.3V, it's likely saturated.
    """
    # Rough heuristic: MOS in saturation when output is in middle of supply
    saturated = (vout_op > 0.3) and (vout_op < (vdd - 0.3))
    return saturated


def find_3db_frequency(freq, gain_db):
    """Find -3dB frequency (cutoff frequency) from gain vs frequency.
    Finds the first frequency where gain drops 3dB from PEAK gain.
    Returns (f_cutoff, peak_gain_dB, f_peak)
    """
    if len(gain_db) == 0:
        return None, None, None
    
    # Get peak gain (maximum across all frequencies)
    peak_gain = max(gain_db)
    peak_idx = gain_db.index(peak_gain)
    f_peak = freq[peak_idx]
    
    cutoff_gain = peak_gain - 3.0  # -3dB from peak
    
    # Find first frequency after peak where gain drops below -3dB
    # Start from peak and search upward
    f_cutoff = None
    for i in range(peak_idx, len(gain_db)):
        if gain_db[i] <= cutoff_gain:
            f_cutoff = freq[i]
            break
    
    # If not found going up, try going down from peak
    if f_cutoff is None:
        for i in range(peak_idx, -1, -1):
            if gain_db[i] <= cutoff_gain:
                f_cutoff = freq[i]
                break
    
    # If still not found, use the nearest frequency to the cutoff
    if f_cutoff is None:
        # Find closest gain to cutoff_gain
        closest_idx = min(range(len(gain_db)), key=lambda i: abs(gain_db[i] - cutoff_gain))
        f_cutoff = freq[closest_idx]
    
    return f_cutoff, peak_gain, f_peak


def calculate_gbw(peak_gain_db, f_3db):
    """Calculate GBW (Gain-Bandwidth Product).
    GBW = (10^(Peak_Gain/20)) * f_3db
    """
    if peak_gain_db is None or f_3db is None:
        return None
    gain_linear = 10.0 ** (peak_gain_db / 20.0)
    gbw = gain_linear * f_3db
    return gbw


def run_make_command(tb_name):
    """Run make command with cicsim."""
    # Don't delete files - just run make and check what gets created
    result = subprocess.run(
        ["make", f"TB={tb_name}", "typical"],
        capture_output=True,
        text=True,
        check=False
    )

    # Check stderr for actual errors (not just warnings)
    if "Error" in result.stderr and "no such device" not in result.stderr.lower():
        # Only raise if it's a real error, not the device measurement error
        if result.returncode != 0:
            raise RuntimeError(f"make failed with return code {result.returncode}\nStderr: {result.stderr[:200]}")

    return result


def parse_op_raw():
    """Parse OP measurement output file (.logm)."""
    logm_file = "output_op/op_SchGtKttTtVt.logm"

    # Retry a few times in case file is still being written
    for attempt in range(5):
        if os.path.exists(logm_file):
            break
        if attempt < 4:
            import time
            time.sleep(0.5)
    else:
        import glob
        op_files = glob.glob("output_op/*")
        raise FileNotFoundError(f"OP logm file not found: {logm_file}\nAvailable files: {op_files}")

    with open(logm_file, 'r') as f:
        content = f.read()

    # Extract values from MEAS_START...MEAS_END section
    meas_start = content.find("MEAS_START")
    meas_end = content.find("MEAS_END")

    if meas_start == -1 or meas_end == -1:
        raise ValueError(f"Could not find MEAS_START/MEAS_END in {logm_file}")

    meas_section = content[meas_start + len("MEAS_START") : meas_end]

    # Parse measurements
    vout = None
    idd = None

    for line in meas_section.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Parse lines like: "v(vout) = 1.677348e-01"
        if 'v(vout)' in line and '=' in line:
            parts = line.split('=')
            if len(parts) == 2:
                vout = float(parts[1].strip())
        elif '-i(vdd)' in line and '=' in line:
            parts = line.split('=')
            if len(parts) == 2:
                idd = float(parts[1].strip())

    if vout is None or idd is None:
        raise ValueError(f"Could not parse vout or idd from {logm_file}")

    return {
        "vout": vout,
        "idd": idd,
    }


def parse_ac_raw():
    """Parse AC raw output file."""
    raw_file = "output_ac/ac_SchGtKttTtVt.raw"

    # Retry a few times in case file is still being written
    for attempt in range(5):
        if os.path.exists(raw_file):
            break
        if attempt < 4:
            import time
            time.sleep(0.5)
    else:
        import glob
        ac_files = glob.glob("output_ac/*")
        raise FileNotFoundError(f"AC raw file not found: {raw_file}\nAvailable files: {ac_files}")

    with open(raw_file, 'r') as f:
        lines = f.readlines()

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

        # Parse frequency line: format is "0    1.000e+00,0.0e+00" (point index, frequency with comma separator)
        parts = re.split(r"\s+", line)

        if len(parts) >= 2 and parts[0].isdigit():
            try:
                # Extract frequency from first part (real component, before comma)
                f_real = float(parts[1].split(",")[0])
                freq.append(f_real)

                # Skip to next line (current value - variable 1: i(v.xdut.v1))
                i += 1

                # Skip current value and move to vin
                i += 1

                # Read vin (real,imag format) - variable 2: v(vin)
                if i < len(lines):
                    vin_line = lines[i].strip()
                    vin_real, vin_imag = map(float, vin_line.split(","))
                    vin_vals.append(complex(vin_real, vin_imag))

                # Skip to next line for vout
                i += 1

                # Read vout (real,imag format) - variable 3: v(vout)
                if i < len(lines):
                    vout_line = lines[i].strip()
                    vout_real, vout_imag = map(float, vout_line.split(","))
                    vout_vals.append(complex(vout_real, vout_imag))

                i += 1
                continue
            except (ValueError, IndexError):
                pass

        i += 1

    if not freq:
        raise ValueError(f"Could not parse any data from {raw_file}")

    # Calculate gain: gain_dB = 20 * log10(|Vout / Vin|)
    # Measure both ac_output and ac_input, then divide
    gain_db = []
    for vo, vi in zip(vout_vals, vin_vals):
        if abs(vi) > 1e-15:
            gain = abs(vo) / abs(vi)
            gain_db.append(20 * math.log10(gain))
        else:
            gain_db.append(0)

    max_idx = max(range(len(gain_db)), key=lambda k: gain_db[k])
    f_3db, peak_gain, f_peak = find_3db_frequency(freq, gain_db)
    gbw = calculate_gbw(peak_gain, f_3db)

    return {
        "gain_max_db": gain_db[max_idx],
        "gain_max_freq": freq[max_idx],
        "gain_db_at_0Hz": gain_db[0] if gain_db else 0,
        "peak_gain_db": peak_gain,
        "f_peak_Hz": f_peak,
        "f_3db_Hz": f_3db,
        "gbw": gbw,
        "freq_array": freq,
        "gain_array": gain_db,
    }


def main():
    rows = []

    print("Starting parametric sweep using make-based approach...")
    print(f"Parameters: W={W_LIST}, R={R_LIST}, VIN={VIN_LIST}")
    print(f"Total combinations: {len(W_LIST) * len(R_LIST) * len(VIN_LIST)}\n")

    # Build netlist first
    print("Building netlist...")
    result = subprocess.run(["make", "netlist"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"Warning: netlist build returned {result.returncode}")
        print(result.stderr[:200])

    # Backup original files
    backup_file(SCH_FILE)
    backup_file(OP_SPI_FILE)
    backup_file(AC_SPI_FILE)

    try:
        total = len(W_LIST) * len(R_LIST) * len(VIN_LIST)
        for idx, (w, r, vin_dc) in enumerate(itertools.product(W_LIST, R_LIST, VIN_LIST), 1):
            print(f"[{idx}/{total}] W={w}, R={r/1e3:.1f}k, VIN={vin_dc}V", end=" ")

            try:
                # Modify schematic
                modify_sch_file(w, r)
                
                # Regenerate netlists after schematic modification
                subprocess.run(["make", "netlist"], capture_output=True, check=False)
                
                # Clear old simulation outputs to avoid SHA conflicts
                subprocess.run(["rm", "-rf", "output_op", "output_ac"], check=False)

                # Modify testbench files for VIN
                modify_spi_file(OP_SPI_FILE, vin_dc)
                modify_spi_file(AC_SPI_FILE, vin_dc)

                # Run OP analysis
                run_make_command("op")
                op_data = parse_op_raw()

                # Check if MOS is in saturation
                saturated = check_saturation(op_data['vout'], vin_dc)
                
                if saturated:
                    # Modify AC sweep parameters
                    modify_ac_sweep(AC_SPI_FILE)
                    
                    # Run AC analysis only if saturated
                    run_make_command("ac")
                    ac_data = parse_ac_raw()
                    
                    row = {
                        "W_um": w,
                        "R_ohm": r,
                        "vin_dc_V": vin_dc,
                        "vout_op_V": f"{op_data['vout']:.6e}",
                        "idd_op_A": f"{op_data['idd']:.6e}",
                        "saturated": "Yes",
                        "gain_0Hz_db": f"{ac_data['gain_db_at_0Hz']:.4f}",
                        "peak_gain_db": f"{ac_data['peak_gain_db']:.4f}",
                        "f_peak_Hz": f"{ac_data['f_peak_Hz']:.6e}",
                        "gain_max_db": f"{ac_data['gain_max_db']:.4f}",
                        "gain_max_freq_Hz": f"{ac_data['gain_max_freq']:.6e}",
                        "f_3db_Hz": f"{ac_data['f_3db_Hz']:.6e}" if ac_data['f_3db_Hz'] else "",
                        "gbw_Hz": f"{ac_data['gbw']:.6e}" if ac_data['gbw'] else "",
                    }
                    rows.append(row)
                    print(f"✓ Saturated, Peak_Gain={ac_data['peak_gain_db']:.2f}dB, F_3dB={ac_data['f_3db_Hz']:.2e}Hz, GBW={ac_data['gbw']:.2e}Hz")
                else:
                    # If not saturated, skip AC and just record OP data
                    row = {
                        "W_um": w,
                        "R_ohm": r,
                        "vin_dc_V": vin_dc,
                        "vout_op_V": f"{op_data['vout']:.6e}",
                        "idd_op_A": f"{op_data['idd']:.6e}",
                        "saturated": "No",
                        "gain_0Hz_db": "",
                        "peak_gain_db": "",
                        "f_peak_Hz": "",
                        "gain_max_db": "",
                        "gain_max_freq_Hz": "",
                        "f_3db_Hz": "",
                        "gbw_Hz": "",
                    }
                    rows.append(row)
                    print(f"✗ Not saturated (Vout={op_data['vout']:.3f}V) - skipping AC")

            except Exception as e:
                rows.append({
                    "W_um": w,
                    "R_ohm": r,
                    "vin_dc_V": vin_dc,
                    "vout_op_V": "",
                    "idd_op_A": "",
                    "saturated": "",
                    "gain_0Hz_db": "",
                    "peak_gain_db": "",
                    "f_peak_Hz": "",
                    "gain_max_db": "",
                    "gain_max_freq_Hz": "",
                    "f_3db_Hz": "",
                    "gbw_Hz": "",
                    "error": str(e)[:100],
                })
                print(f"✗ {str(e)[:50]}")

        # Write results to CSV
        with open("sweep_results_make.csv", "w", newline="") as f:
            fieldnames = [
                "W_um", "R_ohm", "vin_dc_V",
                "vout_op_V", "idd_op_A",
                "saturated",
                "gain_0Hz_db", "peak_gain_db", "f_peak_Hz", 
                "gain_max_db", "gain_max_freq_Hz",
                "f_3db_Hz", "gbw_Hz",
                "error"
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
