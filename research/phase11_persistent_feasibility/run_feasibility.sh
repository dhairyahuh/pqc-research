#!/usr/bin/env bash
# run_feasibility.sh — build & run the ISOLATED persistent-storage feasibility prototype.
# Research-only; does NOT touch mlkem_native, campaigns, raw data, or manifests. Writes
# RESULTS.csv in this directory. Build artifacts go to a temp dir.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/fc11.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT
flt(){ grep -v xcrun_db || true; }
echo "[build] separate-TU reader + prototype (-O2)"
clang -O2 -c "$HERE/reader.c" -o "$TMP/reader.o" 2>"$TMP/e1"; flt <"$TMP/e1" >&2
clang -O2 "$HERE/proto.c" "$TMP/reader.o" -o "$TMP/proto" 2>"$TMP/e2"; flt <"$TMP/e2" >&2
echo "[section check] table placement (expect __DATA_CONST,__fc_tbl)"
nm -m "$TMP/proto" 2>/dev/null | grep -E "_table$" || true
echo "[run]"
"$TMP/proto" "$HERE/RESULTS.csv"; rc=$?
echo "exit=$rc"
exit $rc
