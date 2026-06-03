#!/usr/bin/env python3
"""
Run tb_op.spi and tb_ac.spi across sky130 process corners at VDD=1.2 V.

Generates one wrapper .spi per corner that:
  .lib  "$PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" <corner>
  .include tb_*.spi

Then runs ngspice -b on each and parses the SUMMARY section.

Usage:
    python run_corners.py            # run both OP and AC, all 5 corners
    python run_corners.py op         # just OP
    python run_corners.py ac         # just AC
"""

import os, re, subprocess, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
CORNERS = ["tt", "ff", "ss", "fs", "sf"]
PDK = os.environ.get("PDK_ROOT", "/opt/pdk/share/pdk")
LIB = f"{PDK}/sky130A/libs.tech/ngspice/sky130.lib.spice"


def wrap(corner: str, tb: str) -> pathlib.Path:
    """Make a wrapper netlist that pulls in the corner lib then the tb."""
    work = HERE / "run"
    work.mkdir(exist_ok=True)
    wrapper = work / f"{tb}_{corner}.spi"
    with open(HERE / f"tb_{tb}.spi") as f:
        body = f.read()
    # Replace .include dut.spi with absolute path so wrapper can live in run/
    body = body.replace(".include dut.spi", f'.include "{HERE}/dut.spi"')
    with open(wrapper, "w") as f:
        f.write(f"* corner = {corner}\n")
        f.write(f'.lib "{LIB}" {corner}\n')
        f.write(body)
    return wrapper


def run(wrapper: pathlib.Path) -> str:
    res = subprocess.run(
        ["ngspice", "-b", str(wrapper)],
        capture_output=True, text=True, cwd=wrapper.parent,
        timeout=600,
    )
    return res.stdout + "\n----STDERR----\n" + res.stderr


def grab(label: str, text: str) -> str:
    """Find first line in text containing label after '=' and return its value."""
    m = re.search(rf"{label}\s*=\s*([-\d\.eE+]+)", text)
    return m.group(1) if m else "N/A"


def grab_print(name: str, text: str) -> str:
    """Catch `name = value` lines printed via `print`."""
    m = re.search(rf"^\s*{re.escape(name)}\s*=\s*([-\d\.eE+]+)\s*$",
                  text, flags=re.MULTILINE)
    return m.group(1) if m else "N/A"


def parse_op(text: str) -> dict:
    keys = ["v(ibias)", "v(xdut.vbp)", "v(xdut.vbias1)", "v(xdut.vbias2)",
            "v(xdut.ntail)", "v(xdut.nbl)", "v(xdut.nbr)", "v(xdut.fl)",
            "v(voutp)", "-i(vdd)"]
    out = {k: grab_print(k, text) for k in keys}
    return out


def parse_ac(text: str) -> dict:
    return {
        "dc_gain_db": grab("dc_gain_db", text),
        "fgbw":       grab("fgbw", text),
        "pm":         grab("pm", text),
        "phase_ugf":  grab("phase_ugf", text),
    }


def do_op():
    print("\n========== OP across corners (VDD=1.2 V) ==========")
    header = "{:<6} {:>7} {:>7} {:>7} {:>7} {:>7} {:>7} {:>7} {:>7} {:>9}".format(
        "cor", "ibias", "vbp", "vb1", "vb2", "ntail", "nbL", "fL", "voutp", "IDD[uA]")
    print(header)
    print("-" * len(header))
    for c in CORNERS:
        w = wrap(c, "op")
        out = run(w)
        (w.parent / f"op_{c}.log").write_text(out)
        d = parse_op(out)
        try:
            idd_uA = float(d["-i(vdd)"]) * 1e6
            row = "{:<6} {:>7.3f} {:>7.3f} {:>7.3f} {:>7.3f} {:>7.3f} {:>7.3f} {:>7.3f} {:>7.3f} {:>9.1f}".format(
                c,
                float(d["v(ibias)"]), float(d["v(xdut.vbp)"]), float(d["v(xdut.vbias1)"]),
                float(d["v(xdut.vbias2)"]), float(d["v(xdut.ntail)"]),
                float(d["v(xdut.nbl)"]), float(d["v(xdut.fl)"]),
                float(d["v(voutp)"]), idd_uA)
        except (ValueError, KeyError):
            row = f"{c:<6}  PARSE ERROR -- see run/op_{c}.log"
        print(row)


def do_ac():
    print("\n========== AC across corners (VDD=1.2 V, CL=5pF) ==========")
    header = "{:<6} {:>12} {:>14} {:>10} {:>10}".format(
        "cor", "A0 [dB]", "GBW [Hz]", "ph@ugf", "PM [deg]")
    print(header)
    print("-" * len(header))
    for c in CORNERS:
        w = wrap(c, "ac")
        out = run(w)
        (w.parent / f"ac_{c}.log").write_text(out)
        d = parse_ac(out)
        try:
            print("{:<6} {:>12.2f} {:>14.3e} {:>10.2f} {:>10.2f}".format(
                c, float(d["dc_gain_db"]), float(d["fgbw"]),
                float(d["phase_ugf"]), float(d["pm"])))
        except ValueError:
            print(f"{c:<6}  PARSE ERROR -- see run/ac_{c}.log")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("op", "all"):
        do_op()
    if target in ("ac", "all"):
        do_ac()
