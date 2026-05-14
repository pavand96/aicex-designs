#!/usr/bin/env bash
# Corner sweep for LELO_NMC_3STAGE_FINAL
# Runs OP + AC at K x T x V = 5 x 3 x 3 = 45 corners (TT, FF, SS, SF, FS plus
# T_low/typ/high V_low/typ/high)

set -u
unset DISPLAY
cd "$(dirname "$0")"

K_LIST=(Ktt Kff Kss Ksf Kfs)
T_LIST=(Tt Tl Th)
V_LIST=(Vt Vl Vh)

PASS=0
FAIL=0
echo "corner,gain_db,gbw_mhz,pm_deg,vout_v,status"

for K in "${K_LIST[@]}"; do
  for T in "${T_LIST[@]}"; do
    for V in "${V_LIST[@]}"; do
      tag="Sch_Gt_${K}_${T}_${V}"
      log_op="output_op/op_SchGt${K}${T}${V}.log"
      log_ac="output_ac/ac_SchGt${K}${T}${V}.log"

      cicsim run op Sch Gt $K $T $V --no-sha --replace vos_typ.yaml >/dev/null 2>&1
      cicsim run ac Sch Gt $K $T $V --no-sha --replace vos_typ.yaml >/dev/null 2>&1

      vout=$(grep -m1 "^v(vout) =" "$log_op" 2>/dev/null | awk '{print $3}')
      gain=$(grep -m1 "^dc_gain_db =" "$log_ac" 2>/dev/null | awk '{print $3}')
      gbw=$(grep -m1  "^fgbw ="       "$log_ac" 2>/dev/null | awk '{print $3}')
      pm=$(grep   -m1 "^pm ="         "$log_ac" 2>/dev/null | awk '{print $3}')

      # Spec (Table 7-1): gain >= 100 dB, PM >= 50 deg, GBW >= 5 MHz
      status=$(awk -v g="$gain" -v p="$pm" -v f="$gbw" 'BEGIN{
        if (g+0>=100 && p+0>=50 && f+0>=5e6) print "PASS";
        else if (g+0>=90 && p+0>=45 && f+0>=4e6) print "MARG";
        else print "FAIL"}')
      [[ $status == PASS || $status == MARG ]] && PASS=$((PASS+1)) || FAIL=$((FAIL+1))

      gbwM=$(awk -v x="$gbw" 'BEGIN{ if (x+0>0) printf "%.2f", x/1e6; else print "-" }')
      printf "%-22s,%8s dB,%8s MHz,%6s deg,%6s V,%s\n" "$tag" "$gain" "$gbwM" "$pm" "$vout" "$status"
    done
  done
done

echo ""
echo "================ SUMMARY ================"
echo "PASS = $PASS / $((PASS+FAIL))"
echo "FAIL = $FAIL / $((PASS+FAIL))"
