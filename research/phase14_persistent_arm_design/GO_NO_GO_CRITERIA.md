# Phase 14 — Persistent-Storage Fault Arm: Go / No-Go Decision Criteria

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Target:** Approval and Execution Gate for Proposed Phase 15 Pilot & Campaign  
**Scope:** Strict Formal Gate Conditions (Any Single Failure Triggers Immediate NO-GO)

---

## 1. Decision Matrix Overview

Approval for testing the persistent-storage fault arm requires passing four sequential, deterministic evaluation gates:

```
+-----------------------------------------------------------------------------+
| Gate 1: Binary Layout & Symbol Verification                                 |
|         Symbol in __DATA_CONST, 16KB padded, maxprot allows write,           |
|         zero co-located symbols, identical NTT instruction schedule          |
+-----------------------------------------------------------------------------+
                                       | Pass
                                       v
+-----------------------------------------------------------------------------+
| Gate 2: Memory Subsystem & Kernel Protection Check                          |
|         vm_protect toggles cleanly without SIGBUS or kernel traps           |
+-----------------------------------------------------------------------------+
                                       | Pass
                                       v
+-----------------------------------------------------------------------------+
| Gate 3: Cryptographic Baseline & Conformance Check                          |
|         100% of NIST FIPS 203 KAT vectors pass on research binary           |
+-----------------------------------------------------------------------------+
                                       | Pass
                                       v
+-----------------------------------------------------------------------------+
| Gate 4: Pilot Lifecycle & Hygiene Check                                     |
|         16/16 deterministic trials pass; zero cross-trial contamination     |
+-----------------------------------------------------------------------------+
                                       | Pass
                                       v
                         [ FULL CAMPAIGN AUTHORIZED ]
```

---

## 2. Gate 1: Binary Layout & Symbol Verification Gate

| Metric | Target Requirement | Evaluation Command | Failure Condition | Verdict on Failure |
|---|---|---|---|:---:|
| **Symbol Relocation** | Symbol `_mlk_zetas_page` is in `(__DATA_CONST,__zetas_page)` | `nm -m <obj> \| grep zetas` | Symbol in `(__TEXT,__const)` or missing | **HARD NO-GO** |
| **Linked Max Protection** | Segment `maxprot` permits write (`0x03` or `0x07`) | `otool -l <bin> \| grep -A 8 __DATA_CONST` | `maxprot == 0x01` (read-only) | **HARD NO-GO** |
| **Page Isolation** | Zero other symbols within `[page_addr, page_addr + 16384)` | `nm -n <bin> \| awk ...` | Any other symbol on the 16 KB page | **HARD NO-GO** |
| **Codegen Parity** | Instruction schedules in NTT match baseline identically | Disassembly diffing (`diff -u`) | Differing loop schedules, spills, or instructions | **HARD NO-GO** |
| **Production Invariance** | Unmodified build produces bit-for-bit identical object | `cmp bin/obj/mlkem768.o <clean_rebuild>` | Any differing bytes | **HARD NO-GO** |

---

## 3. Gate 2: Memory Subsystem & Kernel Protection Gate

| Metric | Target Requirement | Evaluation Command | Failure Condition | Verdict on Failure |
|---|---|---|---|:---:|
| **Mach VM Protection** | `vm_protect` returns `KERN_SUCCESS` (0) for RW and RO | Runtime assertion in harness | Returns `KERN_PROTECTION_FAILURE` or non-zero | **HARD NO-GO** |
| **Write Integrity** | Memory write completes without signal | Harness execution | Signal received (`SIGBUS`, `SIGSEGV`) | **HARD NO-GO** |
| **Read-back Fidelity** | Injected value read back equals `golden ^ mask` | Read-back assertion | Read-back mismatch | **HARD NO-GO** |
| **Collateral Isolation** | Surrounding 16,128-byte page padding unaltered | Byte comparison of `page_padding` | Any altered byte in padding | **HARD NO-GO** |

---

## 4. Gate 3: Cryptographic Baseline & Conformance Gate

| Metric | Target Requirement | Evaluation Command | Failure Condition | Verdict on Failure |
|---|---|---|---|:---:|
| **FIPS 203 Conformance** | 100% NIST FIPS 203 KAT vectors pass on research binary | `./bin/test_fips_kats` | Any KAT vector failure | **HARD NO-GO** |
| **Deterministic Reference Equivalence** | 1,000 clean test vectors match baseline bit-for-bit | Automated test runner | Output mismatch against baseline build | **HARD NO-GO** |
| **Timing & Clean Exit** | Baseline execution completes with exit code 0 | Exit code audit | Non-zero exit code | **HARD NO-GO** |

---

## 5. Gate 4: Pilot Lifecycle & Hygiene Gate

| Metric | Target Requirement | Evaluation Command | Failure Condition | Verdict on Failure |
|---|---|---|---|:---:|
| **Activation Rate** | 100% of pilot injection trials succeed in mutating memory | Automated CSV report check | `activation_verified == false` | **STOP & ABORT** |
| **Sham Controls** | 2/2 sham controls yield $K_{golden}$ with zero drift | Automated CSV report check | Sham control output $\neq K_{golden}$ | **STOP & ABORT** |
| **Restoration Fidelity** | 100% of post-trial tables match golden SHA-256 hash | Table SHA-256 validation | `restoration_verified == false` | **EMERGENCY STOP** |
| **Post-Trial Baseline** | 100% of post-trial baseline runs produce $K_{golden}$ | Output comparison | `hygiene_failure == true` | **EMERGENCY STOP** |
| **Crash Rate** | Zero uncaught hardware traps or crashes | Signal handler audit | `endpoint_outcome == CRASH_SIGNAL` | **STOP & ABORT** |

---

## 6. Conditions Requiring Immediate Campaign Termination (Kill Switch)

If any of the following occur during pilot or campaign execution, the runner process must invoke `abort()` immediately:
1. **Contamination Trigger:** A single instance where post-restoration decapsulation yields an altered shared secret ($K_{post} \neq K_{golden}$).
2. **Page Protection Violation:** Any return code from `vm_protect` other than `KERN_SUCCESS`.
3. **Signal Interception:** Any delivery of `SIGBUS` (signal 10), `SIGSEGV` (signal 11), or `SIGILL` (signal 4).
4. **Surrounding Byte Mutation:** Any detected mutation in the 16,128-byte page padding outside the 256-byte window allocated to `zetas`.
5. **Drift in Reference Vectors:** Mismatch in pre-trial reference inputs or golden digests.
