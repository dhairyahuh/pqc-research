# Phase 15D Changelog: Oracle Correction and Pilot Harness Hardening

**Date:** 2026-10-11  
**Author:** Skeptical Cryptographic Implementation Engineer  
**Context:** Phase 15D Oracle Correction and Harness Hardening (Phase 15C Audit Remediation)  
**Git Branch:** `space-resilience-framework`  

---

## 1. Summary of Actions Taken

This changelog documents all engineering actions taken during Phase 15D to resolve the defects identified in the Phase 15C Independent Audit:

* **Artifact Preservation & Backups:**
  - Created backup: `research/phase14_persistent_arm_design/pilot_runner.c.phase15b_bak` before applying code edits.
  - Preserved all historical reports, ledgers, and raw artifacts from Phases 15A, 15B, and 15C without modification.
  - Preserved all 7 pre-existing tracked repository modifications without staging or committing.
* **Independent Oracle Integration:**
  - Implemented a clean, self-contained FIPS 202 Keccak-f[1600] / SHAKE256 implementation directly inside `pilot_runner.c`.
  - Added preflight oracle self-test verifying $\text{SHAKE256}(\text{""}, 32)$ against NIST FIPS 202 KAT.
  - Implemented dynamic derivation of FIPS 203 implicit rejection key $\bar{K} = J(z \parallel c, 32) = \text{SHAKE256}(z \parallel c, 32)$ from reference vector inputs ($32 + 1088 = 1120$ bytes).
  - Replaced the inequality check (`ss_out != test_vector_ss`) with a strict four-way endpoint classifier (`EXPECTED_OUTPUT`, `REJECTION`, `DIFFERENT_OUTPUT`, `NO_OUTPUT`).
* **Memory Cleanup & Safety Hardening:**
  - Refactored `pilot_runner.c` to route every mutation and sham execution through a single structured 6-step cleanup block (restore entry $\rightarrow$ verify value $\rightarrow$ reprotect RO $\rightarrow$ verify RO via `vm_region_64` $\rightarrow$ verify canary padding $\rightarrow$ baseline decapsulation recheck).
  - Ensured that partial failures do not skip restoration; cleanup executes unconditionally.
  - Implemented emergency abort logic terminating the runner immediately if restoration or reprotection fails.
  - Installed `sigaction` signal handlers for `SIGBUS` and `SIGSEGV` to intercept traps cleanly.
* **Target Bounds Checks:**
  - Enforced `0 <= target_idx < 128` and element bit-width validation failing closed before any address calculation or memory unprotection.
* **Claims & Technical Errata:**
  - Documented formal errata correcting the obsolete Kyber Round 3 formula to FIPS 203 Section 6.3 Algorithm 17.
  - Formally retracted the overstated claim regarding Fujisaki-Okamoto key leakage prevention.
  - Corrected cleanup guarantee claims.
* **Read-Only Verification:**
  - Compiled `bin/pilot_runner` with `clang -O3 -Wall -Wextra -std=c11` (zero warnings).
  - Executed read-only oracle test (`./bin/pilot_runner --check-oracle` -> PASS).
  - Verified baseline KAT suite (`./bin/test_fips_kats_research` -> PASS).

---

## 2. Modified and Created Files

### Created Files:
1. `research/phase14_persistent_arm_design/pilot_runner.c.phase15b_bak`:
   Byte-for-byte backup of the original Phase 15B pilot runner.
2. `research/phase14_persistent_arm_design/PHASE15D_REPORT.md`:
   Technical correction report covering errata, hardened architecture, test evidence, artifact hashes, and untested behaviors.
3. `research/phase14_persistent_arm_design/PHASE15D_CHANGELOG.md`:
   This changelog document.

### Modified Files:
1. `research/phase14_persistent_arm_design/pilot_runner.c`:
   Updated with independent FIPS 202 SHAKE256 engine, dynamic FIPS 203 rejection oracle, 4-way endpoint classifier, 6-step structured cleanup path, live VM verification, target bounds checks, and signal trapping.
2. `bin/pilot_runner`:
   Recompiled research binary reflecting the hardened runner code.

---

## 3. Verification Commands Executed

```bash
# 1. Compilation
clang -O3 -Wall -Wextra -std=c11 \
  -I . -I algorithms/source_ref/mlkem \
  research/phase14_persistent_arm_design/pilot_runner.c \
  bin/obj/mlkem768_persistent_reloc.o \
  -o bin/pilot_runner

# 2. Read-only Oracle Self-Test
./bin/pilot_runner --check-oracle

# 3. Cryptographic Baseline KAT Suite
./bin/test_fips_kats_research
```
All commands exited with code 0 and 100% pass rates. Zero live fault-injection trials or mutation experiments were executed.
