# LELO_5TOTA Simulation Testbenches

## Testbenches

| TB | Command | Output |
|----|---------|--------|
| `op` | `make typical TB=op` | Operating point, device currents, region check |
| `ac` | `make typical TB=ac` | Gain, f-3dB, GBW, phase margin |

Results land in `output_op/` and `output_ac/` respectively.

---

## Plotting AC Results

```bash
python3 plot_ac.py
```

Reads the most recent `output_ac/ac_*.raw` and saves `output_ac/bode_plot.png`.

---

## How to Print Values to the Log File in ngspice

ngspice has two output streams inside `.control`:

| Command | Stream | Captured in cicsim `.log`? |
|---------|--------|---------------------------|
| `print varname` | display (stderr-like) | **No** |
| `echo "text"` | stdout | **Yes** |
| `echo "$&varname"` | stdout | **Yes** |

The `$&varname` syntax is ngspice's **inline variable expansion** — it substitutes the
numeric value of a `let` variable into the echo string before sending it to stdout.
Because it goes through `echo`, it is always captured in the log.

### General pattern

```spice
.control
op

* Step 1: assign device parameters to named scalars with let
let vgs = @m.xDUT.xM1.msky130_fd_pr__nfet_01v8[vgs]
let id  = @m.xDUT.xM1.msky130_fd_pr__nfet_01v8[id]
let gm  = @m.xDUT.xM1.msky130_fd_pr__nfet_01v8[gm]
let gds = @m.xDUT.xM1.msky130_fd_pr__nfet_01v8[gds]
let vth = @m.xDUT.xM1.msky130_fd_pr__nfet_01v8[vth]

* Step 2: compute derived quantities
let vov = vgs - vth
let rds = 1 / gds

* Step 3: print to log using $& — goes to stdout, captured by cicsim
echo "  VGS  = $&vgs  V"
echo "  ID   = $&id   A"
echo "  gm   = $&gm   S"
echo "  Vov  = $&vov  V"
echo "  rds  = $&rds  Ohm"

* Step 4: conditional verdict (if/else also captured via echo)
let margin = vds - vov
if margin > 0
    echo "  --> SATURATION"
else
    echo "  --> TRIODE"
end

.endc
```

### Device parameter tokens (ngspice BSIM4)

| Token | Meaning |
|-------|---------|
| `[id]` | Drain current (A) |
| `[vgs]` | VGS for NMOS; VSG for PMOS (positive) |
| `[vds]` | VDS for NMOS; VSD for PMOS (positive) |
| `[vth]` | Threshold voltage (positive for both) |
| `[gm]` | Transconductance (S) |
| `[gds]` | Output conductance (S) |
| `[cgs]` | Gate-source capacitance (F) |
| `[cgd]` | Gate-drain capacitance (F) |

> **PMOS note:** ngspice BSIM4 always returns `vgs`, `vds`, `vth` in NMOS-equivalent
> (source-referenced, positive) coordinates for PMOS. The saturation condition is
> therefore identical: `VDS - Vov > 0` for both NMOS and PMOS.

### Other device types

```spice
* Resistor current
echo "  IR1 = $&i(vr_sense)  A"

* Voltage source current
let ivdd = -i(vdd)       * negative because current flows into + terminal
echo "  IVDD = $&ivdd  A"

* Node voltage (no let needed)
echo "  VOUT = $&v(vout)  V"

* Arithmetic in echo (compute inline)
let av = gm / gds
echo "  gm/gds = $&av"
```

### Why print fails with cicsim

cicsim launches ngspice as a subprocess and pipes its **stdout** to the `.log` file.
The `print` command writes to ngspice's internal display handler which goes to a
different file descriptor (not captured). `echo` always writes to stdout, so `$&var`
inside `echo` is the reliable way to get any computed value into the log.
