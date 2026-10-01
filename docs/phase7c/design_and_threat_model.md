# Phase 7C: Design and Threat Model for Oracle-Free Native Decapsulation Monitoring

## 1. Executive Summary & Problem Formulation
In Phase 7 and Phase 7B, the layered fault-resilience architecture for ML-KEM-768 evaluated decapsulation faults using an external test-harness variable:
```c
bool dec_fault = (expected_ss && memcmp(ss, expected_ss, SS_BYTES) != 0);
```
In an operational space mission (e.g. onboard a satellite or interplanetary probe), the ground station and spacecraft establish a shared secret $K$ through the exchange of public key $pk$ and ciphertext $ct$. The receiving spacecraft possesses only its private key $sk$ and the received ciphertext $ct$. **The ground-truth shared secret `expected_ss` does not exist prior to decapsulation.** Passing `expected_ss` into the decapsulation function was an artificial test artifact that rendered the Phase 7 resilience evaluation dependent on an external oracle.

Phase 7C refactors the decapsulation monitoring architecture to operate completely **oracle-free** and **in-tree**, deriving internal execution integrity directly from the native cryptographic implementation without altering external API contracts or leaking timing or validity oracles.

---

## 2. Core Execution Concepts & Definitions

### 2.1 Successful Decapsulation
An execution is cryptographically successful if and only if:
1. $sk$ satisfies the structural and hash checks mandated by FIPS 203 Section 7.3 ($H(pk) == sk_{\text{hash}}$).
2. The recovered plaintext $m' = \text{INDCPA.Dec}(sk, ct)$ re-encrypts to $c' = \text{INDCPA.Enc}(pk, m', r')$.
3. The constant-time comparison confirms exact equality: $\text{ct\_memcmp}(ct, c') == 0$.
4. The true shared key $K' = \text{hash\_g}(m' \,||\, H(pk))$ is copied into the output buffer $ss$.

### 2.2 Implicit Rejection
Implicit rejection is a fundamental FIPS 203 IND-CCA2 security feature:
1. If $ct \neq c'$ (due to network corruption or active adversarial chosen-ciphertext manipulation), $\text{ct\_memcmp}(ct, c') \neq 0$.
2. Decapsulation does **not** abort with an error code. Instead, it deterministically outputs a pseudorandom rejection key:
   $$K_{\text{rej}} = \text{hash\_j}(z \,||\, ct)$$
   where $z$ is the random seed stored within $sk$.
3. The adversary receives a valid-looking pseudorandom 32-byte key that cannot be distinguished from a true key without knowing $z$, preventing reaction and binary-search attacks.

### 2.3 Internal Invariant Violation
An internal invariant violation represents an anomalous execution state caused by hardware fault injection (e.g. single-event upsets, register flips, twiddle table corruption, or skipped instructions):
1. **Input Integrity Violation:** The ciphertext CRC32 does not match the frame CRC calculated at the link layer before entering the cryptographic pipeline.
2. **NTT Arithmetic Violation:** Intermediate butterfly calculations or twiddle lookups violate the mathematical projection invariants ($\sum \zeta_{2i+1}^{-1}\hat{p} \not\equiv 128 p_2 \pmod{3329}$).
3. **Control-Flow / Predicate Corruption:** Redundant evaluations of the re-encryption check produce conflicting outcomes (e.g. forward vs reverse memory comparisons disagree).
4. **Checker Perturbation:** Internal multi-rail status registers do not satisfy complementary bit patterns ($R_1 \oplus R_2 \neq \text{0xFFFFFFFF}$).

---

## 3. Information Boundaries & Trust Architecture

| Information Item | Available to Native Implementation? | Available to External Spacecraft Network? | Monitored by Phase 7C? |
|---|---|---|---|
| Private Key $sk$ & Seed $z$ | **Yes** (internal memory) | **No** (secret) | Protected from leakage |
| Received Ciphertext $ct$ | **Yes** | **Yes** (transmitted over RF) | Checked via CRC32 |
| Re-encrypted Ciphertext $c'$ | **Yes** (ephemeral buffer) | **No** (ephemeral internal) | Compared against $ct$ |
| FO Comparison Predicate `fail` | **Yes** (`mlk_ct_memcmp`) | **No** (must remain internal) | Dual-evaluated & monitored |
| Internal Status Token | **Yes** (enclave boundary) | **No** (never emitted externally)| Handled via multi-rail |
| Ground-Truth Shared Secret `expected_ss` | **NO** (does not exist) | **NO** (undefined) | **REMOVED ENTIRELY** |

---

## 4. The Validity Oracle Risk & Side-Channel Mitigation

### 4.1 Threat: Creating a Plaintext-Checking Oracle (PCO)
If an implementation exports an external status flag distinguishing `SUCCESS` from `IMPLICIT_REJECTION` over a communications link (or leaks this distinction via execution time, power, or error packets), an active attacker can mount an IND-CCA attack:
* The attacker injects malformed ciphertexts $c^*$.
* If the system replies with "Packet Rejected" or resets connection immediately, the attacker knows $c^* \to m'$ was invalid.
* If the system proceeds normally, the attacker learns the candidate message structure.
* Over thousands of queries, this allows key recovery (e.g. Fujisaki-Okamoto oracle attacks).

### 4.2 Mitigation Strategy: Internal-Only Encapsulation
1. **External API Unchanged:** The standard `mlk_kem_dec(ss, ct, sk)` interface remains identical to FIPS 203. It always returns `0` and populates `ss` with either $K'$ or $K_{\text{rej}}$ in constant time.
2. **Internal Enclave Monitoring:** The extended function `mlk_kem_dec_monitored()` exposes the status **only** within the internal cryptographic pipeline (e.g. to the retry controller).
3. **No External Signaling on Rejection:** If `ct` is invalid, the system produces $K_{\text{rej}}$ in constant time. No external telemetry message or diagnostic packet is dispatched across the RF link.
4. **Transient Fault Recovery:** If the internal status indicates `REJECT`, the internal controller can distinguish an SEU from a malformed ciphertext by performing an autonomous transient retry:
   - If retry succeeds ($ct == c''$), the initial mismatch was caused by an internal transient SEU during decapsulation $\to$ the spacecraft recovers the genuine $K'$ and avoids desynchronization.
   - If retry still fails ($ct \neq c''$), the ciphertext is genuinely malformed $\to$ the system outputs $K_{\text{rej}}$ in constant time.

---

## 5. Scope of Protection & Residual Threat Model

### In-Scope Faults (Covered by Phase 7C Architecture)
1. **Pre-Invocation Ciphertext Bit Flips:** Injected before decapsulation, caught by CRC32 before memory processing.
2. **Intermediate NTT Butterfly Faults:** Single-event transients in NTT stages caught by weighted inverse-zeta projection checks.
3. **Twiddle Factor / Arithmetic Multiplier Faults:** Corrupted lookup tables or multipliers caught by complementary dual projections.
4. **FO Re-encryption Comparison Perturbations:** Transients during `INDCPA.Dec` or `INDCPA.Enc` caught by native re-encryption comparison and recovered via transient retry.
5. **Control-Flow / FO Predicate Overrides:** Malicious or physical flips of the comparison decision bit caught via dual-rail reverse comparison.
6. **Multi-Rail State Perturbations:** Injected bit flips into the monitor token registers caught by compiler-barriered complementary masks.

### Out-of-Scope Faults (Residual Blind Spots)
1. **Correlated Symmetric Double-Pass Multipliers:** Persistent hardware faults that affect both primary execution and retry identically.
2. **Physical Laser Probing of $z$ or $sk$ in Memory:** Hardware-level physical memory tampering requires hardware shielding / BIST.
3. **Common-Mode Input Buffer Alterations Prior to Checksumming:** Corruptions introduced prior to frame generation.
