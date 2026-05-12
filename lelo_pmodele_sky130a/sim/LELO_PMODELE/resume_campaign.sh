#!/bin/bash
#
# PMOS Full Characterization Campaign (restart from scratch)
# W=1..80, L=0.8/0.9/1.0, corners=tt/ss/ff, VSB=0
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

mkdir -p characterize_2d_csvs
LOG_FILE="characterize_2d_csvs/campaign_full.log"
echo "" >> $LOG_FILE
echo "$(date): PMOS characterization campaign start" | tee -a $LOG_FILE

for VSB in 0.0 0.3 0.6 0.9; do
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

echo "$(date): PMOS campaign completed" | tee -a $LOG_FILE
