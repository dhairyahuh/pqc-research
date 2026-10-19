# Research Baseline and Defensible Evidence Reconciliation

**Auditor:** Independent Cryptographic Security Auditor & Implementation Reviewer  
**Scope:** Final Reconciliation of Phase 2 and Phase 3 Claims against Concrete Code, Datasets, and Simulations  
**Standards:** Falsifiable Hypotheses, Zero Unsubstantiated Novelty Claims, Strict Evidence Traceability  

---

## 1. Findings Independently Reproduced

The following cryptographic, fault-tolerance, and protocol behaviors have been independently reproduced with byte-exact verification across 2,400 C trials and 750 simulated protocol sessions:

1. **In-Tree Butterfly Invariant Twiddle Blindness (Target T1)**:
   - When faults are injected into the twiddle factor operand ($\zeta$), the native butterfly invariant checker records `actual_mismatches = 0` in **100.0% [96.3%, 100.0%]** of trials.
   - **Mechanism:** Because both the dynamic butterfly multiplier and the verification monitor share the identical operand pointer or register value $\zeta$, the check $u - v - 2 \cdot fqmul(v, \zeta) \equiv 0 \pmod q$ remains algebraically satisfied under corrupted $\zeta$.
2. **Downstream Containment via Fujisaki-Okamoto Re-Encryption**:
   - Even when intermediate NTT monitors fail to detect twiddle corruption, ML-KEM-768 decapsulation safely rejects the corrupted ciphertext in **97.0% [91.5%, 99.0%]** of trials via the FO transform re-encryption check ($c' \neq c \implies K_{\text{rej}} = J(z \parallel c)$).
   - In **3.0%** of trials (trials 14, 21, 28; bits 14, 5, 12), the corrupted twiddle factor was absorbed by the error-tolerance slack of ML-KEM-768, yielding valid decapsulation.
   - **Silent Data Corruption (SDC):** Strictly **0** SDCs were observed across all 2,400 trials, bounding SDC probability to $\le 0.15\%$ (95% Wilson confidence level).
3. **Transient Multiplier Fault Detection and Recovery (Target T4)**:
   - For genuine arithmetic multiplier glitches ($t$) during forward Cooley-Tukey NTT, the monitor detects the algebraic mismatch, triggers in-place rollback to saved operands, cleanly recomputes on retry, and restores pristine coefficients with **100.0% [96.3%, 100.0%]** success. Output shared keys match ground truth byte-for-byte.
4. **Persistent Stuck-At Fault Containment (Target T5)**:
   - When faults persist across retries (`persistent = true`), the monitor re-detects the mismatch on the second pass, halts recovery, and enforces safe rejection fallback with **100.0% [96.3%, 100.0%]** reliability.
5. **Fail-Stop Key Quenching (Variant D)**:
   - Disabling retry (`allow_retry = false`) successfully prevents speculative key recovery and enforces immediate safe rejection.
6. **Protocol Monotonic Replay Protection**:
   - Monotonic sequence verification ($seq == S_{\text{expected}}$) strictly rejects duplicate telecommand frames resulting from lost acknowledgements (0 replays accepted across all 15 scenarios).

---

## 2. Findings That Failed Reproduction

1. **Variant B "100% Independent Twiddle Detection"**: **FAILED**.
   - In Phase 2 (`countermeasure_eval.c:196-198`), this metric was manually forced in C wrapper code (`g_ntt_native_monitor.mismatch_count++; status = MLK_STATUS_REJECT;`).
   - In reality, no independent twiddle verification logic exists in `algorithms/source_ref/mlkem/`. Under genuine execution, the monitor detects 0% of twiddle faults.
2. **Constant-Time Fail-Stop Execution**: **FAILED**.
   - Clean decapsulation completes in $106.2 \pm 3.1\,\mu\text{s}$, whereas fail-stop execution terminates in $153.1 \pm 3.8\,\mu\text{s}$.
   - This **$+46.9\,\mu\text{s}$ ($+44.2\%$)** timing delta creates an externally observable execution channel that distinguishes clean decapsulation from fault-detected aborts.
3. **Unconditional 100% Space Telecommand Delivery**: **FAILED**.
   - Phase 2 reported 100% delivery by assuming all computational faults vanish on the first retry and ignoring hardware failure modes.
   - When evaluated under persistent stuck-at faults, delivery drops to **86.0%**. When evaluated under radiation-induced endpoint watchdog reboots, delivery collapses to **72.2%** with **84.4%** retransmission overhead.

---

## 3. Results That Are Invalid or Inconclusive

1. **Target T2 (Reference Table Corruption) in Variants A, C, D**:
   - In Phase 3, these trials were reported as `BENIGN_EQUIVALENT_ABSORBED` (100 trials each).
   - **Audit Reality:** The test harness never armed or injected a fault for `tg == 1` in these variants. The cryptographic execution was completely uncorrupted. Reporting these as absorbed faults was an experimental defect; they must be classified as **Not Estimable (0 Triggered Trials)**.
2. **Target T3 (Snapshot Corruption Claims)**:
   - Target T3 was presented as demonstrating recovery from corrupted recovery snapshots.
   - **Audit Reality:** In `poly.c:557-564`, `u_saved` is latched *before* the fault hook mutates `*r_j`. Thus, the recovery snapshot was **never corrupted**. The test only demonstrated recovery from an operating register glitch using a pristine snapshot.
   - Furthermore, the in-tree recovery verifier (`mlkem_fault_hooks.c:857-863`) verifies the retry output against `u_saved`. If `u_saved` were corrupted, the verifier would be completely tautological, recomputing and verifying with the corrupted snapshot and declaring false recovery.
3. **Exploitable SIFA Vulnerability Claim**:
   - Phase 3 claimed that the $+46.9\,\mu\text{s}$ timing difference constitutes a "potent SIFA vulnerability".
   - **Audit Reality:** While an observable timing difference is conclusively demonstrated, classifying it as a SIFA vulnerability is unproven. SIFA requires demonstrating that the fault detection probability is secret-dependent, which was not tested or shown.

---

## 4. Remaining Research Gaps

1. **Compiler-Resilient Table Separation**: How to structure independent reference twiddle tables such that optimizing linkers (LLVM/Clang with ICF/LTO) do not merge identical arrays into single physical memory locations, without requiring specialized hardware MPU/MMU banking.
2. **Constant-Time Fail-Stop Padding**: How to implement deterministic cycle-accurate padding for the fail-stop branch of `mlkem768_dec_monitored()` to equalize execution time to the worst-case path ($155\,\mu\text{s}$) across all inputs.
3. **Authenticated Spacecraft Endpoint Resynchronization**: How to design an authenticated, sequence-protected re-handshake protocol for spacecraft endpoints that reboot during active sessions, guaranteeing that lost ephemeral state does not result in stale command acceptance or unrecoverable channel lockup.

---

## 5. Smallest Next Experiment

### Falsifiable Hypothesis
> **Hypothesis:** *"Padding the fail-stop branch of `mlkem768_dec_monitored()` with constant-time busy-wait delay to normalize its latency to $155.0 \pm 0.5\,\mu\text{s}$ will reduce the timing difference between clean decapsulation and fail-stop abort to $|\Delta t| < 1.0\,\mu\text{s}$ (below the measurement noise threshold) while causing a throughput reduction of less than $3.5\%$ in a simulated 25 ms RTT space link with $5\%$ channel loss and $5\%$ SEU rate."*

### Experimental Design
1. **Implementation**:
   - In `algorithms/source_ref/mlkem_fault_hooks.c`, add a calibrated dummy Montgomery multiplication loop on the fail-stop branch to consume exactly $\approx 47\,\mu\text{s}$ of CPU cycles.
2. **Measurement Protocol**:
   - Run 10,000 clean executions and 10,000 fail-stop executions under pinned CPU affinity.
   - Compute Welch's two-sample t-statistic for timing leakage:
     $$t = \frac{\bar{X}_{\text{clean}} - \bar{X}_{\text{fail-stop}}}{\sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}}$$
   - Falsification criterion: If $|t| \ge 4.5$, the constant-time hypothesis is falsified.
3. **Cross-Layer Throughput Impact**:
   - Run the padded implementation in `cross_layer_sensitivity.py` over 500 sessions.
   - Falsification criterion: If telecommand goodput degrades by $>3.5\%$, the hypothesis is falsified.
