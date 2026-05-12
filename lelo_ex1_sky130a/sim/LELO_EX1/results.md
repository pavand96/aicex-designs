# Parametric Sweep Results - LELO_EX1

## Overview

**Parametric Sweep Configuration:**
- **Total Combinations:** 60
- **Saturated Designs:** 12
- **Success Rate:** 20%
- **Technology:** SKY130A PDK
- **Simulation:** ngspice with AC analysis (1 Hz - 10 GHz, 1000 pts/decade)

**Parameters Swept:**
- **W (Width):** 20 µm, 40 µm, 60 µm
- **R (Resistance):** 5 kΩ, 10 kΩ, 15 kΩ, 20 kΩ
- **VIN (Input Voltage):** 0.5 V, 0.6 V, 0.7 V, 0.8 V, 0.9 V

**Saturation Criterion:** 0.3 V < Vout < 1.5 V (VDD = 1.8 V)

---

## Top Performers

### 🥇 Highest Peak Gain
**W=40 µm, R=10 kΩ, VIN=0.7 V**
- Peak Gain: **23.47 dB**
- F_3dB: 603 MHz
- GBW: 8.99 GHz
- Vout: 0.570 V (saturated)

### 🥈 Best GBW (Highest Bandwidth)
**W=20 µm, R=5 kΩ, VIN=0.9 V**
- Peak Gain: 12.43 dB
- F_3dB: 3.03 GHz
- GBW: **12.7 GHz**
- Vout: 0.315 V (saturated)

### 🥉 Best Balanced Performance
**W=20 µm, R=10 kΩ, VIN=0.7 V**
- Peak Gain: 18.09 dB
- F_3dB: 1.38 GHz
- GBW: **11.1 GHz** (high bandwidth)
- Vout: 1.19 V (saturated)

---

## All Saturated Designs

| W (µm) | R (kΩ) | VIN (V) | Vout (V) | Idd (mA) | Gain (dB) | F_3dB (MHz) | GBW (GHz) |
|--------|--------|---------|----------|----------|-----------|-------------|-----------|
| 20 | 5 | 0.9 | 0.315 | 0.990 | 12.43 | 3033 | 12.7 |
| 20 | 10 | 0.7 | 1.194 | 0.061 | 18.09 | 1377 | 11.1 |
| 20 | 15 | 0.7 | 0.908 | 0.059 | 21.25 | 843 | 9.74 |
| 20 | 20 | 0.7 | 0.637 | 0.058 | 23.24 | 607 | 8.81 |
| 40 | 5 | 0.7 | 1.156 | 0.129 | 18.49 | 1355 | 11.4 |
| **40** | **10** | **0.7** | **0.570** | **0.123** | **23.47** | **603** | **8.99** |
| 40 | 15 | 0.6 | 1.440 | 0.024 | 16.97 | 482 | 3.40 |
| 40 | 20 | 0.6 | 1.314 | 0.024 | 19.30 | 340 | 3.13 |
| 60 | 5 | 0.7 | 0.835 | 0.193 | 21.70 | 830 | 10.1 |
| 60 | 10 | 0.6 | 1.431 | 0.037 | 17.15 | 480 | 3.45 |
| 60 | 15 | 0.6 | 1.238 | 0.037 | 20.40 | 296 | 3.10 |
| 60 | 20 | 0.6 | 1.050 | 0.038 | 22.61 | 214 | 2.90 |

---

## Gain vs. Bandwidth Tradeoff

The results clearly demonstrate the fundamental gain-bandwidth tradeoff in amplifier design:

- **High Gain, Low Bandwidth:** R=20 kΩ designs achieve up to 23.24 dB but with limited bandwidth (607-214 MHz)
- **Low Gain, High Bandwidth:** R=5 kΩ designs achieve best GBW (12.7 GHz) with moderate gain (12-21 dB)
- **Optimal Balance:** W=20 µm, R=10 kΩ provides 18 dB gain with 11.1 GHz GBW

---

## Design Insights

### Saturation Behavior
- Only 20% of parameter combinations achieve saturation (0.3-1.5 V output range)
- Saturation most achieved at **VIN=0.6-0.7 V** (mid-range values)
- Extreme VIN values (0.5 V, 0.8-0.9 V) rarely saturate except with specific R values

### Width Dependency
- **W=20 µm:** Smallest width, best GBW (narrow channel = high frequency performance)
- **W=40 µm:** Sweet spot for peak gain (23.47 dB best overall)
- **W=60 µm:** Larger width reduces speed, lower GBW values at high R

### Resistance Dependency
- **R=5 kΩ:** Lowest impedance, highest bandwidth, lower gain, best GBW
- **R=10 kΩ:** Best all-around performance, ideal gain-bandwidth balance
- **R=15-20 kΩ:** Higher impedance, higher gain, significantly reduced bandwidth
- **R=20 kΩ:** Maximum gain (23.24 dB), minimum bandwidth (214 MHz)

### Frequency Characteristics
- **Peak Gain Frequency:** Predominantly at DC (1 Hz) for most designs
- **3dB Bandwidth:** Extends from 214 MHz to 3.03 GHz across all saturated designs
- **GBW Product:** Ranges from 2.90 GHz to 12.7 GHz

---

## Recommendations

**For Maximum Gain:** Use W=20 µm, R=20 kΩ, VIN=0.7 V (23.24 dB)

**For Maximum Bandwidth:** Use W=20 µm, R=5 kΩ, VIN=0.9 V (12.7 GHz GBW)

**For Best Balance (Recommended):** Use W=20 µm, R=10 kΩ, VIN=0.7 V 
- Gain: 18.09 dB (reasonable for amplifier)
- GBW: 11.1 GHz (excellent bandwidth)
- Idd: 0.061 mA (power-efficient)

**For High Current Tolerance:** Use W=60 µm configurations (highest Idd designs)

---

## Notes

- All simulations performed with 1000 points/decade AC sweep from 1 Hz to 10 GHz
- Power supply: VDD = 1.8 V
- Gain calculated from AC frequency response (complex impedance magnitude in dB)
- F_3dB determined from -3 dB point relative to peak gain (not DC gain)
- GBW = Peak Gain × F_3dB (in linear units)

---

*Generated from sweep_results_make.csv on April 11, 2026*
