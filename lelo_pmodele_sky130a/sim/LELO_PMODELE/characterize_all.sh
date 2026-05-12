#!/bin/bash
#
# PMOS Characterization Campaign - Generate CSV files for all W/L/Corner combinations
# Usage: ./characterize_all.sh
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Define device parameter ranges
WIDTHS=(5 10 15 20 25 30 35 40 45 50 80)      # µm
LENGTHS=(0.8 0.9 1.0)                          # µm
CORNERS=(tt ss ff)                             # Process corners

echo "================================================================================="
echo "PMOS CHARACTERIZATION CAMPAIGN - All W/L/Corner Combinations"
echo "================================================================================="
echo "Widths:  ${WIDTHS[@]} µm"
echo "Lengths: ${LENGTHS[@]} µm"
echo "Corners: ${CORNERS[@]}"
echo ""

# Create output directory for CSVs
mkdir -p characterize_2d_csvs
LOG_FILE="characterize_2d_csvs/campaign.log"

echo "$(date): Starting PMOS characterization campaign" | tee $LOG_FILE
echo "" | tee -a $LOG_FILE

TOTAL=0
COMPLETED=0
FAILED=0

# Pre-compute total count
for W in "${WIDTHS[@]}"; do
    for L in "${LENGTHS[@]}"; do
        for CORNER in "${CORNERS[@]}"; do
            TOTAL=$((TOTAL + 1))
        done
    done
done

echo "Total combinations to run: $TOTAL" | tee -a $LOG_FILE
echo "Estimated time: ~$((TOTAL / 2)) minutes" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Main loop - iterate through corners first
for CORNER in "${CORNERS[@]}"; do
    echo "================================================================================" | tee -a $LOG_FILE
    echo "CORNER: $CORNER" | tee -a $LOG_FILE
    echo "================================================================================" | tee -a $LOG_FILE
    
    CSV_FILE="characterize_2d_csvs/characterize_2d_${CORNER}.csv"

    # Clear CSV for this corner (start fresh)
    rm -f "$CSV_FILE"

    for L in "${LENGTHS[@]}"; do
        for W in "${WIDTHS[@]}"; do
            COMPLETED=$((COMPLETED + 1))
            PERCENT=$((COMPLETED * 100 / TOTAL))

            echo "[${PERCENT}%] W=${W}um, L=${L}um, corner=${CORNER}" | tee -a $LOG_FILE

            # Run characterization with corner
            if python3 characterize_measured_corner.py $W $L $CORNER >> "$LOG_FILE" 2>&1; then
                # Append to corner-specific CSV
                if [ ! -f "$CSV_FILE" ]; then
                    head -1 characterize_2d_${CORNER}.csv > "$CSV_FILE"
                fi
                tail -n +2 characterize_2d_${CORNER}.csv | grep "^[^,]*,${W}" >> "$CSV_FILE" 2>/dev/null || true

                echo "  Success" | tee -a $LOG_FILE
            else
                echo "  FAILED" | tee -a $LOG_FILE
                FAILED=$((FAILED + 1))
            fi
        done
    done

    # Verify corner CSV
    if [ -f "$CSV_FILE" ]; then
        LINES=$(wc -l < "$CSV_FILE")
        echo "Corner ${CORNER} CSV: $LINES rows" | tee -a $LOG_FILE
    fi
    echo "" | tee -a $LOG_FILE
done

echo "================================================================================" | tee -a $LOG_FILE
echo "CAMPAIGN SUMMARY" | tee -a $LOG_FILE
echo "================================================================================" | tee -a $LOG_FILE
echo "Total combinations: $TOTAL" | tee -a $LOG_FILE
echo "Completed: $COMPLETED" | tee -a $LOG_FILE
echo "Failed: $FAILED" | tee -a $LOG_FILE
echo "Success rate: $((100 - FAILED*100/TOTAL))%" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# List generated CSV files with stats
echo "Generated CSV files:" | tee -a $LOG_FILE
for CORNER in "${CORNERS[@]}"; do
    CSV_FILE="characterize_2d_csvs/characterize_2d_${CORNER}.csv"
    if [ -f "$CSV_FILE" ]; then
        ROWS=$(wc -l < "$CSV_FILE")
        SIZE=$(du -h "$CSV_FILE" | cut -f1)
        echo "  $CSV_FILE: $ROWS rows, $SIZE" | tee -a $LOG_FILE
    fi
done

echo "" | tee -a $LOG_FILE
echo "Campaign completed: $(date)" | tee -a $LOG_FILE
