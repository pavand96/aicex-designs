#!/bin/bash
#
# Resume NMOS Characterization Campaign
# Picks up where campaign_full left off:
#   - ff VSB=0 L=1.0: W=52..80
#   - Then all VSB=0.3, 0.6, 0.9 for tt/ss/ff
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

LOG_FILE="characterize_2d_csvs/campaign_full.log"
echo "" >> $LOG_FILE
echo "$(date): RESUME - continuing campaign after system restart" | tee -a $LOG_FILE

# ============================================================
# PART 1: Complete ff VSB=0 L=1.0 (W=52..80)
# ============================================================
echo "--- RESUME: ff VSB=0.0 L=1.0 W=52..80 ---" | tee -a $LOG_FILE
VSB=0.0
CORNER=ff
L=1.0
for W in $(seq 52 80); do
    echo "[$(date +%H:%M:%S)] W=$W L=$L C=$CORNER VSB=$VSB" | tee -a $LOG_FILE
    if python3 characterize_measured_corner.py $W $L $CORNER $VSB >> $LOG_FILE 2>&1; then
        echo "  OK" | tee -a $LOG_FILE
    else
        echo "  FAIL" | tee -a $LOG_FILE
    fi
done

# ============================================================
# PART 2: All VSB > 0 combinations
# ============================================================
for VSB in 0.3 0.6 0.9; do
    for CORNER in tt ss ff; do
        echo "--- VSB=$VSB CORNER=$CORNER ---" | tee -a $LOG_FILE
        for L in 0.8 0.9 1.0; do
            for W in $(seq 1 80); do
                echo "[$(date +%H:%M:%S)] W=$W L=$L C=$CORNER VSB=$VSB" | tee -a $LOG_FILE
                if python3 characterize_measured_corner.py $W $L $CORNER $VSB >> $LOG_FILE 2>&1; then
                    echo "  OK" | tee -a $LOG_FILE
                else
                    echo "  FAIL" | tee -a $LOG_FILE
                fi
            done
        done
    done
done

echo "$(date): RESUME campaign completed" | tee -a $LOG_FILE
