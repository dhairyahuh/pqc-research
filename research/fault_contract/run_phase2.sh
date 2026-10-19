#!/usr/bin/env bash
# run_phase2.sh — reproducible driver for the Phase 2 logical-value memory-fault arm.
# Builds the v1 campaign, runs pilot + confirmatory, checks reproducibility, runs the
# matched-baseline comparison + stats, and writes a provenance manifest. Additive only:
# writes to research/results/phase2_mem_logical_v1/; never touches historical files.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/liboqs/lib:${DYLD_LIBRARY_PATH:-}
OUT="research/results/phase2_mem_logical_v1"; mkdir -p "$OUT"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/p2.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/mem_campaign"
HIST="tfib_experiments/phase2_step2c_trial_results.csv"
INC="-Ialgorithms/source_ref/mlkem/include -Itfib_implementation -Itfib_experiments -Itfib_experiments/phase11_oracle -Iresearch/fault_contract -I/opt/homebrew/opt/liboqs/include"
OBJS="bin/obj/mlkem768_inst.o tfib_implementation/libtfib.a tfib_experiments/phase11_oracle/libindependent_oracle.a"
rc=0

echo "[1 build]"
clang -O3 -std=c11 -Wall -Wextra $INC research/fault_contract/mem_campaign.c $OBJS \
      -L/opt/homebrew/opt/liboqs/lib -loqs -o "$BIN" 2>"$TMP/build.log" || { grep -v xcrun_db "$TMP/build.log"; echo BUILD_FAIL; exit 10; }

echo "[2 pilot (5/suite)]";        "$BIN" "$OUT/pilot.jsonl" --pilot 5 || rc=1
echo "[3 confirmatory (50/suite)]"; "$BIN" "$OUT/raw.jsonl"            || rc=1
echo "[4 reproducibility]";         "$BIN" "$TMP/raw2.jsonl" >/dev/null || rc=1
H1=$(shasum -a256 "$OUT/raw.jsonl" | awk '{print $1}')
H2=$(shasum -a256 "$TMP/raw2.jsonl" | awk '{print $1}')
[ "$H1" = "$H2" ] && echo "  G5 reproducible: PASS ($H1)" || { echo "  G5 FAIL"; rc=1; }

echo "[5 compare + stats]"
python3 research/fault_contract/compare_and_stats.py "$OUT/raw.jsonl" "$HIST" "$OUT/comparison_stats.md" || rc=1

echo "[6 manifest]"
{
  echo "{"
  echo "  \"phase\": \"2-mem-logical-v1\","
  echo "  \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"platform\": \"$(uname -smr)\","
  echo "  \"clang\": \"$(clang --version 2>/dev/null | head -1 | tr -d '\"')\","
  echo "  \"liboqs\": \"$(ls /opt/homebrew/lib/liboqs.*.dylib 2>/dev/null | head -1)\","
  echo "  \"git_branch\": \"$(git rev-parse --abbrev-ref HEAD 2>/dev/null)\","
  echo "  \"git_head\": \"$(git rev-parse HEAD 2>/dev/null)\","
  echo "  \"working_tree_dirty\": $( [ -n "$(git status --porcelain 2>/dev/null)" ] && echo true || echo false ),"
  echo "  \"build_flags\": \"-O3 -std=c11 -Wall -Wextra\","
  echo "  \"seed_base_magic\": \"0x1337C0DE\","
  echo "  \"n_per_suite\": 50, \"n_total\": 900,"
  echo "  \"inputs\": {"
  for f in research/fault_contract/mem_campaign.c research/fault_contract/fault_contract.h \
           bin/obj/mlkem768_inst.o tfib_implementation/libtfib.a \
           tfib_experiments/phase11_oracle/libindependent_oracle.a tfib_experiments/campaign_prf.h "$HIST"; do
    echo "    \"$f\": \"$(shasum -a256 "$f" 2>/dev/null | awk '{print $1}')\","
  done | sed '$ s/,$//'
  echo "  },"
  echo "  \"outputs\": {"
  echo "    \"raw.jsonl\": \"$H1\","
  echo "    \"comparison_stats.md\": \"$(shasum -a256 "$OUT/comparison_stats.md" | awk '{print $1}')\""
  echo "  }"
  echo "}"
} > "$OUT/manifest.json"
cat "$OUT/manifest.json"

echo
[ $rc -eq 0 ] && echo "PHASE 2 DRIVER: PASS" || echo "PHASE 2 DRIVER: FAIL"
exit $rc
