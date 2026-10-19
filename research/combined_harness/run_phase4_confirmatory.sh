#!/usr/bin/env bash
# run_phase4_confirmatory.sh — Gate 5 CONFIRMATORY (500 seeds x4). Records frozen-input
# hashes BEFORE execution, builds, runs the paired campaign to raw.jsonl, checks
# reproducibility, runs the FROZEN analysis + joint sensitivity, writes a manifest.
# Additive only; no historical file touched; no protocol/analysis change after this point.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/liboqs/lib:${DYLD_LIBRARY_PATH:-}
OUT="research/results/phase4_combined_v1"; mkdir -p "$OUT"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/p4c.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/combined"
INC="-Ialgorithms/source_ref/mlkem/include -Itfib_implementation -Itfib_experiments -Itfib_experiments/phase11_oracle -I/opt/homebrew/opt/liboqs/include"
OBJS="bin/obj/mlkem768_inst.o tfib_implementation/libtfib.a tfib_experiments/phase11_oracle/libindependent_oracle.a"
rc=0
h(){ shasum -a256 "$1" | awk '{print $1}'; }

echo "[0 freeze: pre-execution input hashes]"
PRE=$(h research/PHASE4_PREREGISTRATION.md); AMD=$(h research/PHASE4_PREREGISTRATION_AMENDMENT_v2.md)
COORD=$(h research/combined_harness/combined_campaign.c); STATS=$(h research/combined_harness/combined_stats.py)
SENS=$(h research/combined_harness/combined_sensitivity.py); OBJ=$(h bin/obj/mlkem768_inst.o)
printf "  prereg_v1=%s\n  amendment_v2=%s\n  coordinator+F=%s\n  stats=%s\n  sensitivity=%s\n  mlkem768_inst.o=%s\n" \
  "$PRE" "$AMD" "$COORD" "$STATS" "$SENS" "$OBJ"

echo "[1 build -Werror]"
clang -O3 -std=c11 -Wall -Wextra -Werror $INC research/combined_harness/combined_campaign.c $OBJS \
      -L/opt/homebrew/opt/liboqs/lib -loqs -o "$BIN" 2>"$TMP/b.log" || { grep -v xcrun_db "$TMP/b.log"; echo BUILD_FAIL; exit 10; }

echo "[2 confirmatory: 500 seeds x4]"; "$BIN" "$OUT/raw.jsonl" || { echo "VALIDATION FAIL (ledger/inconclusive)"; rc=1; }
echo "[3 reproducibility]"; "$BIN" "$TMP/r2.jsonl" >/dev/null
H1=$(h "$OUT/raw.jsonl"); H2=$(h "$TMP/r2.jsonl")
[ "$H1" = "$H2" ] && echo "  reproducible: PASS ($H1)" || { echo "  reproducible: FAIL"; rc=1; }

echo "[4 frozen analysis (CONFIRMATORY)]"
python3 research/combined_harness/combined_stats.py "$OUT/raw.jsonl" "$OUT/confirmatory_stats.md" --label CONFIRMATORY --B 10000 || rc=1
echo "[5 joint sensitivity on confirmatory data]"
python3 research/combined_harness/combined_sensitivity.py "$OUT/raw.jsonl" --B 10000 | tee "$OUT/confirmatory_sensitivity.txt" >/dev/null || rc=1

echo "[6 manifest]"
DIRTY=false; [ -n "$(git status --porcelain 2>/dev/null)" ] && DIRTY=true
{
  echo "{"
  echo "  \"phase\": \"4-combined-v1-CONFIRMATORY\", \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"platform\": \"$(uname -smr)\", \"clang\": \"$(clang --version 2>/dev/null|head -1|tr -d '\"')\","
  echo "  \"liboqs\": \"$(ls /opt/homebrew/lib/liboqs.*.dylib 2>/dev/null|head -1)\","
  echo "  \"git_head\": \"$(git rev-parse HEAD 2>/dev/null)\", \"working_tree_dirty\": $DIRTY,"
  echo "  \"n_seeds\": 500, \"conditions\": 4, \"retry_max\": 2, \"combined_schema_version\": 1,"
  echo "  \"frozen_inputs\": {"
  echo "    \"PHASE4_PREREGISTRATION.md\": \"$PRE\", \"PHASE4_PREREGISTRATION_AMENDMENT_v2.md\": \"$AMD\","
  echo "    \"combined_campaign.c\": \"$COORD\", \"combined_stats.py\": \"$STATS\","
  echo "    \"combined_sensitivity.py\": \"$SENS\", \"mlkem768_inst.o\": \"$OBJ\""
  echo "  },"
  echo "  \"outputs\": { \"raw.jsonl\": \"$H1\", \"confirmatory_stats.md\": \"$(h "$OUT/confirmatory_stats.md")\","
  echo "    \"confirmatory_sensitivity.txt\": \"$(h "$OUT/confirmatory_sensitivity.txt")\" }"
  echo "}"
} > "$OUT/manifest_confirmatory.json"
cat "$OUT/manifest_confirmatory.json"
echo; [ $rc -eq 0 ] && echo "PHASE 4 CONFIRMATORY: PASS" || echo "PHASE 4 CONFIRMATORY: FAIL"
exit $rc
