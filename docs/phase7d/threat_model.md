# Formal Threat and Trust Model for ML-KEM Layered Fault Resilience

## 1. System Context and Architectural Scope

This document defines the formal threat model, trust boundaries, physical fault assumptions, and detection/recovery contracts for the layered fault-resilience architecture protecting **NIST FIPS 203 ML-KEM-768** decapsulation in spaceborne systems.

The target system operates in harsh ionizing radiation environments (e.g., Low Earth Orbit, Geostationary Orbit, Deep Space), subject to single-event effects (SEE) such as Single-Event Upsets (SEU), Single-Event Transients (SET), Single-Event Functional Interrupts (SEFI), as well as targeted physical glitching attacks by adversaries with physical or near-field access.

---

## 2. Trust Boundaries and Execution Path

The end-to-end decapsulation execution path spans six discrete stages. The architectural diagram below marks trust domains, data flows, and critical common-mode fault points where a physical disturbance can simultaneously degrade both computation and monitoring.

```
       [ UNTRUSTED NETWORK / SPACE TELECOMMAND LINK ]
                            │
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │ [Stage 1] Input Acquisition & Pre-Invocation Integrity │
   │ - Inputs: ct (1,088 B), expected_ct_crc (32-bit)       │
   │ - Check: crc32_ieee(ct) == expected_ct_crc             │
   │ - [!] COMMON-MODE POINT A: Corrupted input prior to    │
   │     checksum generation or simultaneous CT+CRC corrupt │
   └────────────────────────┬───────────────────────────────┘
                            │ Pass
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │ [Stage 2] Polynomial Transform Domain Invariants       │
   │ - Check: Sum & Weighted NTT projections               │
   │   verify_complementary_ntt(time_poly, ntt_poly)        │
   │ - [!] COMMON-MODE POINT B: Error kernel blind spots    │
   │     (Layers 1-6 butterfly cancellations, zero-weights) │
   └────────────────────────┬───────────────────────────────┘
                            │ Pass
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │ [Stage 3] Native In-Tree Decapsulation (mlk_kem_dec)   │
   │ 1. Hash check: mlk_kem_check_sk(sk)                    │
   │ 2. IND-CPA Decrypt: mlk_indcpa_dec(buf, ct, sk)        │
   │ 3. Derivation: mlk_hash_g(kr, buf, 64)                 │
   │ 4. IND-CPA Re-Encrypt: mlk_indcpa_enc(tmp, buf, pk)   │
   │ 5. FO Dual-Rail Verification:                          │
   │    rail1 = mlk_ct_memcmp(ct, tmp, 1088)                │
   │    rail2 = rev_xor_accumulate(ct, tmp, 1088)           │
   │ - [!] COMMON-MODE POINT C: Shared memory (ct/tmp),     │
   │     ALU comparator stuck-at, condition flag glitch     │
   └────────────────────────┬───────────────────────────────┘
                            │ Internal Status Token
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │ [Stage 4] Fault Monitor & Barrier Verification         │
   │ - Tokens: SUCCESS (0x5A5A5A5A), REJECT (0xA5A5A5A5),   │
   │           FAULT (0xFFFFFFFF)                           │
   │ - Compiler Barriers: __asm__ volatile("" ::: "memory")│
   │ - [!] COMMON-MODE POINT D: Glitched barrier condition, │
   │     symmetric rail flip (rail1 ^ mask == ~rail2 ^ mask)│
   └────────────────────────┬───────────────────────────────┘
                            │
             ┌──────────────┴──────────────┐
             │ Status                      │ Status
             ▼ == OK                       ▼ != OK
   ┌──────────────────┐          ┌──────────────────────────┐
   │ [Stage 6] Output │          │ [Stage 5] Recovery Logic │
   │ Release          │          │ - Retry transient faults │
   │ - Release ss     │          │ - [!] TIMING SIDE-CHANNEL:│
   │   (Shared Secret)│          │   Retrying on REJECT     │
   └──────────────────┘          │   doubles execution time │
                                 │ - Exhaustion -> Zeroize  │
                                 └──────────────────────────┘
```

---

## 3. Explicit Threat and Fault Classification

We partition physical and adversarial faults into eight distinct, precisely bounded classes.

### Class 1: Transient Arithmetic Glitch (Intermediate NTT Butterflies)
- **Fault Location:** Arithmetic Logic Unit (ALU), SIMD multiply-accumulate registers during polynomial NTT computation.
- **Fault Timing:** Mid-transform execution (Layers 1 through 7 of the Cooley-Tukey butterfly network).
- **Fault Duration:** Transient (single-cycle or multi-cycle glitch, 1 to 10 ns).
- **Fault Mechanism:** SEU or voltage glitch causing bit flips in intermediate butterfly variable $t = r[j+\text{len}] \cdot \zeta$.
- **Attacker/Physical Assumptions:** Attacker injects clock/voltage glitches or cosmic ray strikes DSP units.
- **Trusted State:** Input polynomial coefficients $p_{\text{time}}$, twiddle factors $\zeta$.
- **Corrupted State:** Transformed intermediate polynomial buffer $p_{\text{ntt}}$.
- **Expected Detection Mechanism:** Weighted NTT inverse-zeta invariant ($\psi_{\text{even}}, \psi_{\text{odd}}$) and FO ciphertext re-encryption check.
- **Expected Recovery:** Re-execution succeeds after transient state clears.
- **Known Limitations:** The weighted invariant table only provides 100% single-stage coverage at Layer 7. Layers 1–6 exhibit non-trivial error kernels where multi-butterfly perturbations cancel out.

### Class 2: Memory/Register Perturbation (Twiddle Factors $\zeta$)
- **Fault Location:** Constant lookup table memory (SRAM/Flash/ROM) or memory load registers caching roots of unity $\zeta$.
- **Fault Timing:** During twiddle factor loading prior to modular reduction.
- **Fault Duration:** Transient single-word corruption or localized SEU.
- **Fault Mechanism:** Bit flip in stored or loaded $\zeta$ coefficient.
- **Attacker/Physical Assumptions:** Heavy-ion strike on memory cells or read bus line.
- **Trusted State:** Base polynomial coefficients, program counter.
- **Corrupted State:** Twiddle scalar $\zeta_k$, contaminating all downstream butterfly evaluations.
- **Expected Detection Mechanism:** FO ciphertext verification mismatch ($ct \neq \text{tmp}$) and NTT parity check.
- **Expected Recovery:** Autonomous retry with fresh cache line load.
- **Known Limitations:** If the underlying flash memory has a permanent SEU (stuck bit in ROM), retrying the same memory address repeats the failure.

### Class 3: Arithmetic Output Perturbation (Additive Butterfly Glitch)
- **Fault Location:** Accumulator register or write-back bus for butterfly addition/subtraction ($r[j] + t, r[j] - t$).
- **Fault Timing:** Stage write-back phase.
- **Fault Duration:** Transient additive perturbation ($\delta \in [1, q-1]$).
- **Fault Mechanism:** Electromagnetic fault injection (EMFI) or radiation induced charge deposition on register latch.
- **Trusted State:** Time-domain input polynomial.
- **Corrupted State:** Transformed polynomial output buffer.
- **Expected Detection Mechanism:** Parity invariant ($\sum \hat{p} \equiv 128 p_0 \pmod q$) and FO re-encryption.
- **Expected Recovery:** Autonomous single retry.
- **Known Limitations:** Symmetric additive faults ($\Delta r[j] = +\delta, \Delta r[j+\text{len}] = -\delta$) sum to zero in linear parity checks.

### Class 4: Correlated Multiplier Perturbation (Polynomial Multiplication)
- **Fault Location:** Montgomery modular multiplication pipeline ($a \cdot b \cdot R^{-1} \pmod q$).
- **Fault Timing:** Pointwise vector multiplication in IND-CPA encryption or decryption.
- **Fault Duration:** Transient multi-cycle perturbation affecting repeated products.
- **Fault Mechanism:** Clock glitch causing timing violations across pipeline stages.
- **Trusted State:** Matrix $A$, vector $s$.
- **Corrupted State:** Inner product vector accumulator.
- **Expected Detection Mechanism:** Fujisaki-Okamoto re-encryption check ($tmp \neq ct$).
- **Expected Recovery:** Single retry cleans the execution pipeline.
- **Known Limitations:** Linear algebraic NTT invariants cannot detect faults inside pointwise matrix-vector multiplication because polynomial multiplication occurs outside the standalone NTT block.

### Class 5: Pre-Invocation Input Corruption
- **Fault Location:** Inbound communication buffer, DMA ring buffer, or telecommand FIFO memory.
- **Fault Timing:** After transmission reception, before or during cryptographic decapsulation invocation.
- **Fault Duration:** Persistent in the buffer until overwritten.
- **Fault Mechanism:** Memory bit-flip in ciphertext buffer ($ct$) or transmission line noise.
- **Trusted State:** Cryptographic secret key ($sk$), system integrity status.
- **Corrupted State:** Ciphertext buffer $ct \in \mathbb{F}_q^{1088}$.
- **Expected Detection Mechanism:** CRC32 input integrity verification: $\text{CRC32}(ct) == \text{expected\_crc}$.
- **Expected Recovery:** Rejection (safe termination). **Non-recoverable via retry** because the input buffer itself is corrupted.
- **Known Limitations & Blind Spots:**
  1. *Pre-CRC Corruption:* If the ciphertext is corrupted *before* or *during* generation of the CRC checksum, the checksum matches the bad ciphertext. CRC32 provides ZERO authentication against malicious tampering.
  2. *Simultaneous Corruption:* A multi-byte SEU spanning both the ciphertext tail and the CRC field can evade detection (CRC32 error probability $\approx 2^{-32}$).
  3. *TOCTOU (Time-of-Check to Time-of-Use):* If DMA modifies `ct` after CRC verification but before `mlk_indcpa_dec`, the CRC check is bypassed.

### Class 6: Checker Perturbation (Faults on Detection Logic)
- **Fault Location:** Verification registers, intermediate comparison flags, and multi-rail barrier logic.
- **Fault Timing:** During or immediately following checker execution.
- **Fault Duration:** Single-event transient or microarchitectural fault.
- **Fault Mechanism:** Glitch targeting CPU status flags (Zero Flag $Z$, Carry Flag $C$) or multi-rail comparison logic.
- **Trusted State:** None (the detector itself is under attack).
- **Corrupted State:** Rail tokens, boolean comparison result, branch target.
- **Expected Detection Mechanism:** Multi-rail barrier complementarity ($rail_1 == \sim rail_2$), high-Hamming distance status tokens ($d_H \ge 16$).
- **Expected Recovery:** Re-execution or immediate fail-safe lockup.
- **Known Limitations & Blind Spots:**
  - Common-mode ALU failure: If the hardware ALU comparator is stuck, both $rail_1$ and $rail_2$ can be simultaneously assigned corrupt values.
  - Phase 7C harness hardcoded this class (`d6 = true`), leaving empirical validation unmeasured until Phase 7D.

### Class 7: FO Control-Gate Corruption (Verification Predicate Bypass)
- **Fault Location:** FO verification predicate registers `fail` and `fail_chk`.
- **Fault Timing:** Execution of `ct_memcmp` and reverse XOR accumulator loop.
- **Fault Duration:** Transient bit-flip or instruction skip.
- **Fault Mechanism:** Clock glitch skipping `csel` instruction or flipping register holding `fail` from $0xFF \to 0x00$.
- **Trusted State:** In-tree memory buffers `tmp` and `ct`.
- **Corrupted State:** Decision variable `fail`.
- **Expected Detection Mechanism:** Dual-rail forward/reverse discrepancy verification:
  $$\text{Discrepancy} = (fail \neq fail\_chk)$$
  If discrepancy occurs, `fail` is hard-forced to `0xFF` and `internal_status` is forced to `MLK_DECAPS_STATUS_FAULT`.
- **Expected Recovery:** Safe rejection with pseudorandom implicit rejection key; zeroization of candidate secret key.
- **Known Limitations:** If both forward and reverse loops are bypassed or both accumulators suffer identical bit flips (e.g., data bus line stuck to 0), the discrepancy check evaluates to equal.

### Class 8: Persistent Hardware Faults (Stuck-At Defects)
- **Fault Location:** Hardware register cell, bus transceiver line, SRAM bitcell, or ALU bit-slice stuck at logic 0 or 1.
- **Fault Timing:** Continuous across initial execution, monitoring, and all retry attempts.
- **Fault Duration:** Permanent until hardware reset or power cycle.
- **Fault Mechanism:** Total Ionizing Dose (TID) degradation, latch-up, or physical gate failure.
- **Trusted State:** Secret key in immutable storage.
- **Corrupted State:** Any computation passing through the affected bit-slice.
- **Expected Detection Mechanism:** Detection via Invariant/FO/Dual-rail check.
- **Expected Recovery:** **Zero recovery possible.** The system MUST detect failure across retries, exhaust retry limit ($k_{\text{max}} = 1$), safe-abort, and alert the spacecraft flight computer.
- **Known Limitations:** Retrying a persistent fault is useless and wastes CPU cycles. Treating detection as synonymous with recovery is fundamentally flawed.
