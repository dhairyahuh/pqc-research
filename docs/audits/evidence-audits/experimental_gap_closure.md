# Experimental Gap Closure and Methodological Audit

**Date:** October 2026  
**Subject:** Methodological Resolution of Critical Experimental Gaps in ML-KEM-768 Fault Resilience  
**Status:** All 8 Critical Gaps Formally Resolved with Source Inspection, Raw Data, and Reproducible Binaries  

---

## 1. Resolution of the 8 Critical Experimental Gaps

### Gap 1: Independent Validation of the Implicit-Rejection Oracle
- **Audit Concern:** Does the test harness verify implicit rejection against an independent standard oracle, or does it compare against the implementation under test?
- **Resolution:** Fully Resolved via Independent Clean-Room Oracle.
  - In `phase18_audit/production_reproducer.c` (lines 48–65), an independent `fips203_cleanroom_reject()` function was implemented using the standalone Keccak-f[1600] / SHAKE-256 implementation.
  - Per FIPS 203 Section 7.3, when decapsulation fails, the oracle recomputes $K_{\text{rej}} = \text{SHAKE256}(z \parallel c, 32)$.
  - Across 200 persistent fault trials ($F5A, F5B$) and 100 invalid ciphertext mutations (`tests/kat_mlkem768.c`), the implementation's output matched the independent clean-room oracle in $100\%$ of cases ($300 / 300$, $95\%$ Wilson score CI: $[98.74\%, 100.00\%]$).

### Gap 2: Direct Recalculation of H1 (Blindness) and H2 (SDC) from Raw Trial Records
- **Audit Concern:** Were H1 and H2 rates calculated from raw trial logs or transcribed from previous summary tables?
- **Resolution:** Direct Recalculation from Raw CSV Datasets.
  - **H1 (Circular Verifier False-Pass):** Recalculated from `phase16_targeted_evidence_closure/h1_activation_audit.csv` across all 6 vulnerable targets ($N=600$):
    - Target 1: $98 / 100$ ($98.0\%$, CI $[93.0\%, 99.5\%]$)
    - Target 2: $94 / 100$ ($94.0\%$, CI $[87.5\%, 97.2\%]$)
    - Target 3: $100 / 100$ ($100.0\%$, CI $[96.3\%, 100.0\%]$)
    - Target 4: $100 / 100$ ($100.0\%$, CI $[96.3\%, 100.0\%]$)
    - Target 5: $99 / 100$ ($99.0\%$, CI $[94.6\%, 99.8\%]$)
    - Target 6: $100 / 100$ ($100.0\%$, CI $[96.3\%, 100.0\%]$)
    - Aggregate: $591 / 600 = 98.5\%$ ($95\%$ Wilson CI: $[97.1\%, 99.2\%]$).
  - **H2 (Production Silent Data Corruption):** Recalculated from fresh binary execution in `phase18_audit/raw_production_trials.csv` across $N=300$ active fault trials:
    - Zero SDC observations ($0 / 300 = 0.00\%$).
    - Applying Wilson score interval with continuity correction yields an empirical $95\%$ confidence interval of $[0.00\%, 1.26\%]$.

### Gap 3: Confirmation that Fault Activation is Recorded Rather than Inferred
- **Audit Concern:** Does the injection harness confirm that a fault was actually injected into the arithmetic state rather than assuming it based on final status?
- **Resolution:** Explicit In-Datapath Activation Logging.
  - In `mlkem_fault_hooks.c` (lines 780–810), the hook records `g_fault_injected = 1`, logs the pre-fault value, corrupts the value (`*t ^= mask`), and verifies `*t != original`.
  - In `production_reproducer.c`, every trial records `fault_activated = 1`. If an injected fault produced no arithmetic difference (e.g., zero mask or identity twiddle), the trial would be flagged as inactive. All 300 active trials confirmed physical value alteration.

### Gap 4: Verification of Genuine Recovery vs. Successful Final Output Alone
- **Audit Concern:** Could a test pass simply because the fault was ignored or bypassed, producing a valid key without actually executing the recovery path?
- **Resolution:** Full Internal State & Counter Audit.
  - In `phase18_audit/production_reproducer.c`, every trial inspects three internal fields from the production object:
    1. `trial_retries`: Must equal exactly $1$ for $F4$ (proving that recovery executed) and exactly $2$ for $F5A/F5B$ (proving that the retry limit was exhausted).
    2. `trial_fail_flag`: Must equal $0x00$ for $F4$ and $0xFF$ for $F5A/F5B$.
    3. `status`: Must transition to `0x5A5A5A5A` for $F4$ and `0xFFFFFFFF` for $F5A/F5B$.
  - All 100 $F4$ trials showed `retry_count == 1`, confirming genuine single-butterfly rollback and recomputation.

### Gap 5: Detection Coverage Across Fault Locations and Persistence
- **Audit Concern:** What is the exact coverage across butterfly stages, and how does the system behave under different fault persistence models?
- **Resolution:** Comprehensive Matrix across Transient, Persistent, and Force-Value Models.
  - Invariant checks are placed on all 7 stages of Forward CT and all 7 stages of Inverse GS.
  - Tested models:
    - Single-event transient bitflips ($F4$): $100\%$ recovery via 1 retry.
    - Multi-cycle persistent faults ($F5A$): $100\%$ safe fail-stop via 2 retries and escalation.
    - Software force-value zeroing ($F5B$): $100\%$ safe fail-stop via 2 retries and escalation.

### Gap 6: Shared-State and Common-Mode Blind Spots
- **Audit Concern:** What happens when twiddle factors or input memory are corrupted?
- **Resolution:** Formal Demarcation of Blind Spots and Two-Tier Defense.
  - **Theorem (Twiddle Factor Blindness):** If twiddle factor $\zeta$ is corrupted in memory, the local monitor computes $r_1 \equiv (u - v)\tilde{\zeta}$ using the same corrupted $\tilde{\zeta}$. The invariant holds identically. Local detection probability is exactly $0.0\%$.
  - **Outer Containment:** The downstream Fujisaki-Okamoto re-encryption comparison (`mlk_ct_memcmp` in `kem.c:166`) detects the discrepancy between candidate ciphertext $c'$ and received ciphertext $c$, forcing implicit rejection ($K_{\text{rej}}$) in $100\%$ of tested twiddle fault cases.

### Gap 7: Reproducible Transform-Operation Counts
- **Audit Concern:** Is the figure of 9,856 butterflies derived from actual code or copied from literature?
- **Resolution:** Line-by-Line Code and Mathematical Proof.
  - Decapsulation (`indcpa.c:609, 621`):
    - $k=3$ Forward NTTs on $\mathbf{u}$ ($3 \times 896 = 2{,}688$ CT butterflies).
    - $1$ Inverse NTT on $v - \mathbf{s}^T \mathbf{u}$ ($1 \times 896 = 896$ GS butterflies).
  - Re-encryption (`indcpa.c:560, 568, 580`):
    - $k=3$ Forward NTTs on $\mathbf{r}$ ($3 \times 896 = 2{,}688$ CT butterflies).
    - $k=3$ Inverse NTTs on $\mathbf{u}'$ ($3 \times 896 = 2{,}688$ GS butterflies).
    - $1$ Inverse NTT on $v'$ ($1 \times 896 = 896$ GS butterflies).
  - Total: 6 Forward transforms ($5{,}376$ CT butterflies) + 5 Inverse transforms ($4{,}480$ GS butterflies) = **11 transforms** and exactly **9,856 butterflies**.

### Gap 8: Benchmark Methodology and Comparable Baselines
- **Audit Concern:** Is the comparison against software DMR fair, and are timing benchmarks reproducible?
- **Resolution:** Rigorous Methodology and Parameterized Profiling.
  - Benchmarked on Apple M3 Pro using `bin/phase7i_e2e_validation` ($N=2{,}000$, 5,000 warmup iterations).
  - Baseline latency: $110.77\,\mu\text{s}$ ($\sigma = 4.82\,\mu\text{s}$).
  - Monitored latency: $129.51\,\mu\text{s}$ ($\sigma = 5.14\,\mu\text{s}$) $\rightarrow +16.9\%$ overhead.
  - Software DMR latency: $260.68\,\mu\text{s}$ ($\sigma = 8.92\,\mu\text{s}$) $\rightarrow +135.3\%$ overhead ($2.35\times$).
  - Across optimization flags (`-O2` vs `-O3`), monitored overhead ranges between $+16.8\%$ and $+28.9\%$, while software DMR ranges between $+135\%$ and $+160\%$.
  - The comparison is strictly against single-threaded software duplicate execution, not specialized multi-core or hardware lockstep.
