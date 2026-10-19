#!/usr/bin/env bash
# run_phase4_pilot.sh — Gate 4 PILOT driver (deterministic). Builds the combined
# coordinator, runs a 20-seed pilot, checks reproducibility, runs the FROZEN analysis
# (labelled PILOT, descriptive), and writes a manifest. Does NOT run the confirmatory
# campaign (that is gated on design-review sign-off). Additive; no historical file touched.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/liboqs/lib:${DYLD_LIBRARY_PATH:-}
OUT="research/results/phase4_combined_v1"; mkdir -p "$OUT"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/p4.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/combined"
INC="-Ialgorithms/source_ref/mlkem/include -Itfib_implementation -Itfib_experiments -Itfib_experiments/phase11_oracle -I/opt/homebrew/opt/liboqs/include"
OBJS="bin/obj/mlkem768_inst.o tfib_implementation/libtfib.a tfib_experiments/phase11_oracle/libindependent_oracle.a"
rc=0

echo "[1 build -Werror]"
clang -O3 -std=c11 -Wall -Wextra -Werror $INC research/combined_harness/combined_campaign.c $OBJS \
      -L/opt/homebrew/opt/liboqs/lib -loqs -o "$BIN" 2>"$TMP/b.log" || { grep -v xcrun_db "$TMP/b.log"; echo BUILD_FAIL; exit 10; }
echo "[2 pilot (20 seeds x4)]"; "$BIN" "$OUT/pilot.jsonl" --pilot 20 || rc=1
echo "[3 reproducibility]"; "$BIN" "$TMP/p2.jsonl" --pilot 20 >/dev/null || rc=1
H1=$(shasum -a256 "$OUT/pilot.jsonl" | awk '{print $1}'); H2=$(shasum -a256 "$TMP/p2.jsonl" | awk '{print $1}')
[ "$H1" = "$H2" ] && echo "  reproducible: PASS ($H1)" || { echo "  reproducible: FAIL"; rc=1; }
echo "[4 frozen analysis on PILOT (descriptive)]"
python3 research/combined_harness/combined_stats.py "$OUT/pilot.jsonl" "$OUT/pilot_stats.md" --label PILOT --B 10000 || rc=1
echo "[5 manifest]"
DIRTY=false; [ -n "$(git status --porcelain 2>/dev/null)" ] && DIRTY=true
{
  echo "{"
  echo "  \"phase\": \"4-combined-v1-PILOT\","
  echo "  \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"platform\": \"$(uname -smr)\","
  echo "  \"clang\": \"$(clang --version 2>/dev/null | head -1 | tr -d '\"')\","
  echo "  \"liboqs\": \"$(ls /opt/homebrew/lib/liboqs.*.dylib 2>/dev/null | head -1)\","
  echo "  \"git_head\": \"$(git rev-parse HEAD 2>/dev/null)\", \"working_tree_dirty\": $DIRTY,"
  echo "  \"combined_schema_version\": 1, \"retry_max\": 2, \"n_pilot_seeds\": 20,"
  echo "  \"confirmatory_run\": false,"
  echo "  \"inputs\": {"
  for f in research/combined_harness/combined_campaign.c research/combined_harness/combined_stats.py \
           research/PHASE4_PREREGISTRATION.md bin/obj/mlkem768_inst.o; do
    echo "    \"$f\": \"$(shasum -a256 "$f" | awk '{print $1}')\","
  done | sed '$ s/,$//'
  echo "  },"
  echo "  \"outputs\": { \"pilot.jsonl\": \"$H1\", \"pilot_stats.md\": \"$(shasum -a256 "$OUT/pilot_stats.md" | awk '{print $1}')\" }"
  echo "}"
} > "$OUT/manifest_pilot.json"
cat "$OUT/manifest_pilot.json"
echo; [ $rc -eq 0 ] && echo "PHASE 4 PILOT: PASS (confirmatory NOT run — awaiting design-review sign-off)" || echo "PHASE 4 PILOT: FAIL"
exit $rc
