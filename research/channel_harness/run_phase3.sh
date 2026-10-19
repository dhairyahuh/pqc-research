#!/usr/bin/env bash
# run_phase3.sh — reproducible driver for the Phase 3 channel-fault arm.
# Gate 3 tests -> pilot -> confirmatory -> reproducibility -> stats -> manifest.
# Additive only; writes research/results/phase3_channel_v1/; no historical file touched.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
OUT="research/results/phase3_channel_v1"; mkdir -p "$OUT"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/p3.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT
PY=python3; CAMP=research/channel_harness/channel_campaign.py
rc=0

echo "[1 gate-3 tests]"; $PY research/channel_harness/test_channel_contract.py || { echo "TESTS FAIL"; exit 5; }
echo "[2 pilot (5/suite)]";        $PY "$CAMP" "$OUT/pilot.jsonl" --pilot 5 || rc=1
echo "[3 confirmatory (50/suite)]"; $PY "$CAMP" "$OUT/raw.jsonl"            || rc=1
echo "[4 reproducibility]";         $PY "$CAMP" "$TMP/raw2.jsonl" >/dev/null || rc=1
H1=$(shasum -a256 "$OUT/raw.jsonl" | awk '{print $1}')
H2=$(shasum -a256 "$TMP/raw2.jsonl" | awk '{print $1}')
[ "$H1" = "$H2" ] && echo "  reproducible: PASS ($H1)" || { echo "  reproducible: FAIL"; rc=1; }
echo "[5 stats]"; $PY research/channel_harness/channel_stats.py "$OUT/raw.jsonl" "$OUT/stats.md" || rc=1

echo "[6 manifest]"
DIRTY=false; [ -n "$(git status --porcelain 2>/dev/null)" ] && DIRTY=true
{
  echo "{"
  echo "  \"phase\": \"3-channel-v1\","
  echo "  \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"platform\": \"$(uname -smr)\","
  echo "  \"python\": \"$($PY --version 2>&1 | tr -d '\"')\","
  echo "  \"liboqs\": \"$(ls /opt/homebrew/lib/liboqs.*.dylib 2>/dev/null | head -1)\","
  echo "  \"git_branch\": \"$(git rev-parse --abbrev-ref HEAD 2>/dev/null)\","
  echo "  \"git_head\": \"$(git rev-parse HEAD 2>/dev/null)\","
  echo "  \"working_tree_dirty\": $DIRTY,"
  echo "  \"protocol_schema_version\": 1, \"retry_max\": 2, \"n_per_suite\": 50,"
  echo "  \"inputs\": {"
  for f in research/channel_harness/channel_campaign.py research/channel_harness/channel_stats.py \
           research/PROTOCOL_FAULT_MODEL_SPEC.md; do
    echo "    \"$f\": \"$(shasum -a256 "$f" | awk '{print $1}')\","
  done | sed '$ s/,$//'
  echo "  },"
  echo "  \"outputs\": { \"raw.jsonl\": \"$H1\", \"stats.md\": \"$(shasum -a256 "$OUT/stats.md" | awk '{print $1}')\" }"
  echo "}"
} > "$OUT/manifest.json"
cat "$OUT/manifest.json"
echo; [ $rc -eq 0 ] && echo "PHASE 3 DRIVER: PASS" || echo "PHASE 3 DRIVER: FAIL"
exit $rc
