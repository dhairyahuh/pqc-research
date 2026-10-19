#!/usr/bin/env bash
# run_phase1_tests.sh — build & run the Phase 1 fault-contract verification suite.
# Records exact commands and exit codes. No repository state is modified; all
# build artifacts go to a temp dir. Re-runnable and deterministic.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$(mktemp -d "${TMPDIR:-/tmp}/fc_build.XXXXXX")"
trap 'rm -rf "$BUILD"' EXIT
CC="${CC:-clang}"
STRICT="-std=c11 -Wall -Wextra -Werror -Wconversion -Wshadow"
SAN="-fsanitize=address,undefined -fno-omit-frame-pointer -g"
# strip the cosmetic macOS sandbox xcrun cache warning (no process substitution:
# /dev/fd is blocked under the sandbox, so compile to a log file and filter it)
showerr() { grep -v "xcrun_db" "$1" 1>&2 || true; }
rc_overall=0
say() { printf '\n>>> %s\n' "$*"; }

say "[1/4] Unit + negative tests (strict warnings + ASAN/UBSAN)"
echo "CMD: $CC $STRICT $SAN test_fault_contract.c -o \$B/t"
if $CC $STRICT $SAN "$HERE/test_fault_contract.c" -o "$BUILD/t" 2>"$BUILD/e1"; then
    showerr "$BUILD/e1"; "$BUILD/t"; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || rc_overall=1
else
    showerr "$BUILD/e1"; echo "COMPILE FAILED"; rc_overall=1
fi

say "[2/4] Hook-gate: clean build must COMPILE (hooks OFF)"
echo "CMD: $CC $STRICT test_hook_gate.c -o \$B/g"
if $CC $STRICT "$HERE/test_hook_gate.c" -o "$BUILD/g" 2>"$BUILD/e2"; then
    showerr "$BUILD/e2"; "$BUILD/g"; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || rc_overall=1
else
    showerr "$BUILD/e2"; echo "COMPILE FAILED (unexpected)"; rc_overall=1
fi

say "[3/4] Hook-gate: build WITH -DMLKEM_RESEARCH_FAULT_HOOKS must FAIL to compile"
echo "CMD: $CC $STRICT -DMLKEM_RESEARCH_FAULT_HOOKS test_hook_gate.c (expect error)"
if $CC $STRICT -DMLKEM_RESEARCH_FAULT_HOOKS "$HERE/test_hook_gate.c" -o "$BUILD/gneg" 2>/dev/null; then
    echo "FAIL: gate did NOT trip when hooks were defined"; rc_overall=1
else
    echo "ok: gate correctly rejected a hooks-enabled production build"
fi

say "[4/4] Robustness fuzz: validate/classify/ledger on malformed input (ASAN/UBSAN)"
# Prefer coverage-guided libFuzzer; fall back to the deterministic standalone
# driver when the libFuzzer runtime is absent (Command-Line-Tools-only clang).
if $CC -std=c11 -g -O1 -DFC_LIBFUZZER -fsanitize=fuzzer,address,undefined \
       "$HERE/fuzz_fault_contract.c" -o "$BUILD/fz" 2>"$BUILD/e4"; then
    echo "mode: libFuzzer (-runs=200000)"
    "$BUILD/fz" -runs=200000 -max_total_time=20 -print_final_stats=1 >/dev/null 2>"$BUILD/fz.log"; rc=$?
    echo "exit=$rc"; tail -2 "$BUILD/fz.log" 2>/dev/null
    [ $rc -eq 0 ] || { echo "FUZZER FOUND A CRASH"; rc_overall=1; }
else
    echo "note: libFuzzer runtime unavailable here; using deterministic standalone driver"
    if $CC -std=c11 -g -O1 -fsanitize=address,undefined \
           "$HERE/fuzz_fault_contract.c" -o "$BUILD/fz" 2>"$BUILD/e4b"; then
        "$BUILD/fz" 500000; rc=$?; echo "exit=$rc"
        [ $rc -eq 0 ] || { echo "ROBUSTNESS DRIVER CRASHED (ASAN/UBSAN)"; rc_overall=1; }
    else
        showerr "$BUILD/e4b"; echo "ROBUSTNESS BUILD FAILED"; rc_overall=1
    fi
fi

say "PHASE 1 SUITE: $([ $rc_overall -eq 0 ] && echo PASS || echo FAIL) (overall exit=$rc_overall)"
exit $rc_overall
