# Phase 00: Risk Register & Threat Assessment
## ASTRA-Sec Development — Initial Risk Register for PQC Integration

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Active Baseline  
**Scope:** Cryptographic, algorithmic, fault-tolerance, concurrency, build toolchain, integration, and governance risks.

---

## 1. Risk Scoring Methodology

- **Likelihood ($L$):** 1 (Rare) to 5 (Almost Certain)
- **Impact ($I$):** 1 (Negligible) to 5 (Catastrophic / Severe SDC / Security Compromise)
- **Risk Score ($S = L \times I$):**
  - **1–6:** Low (Acceptable with standard monitoring)
  - **8–12:** Medium (Mitigation required during integration)
  - **15–25:** High / Critical (Mandatory architectural gating prior to deployment)

---

## 2. Comprehensive Risk Register

| Risk ID | Category | Risk Description | $L$ | $I$ | Score | Mitigation Strategy | Contingency Plan | Status |
|---|---|---|:---:|:---:|:---:|---|---|:---:|
| **RSK-01** | Algorithmic | **Twiddle Factor Invariant Blindness (Theorem 1):** Invariant $(u'+v') \equiv 2u \pmod q$ cancels $\zeta v$, blinding operand monitors to twiddle corruption. | 3 | 4 | **12** | Deploy Hardened v2 TFIB reference binding (`tfib_ref.c`), enforcing dual-table verification from independent ROM addresses. | Outer Fujisaki-Okamoto re-encryption rejects corrupted ciphertexts with 0 SDC. | **Mitigated in v2** |
| **RSK-02** | Algorithmic | **Circular Verifier Blindness:** Checkers inspecting live mutated registers fail to detect faults (98.5% failure rate in Phase 16). | 4 | 5 | **20** | Enforce pre-computation register snapshotting (`u_saved, v_saved`) prior to butterfly arithmetic execution. | Automated audit harness continuously verifies snapshot register allocations in disassembly. | **Mitigated** |
| **RSK-03** | Concurrency | **Global Monitor State Non-Reentrancy:** `g_ntt_native_monitor` and `g_tfib_fault` use global structs, which are not thread-safe. | 3 | 4 | **12** | For ASTRA-Sec multi-channel communication, encapsulate telemetry inside per-session thread-local or context-passed structs. | Enforce single-threaded execution during cryptographic handshakes in initial milestone. | **Active / Open** |
| **RSK-04** | Fault Model | **Control-Flow Hijack & Instruction Skips:** Energetic particle causes CPU to skip monitor instructions entirely. | 2 | 5 | **10** | Complement arithmetic invariants with hardware watchdog timers and software branch execution counters. | Fall back to outer FO re-encryption verification at protocol boundary. | **Planned (WP3)** |
| **RSK-05** | Cryptographic | **Timing Side-Channel via Retry Branching:** Non-constant execution time during localized rollback on transient strikes. | 2 | 3 | **6** | Stochastic cosmic radiation events are not attacker-controlled inputs; persistent fail-stop uses constant-time `cmov` for $K_{rej}$. | Implement dummy retry cycles to enforce strict constant-time decapsulation if side-channel attacks are in threat model. | **Monitored** |
| **RSK-06** | Toolchain | **Homebrew Dynamic Linkage Drift:** `Makefile` links `/opt/homebrew/lib/loqs` for Path A harnesses, risking breakage across machines. | 4 | 2 | **8** | Isolate Path A to testing; ensure ASTRA-Sec links hermetic, zero-dependency `mlkem-native` and `libtfib.a` exclusively. | Provide static compilation flags and pre-compiled object archives. | **Mitigated** |
| **RSK-07** | Governance | **Missing Root Repository License:** Repository has no top-level `LICENSE` file, leaving rights ambiguous. | 3 | 3 | **9** | Add formal Apache-2.0 or MIT license file with explicit attribution to `mlkem-native` and `mldsa-native` authors. | Restrict public distribution until repository owner approves license text. | **Action Required** |
| **RSK-08** | Embedded HW | **Stack Budget Exceeded on Microcontrollers:** Embedded flight processors (Cortex-M4) typically have <64 KB SRAM. | 2 | 4 | **8** | Verify that combined polynomial vectors ($k=3$, degree 256, 16-bit) and snapshots stay within 8 KB stack frame. | Use static buffers or BSS allocation if stack size on target flight board is constrained. | **Verified Safe** |
| **RSK-09** | Reliability | **Infinite Retry Loop under Permanent Latchup:** Stuck-at fault in ALU could cause infinite re-execution loop. | 3 | 5 | **15** | Hard-code bounded retry threshold ($R_{max} = 2$) and escalate directly to persistent fail-stop counter. | Hardware watchdog timer triggers system reset if software fails to terminate within 1 ms. | **Mitigated** |
| **RSK-10** | Verification | **FIPS Standard Conformance Drift:** Code modifications during integration could break KAT matching. | 2 | 5 | **10** | Require all 18 NIST KAT vectors (`./bin/test_fips_kats`) to pass in CI prior to any merge or release. | Automated rollback of any integration commit that fails KAT conformance. | **Active Gate** |

---

## 3. High-Priority Mitigation Roadmap for ASTRA-Sec

1. **Context Encapsulation (RSK-03):** Refactor the monitoring API from global variables to an opaque context pointer (`astra_pqc_ctx_t`) before multi-threaded ASTRA-Sec protocol integration.
2. **License Addition (RSK-07):** Formally establish the repository license with the repository owner.
3. **Continuous KAT Gating (RSK-10):** Integrate `./bin/test_fips_kats` as a mandatory pre-commit validation step for all future ASTRA-Sec milestones.
