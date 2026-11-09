# Comprehensive Technical Defense & Study Guide
## Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment

This document is your complete oral defense handbook. It prepares you to confidently answer critical questions from professors, cryptographers, and avionics engineers.

Every question provides:
1. **Short Oral Answer (20–40 seconds):** What you should say immediately when asked.
2. **Technical Deep Dive:** The detailed mathematical, algorithmic, and architectural facts.
3. **Potential Follow-Up Question:** What the professor might probe next.

---

## Category A: Fundamental Cryptographic Concepts

### Q1: What is the fundamental difference between conventional cryptography and Post-Quantum Cryptography?
- **Short Oral Answer (~30s):**  
  *"Conventional public-key cryptography—like RSA and Elliptic Curve Cryptography—relies on mathematical problems such as prime factorization and discrete logarithms. Peter Shor proved that a quantum computer can solve these problems in polynomial time. Post-Quantum Cryptography refers to classical algorithms whose mathematical security rests on problems believed to be intractable for both classical and quantum computers, such as high-dimensional lattice problems like Module-LWE."*
- **Technical Deep Dive:**  
  - RSA relies on factoring $N = pq$; ECC relies on finding $k$ such that $Q = kP$. Shor's algorithm (1994) uses the Quantum Fourier Transform to solve period finding in $O((\log N)^3)$ operations, rendering 2048-bit RSA and 256-bit ECC completely insecure.
  - PQC operates on classical processors using classical arithmetic. FIPS 203 (ML-KEM) is based on the hardness of the Module Learning With Errors (M-LWE) problem over the cyclotomic ring $R_q = \mathbb{Z}_{3329}[X]/(X^{256} + 1)$. The best-known quantum algorithms (e.g., dual lattice attacks using the BKZ reduction algorithm) achieve only exponential complexity $2^{O(d)}$ against lattice problems.
- **Potential Follow-Up:** *"Does Grover's algorithm break post-quantum cryptography?"*  
  *Answer:* No. Grover's algorithm provides a quadratic speedup for unstructured search ($O(\sqrt{N})$ instead of $O(N)$), which effectively halves symmetric security levels (e.g., AES-256 provides 128-bit quantum security). PQC key sizes are selected specifically to maintain security margins against Grover.

---

### Q2: What is a Key-Encapsulation Mechanism (KEM) and why is it preferred over raw public-key encryption?
- **Short Oral Answer (~30s):**  
  *"A Public-Key Encryption scheme encrypts an arbitrary user-supplied plaintext. A Key-Encapsulation Mechanism, or KEM, generates a random symmetric key and simultaneously encapsulates it in an encrypted ciphertext. Decapsulation recovers that exact symmetric key. KEMs are preferred because they avoid complex plaintext padding vulnerabilities and directly provide IND-CCA2 secure key establishment for hybrid symmetric ciphers like AES-GCM."*
- **Technical Deep Dive:**  
  - A KEM consists of three algorithms:
    1. $\text{KeyGen}() \to (\text{pk}, \text{sk})$
    2. $\text{Encaps}(\text{pk}) \to (c, K_{\text{shared}})$
    3. $\text{Decaps}(c, \text{sk}) \to K_{\text{shared}}$
  - Under FIPS 203, ML-KEM uses the Fujisaki-Okamoto (FO) transform to convert a passively secure (IND-CPA) public-key encryption scheme (K-PKE) into an actively secure (IND-CCA2) KEM. The sender samples 32 random bytes $m$, computes $(K, r) = G(m \parallel H(\text{pk}))$, and encrypts $m$ using coins $r$.
- **Potential Follow-Up:** *"Why is decapsulation the most critical target for fault attacks?"*  
  *Answer:* Decapsulation processes the private secret key $\hat{\mathbf{s}}$ and untrusted ciphertexts. If a fault perturbs the decrypted plaintext or bypasses re-encryption validation, the receiver might accept a corrupted key or leak secret-key information.

---

### Q3: What is ML-KEM-768 and why was it chosen as the primary focus of this research?
- **Short Oral Answer (~30s):**  
  *"ML-KEM-768 is the parameter set standardized in NIST FIPS 203 corresponding to NIST Security Category 3, providing classical and quantum security equivalent to AES-192. It balances key size—1,184-byte public keys and 1,088-byte ciphertexts—with computational latency. It is the designated primary standard for general-purpose secure communications worldwide, making it the highest-priority target for implementation resilience."*
- **Technical Deep Dive:**  
  - Parameter comparison in FIPS 203:
    - ML-KEM-512: Module rank $k = 2$, NIST Category 1 (AES-128 equivalent).
    - **ML-KEM-768: Module rank $k = 3$, NIST Category 3 (AES-192 equivalent).**
    - ML-KEM-1024: Module rank $k = 4$, NIST Category 5 (AES-256 equivalent).
  - All three operate over the identical ring $R_q = \mathbb{Z}_{3329}[X]/(X^{256} + 1)$ with identical modulus $q = 3329$ and identical polynomial degree $n = 256$.
  - In ML-KEM-768, the public matrix $\mathbf{A}$ has dimension $3 \times 3$, secret vector $\mathbf{s}$ has dimension $3$, and decapsulation requires exactly 11 polynomial transforms ($9{,}856$ butterflies).
- **Potential Follow-Up:** *"Would your fault resilience scheme work on ML-KEM-512 or ML-KEM-1024?"*  
  *Answer:* Yes, identically. Because the polynomial arithmetic and butterfly structures ($q = 3329, n = 256$) are mathematically identical across all parameter sets, the exact same butterfly invariant equations and register snapshot primitives apply; only the module rank $k$ (number of transforms) changes.

---

### Q4: What is "Implicit Rejection" in FIPS 203 Section 7.3?
- **Short Oral Answer (~35s):**  
  *"Implicit rejection is a defensive cryptographic mechanism in IND-CCA2 KEMs. When decapsulation detects an invalid ciphertext or an arithmetic mismatch, it does NOT return an error code or empty key—which would give an attacker an error oracle. Instead, it deterministically outputs a pseudorandom key derived from a secret seed $z$ and the ciphertext: $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$. The attacker cannot tell whether decapsulation succeeded or failed, preventing chosen-ciphertext attacks."*
- **Technical Deep Dive:**  
  - Standardized in FIPS 203 Section 7.3: The secret key $\text{sk}$ contains a 32-byte pseudo-random rejection seed $z$.
  - During decapsulation, candidate message $m'$ is decrypted, re-encrypted to candidate ciphertext $c'$, and compared: `fail = ct_memcmp(c, c')`.
  - Rejection key is computed: $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.
  - Constant-time conditional move (`mlk_ct_cmov_zero`) selects valid key $K_{\text{valid}}$ if `fail == 0`, else retains $K_{\text{rej}}$.
  - Our architecture ties hardware fault containment directly into this mechanism: if persistent defects occur, `fail` is forced to `0xFF`, guaranteeing deterministic implicit rejection `[DIRECTLY OBSERVED: kem.c:489]`.
- **Potential Follow-Up:** *"If the key is rejected, why is that considered a safe outcome?"*  
  *Answer:* Because $K_{\text{rej}}$ is derived using a cryptographic hash of the secret seed $z$ and the ciphertext. It leaks zero mathematical information about the private key vector $\mathbf{s}$, preventing fault analysis.

---

## Category B: Mathematical Foundations & NTT Invariants

### Q5: Why do we use the Number Theoretic Transform (NTT) instead of naive polynomial multiplication?
- **Short Oral Answer (~30s):**  
  *"In ML-KEM, multiplying two degree-256 polynomials naively requires 65,536 coefficient multiplications, which is far too slow for real-time systems. The NTT is a Discrete Fourier Transform over finite fields. By transforming polynomials into the NTT domain, multiplication becomes point-wise coordinate multiplication, reducing computational complexity from $O(n^2)$ to $O(n \log n)$."*
- **Technical Deep Dive:**  
  - Naive schoolbook multiplication of $a(X) \cdot b(X) \pmod{X^{256} + 1}$ requires $256^2 = 65{,}536$ modular multiplications plus reductions.
  - The NTT factors $X^{256} + 1$ over $\mathbb{Z}_{3329}$ into 128 quadratic factors: $X^{256} + 1 \equiv \prod_{i=0}^{127} (X^2 - \zeta^{2i+1}) \pmod{3329}$.
  - In the NTT domain, polynomials are represented as 128 degree-1 polynomials. Multiplying two elements in the NTT domain requires only 128 degree-1 polynomial multiplications (each taking 4 coefficient multiplications), reducing operations by over $90\%$.
- **Potential Follow-Up:** *"Why is the modulus $q = 3329$ specifically chosen?"*  
  *Answer:* $3329$ is prime, fits in 16-bit signed registers (`int16_t`), and satisfies $3329 \equiv 1 \pmod{512}$, meaning $256 \mid (q - 1)$. This guarantees the existence of a 256-th primitive root of unity, enabling full 7-stage NTT decomposition.

---

### Q6: Can you write out and explain the Cooley-Tukey butterfly invariant derivation?
- **Short Oral Answer (~40s):**  
  *"In a forward Cooley-Tukey butterfly, the inputs are $u$ and $v$ with twiddle $\zeta$. We compute $t = v \cdot \zeta \pmod q$, and the outputs are $r_0 = u + t$ and $r_1 = u - t$. If we add the two outputs, $r_0 + r_1 = (u + t) + (u - t) = 2u \pmod q$. The sum is algebraically invariant to $t$. If we subtract them, $r_0 - r_1 = 2t \pmod q$. If a fault corrupts $t$ by error $e_t$, the difference check detects $2e_t \pmod{3329}$. Because $\gcd(2, 3329) = 1$, any non-zero fault is caught with 100% certainty."*
- **Technical Deep Dive:**  
  - Operational equations:
    $$t = \text{fqmul}(v, \zeta) = (v \cdot \zeta \cdot R^{-1}) \pmod q$$
    $$r_0 = u + t \pmod q, \quad r_1 = u - t \pmod q$$
  - Verification equations:
    $$\Delta_{\text{sum}} = (r_0 + r_1 - 2u) \pmod q \equiv 0$$
    $$\Delta_{\text{mul}} = (r_0 - r_1 - 2t_{\text{check}}) \pmod q \equiv 0$$
    where $t_{\text{check}} = \text{fqmul}(v_{\text{saved}}, \zeta)$.
  - If a fault strikes $t \to \tilde{t} = t + e_t$:
    - $\tilde{r}_0 = u + t + e_t, \quad \tilde{r}_1 = u - t - e_t$
    - $\Delta_{\text{sum}} = (u + t + e_t) + (u - t - e_t) - 2u = 2u - 2u \equiv 0 \pmod q$ (Sum is completely blind!).
    - $\Delta_{\text{mul}} = (u + t + e_t) - (u - t - e_t) - 2t = 2t + 2e_t - 2t = 2e_t \pmod q$.
    - In $\mathbb{Z}_{3329}$, $2e_t \equiv 0 \pmod{3329} \iff e_t \equiv 0 \pmod{3329}$.
- **Potential Follow-Up:** *"Why is checking $\Delta_{\text{sum}}$ alone dangerous?"*  
  *Answer:* Because $\Delta_{\text{sum}}$ cancels out $t$. Any fault on the multiplier output $t$ completely bypasses the sum check. A dual invariant (sum AND difference) is mathematically required.

---

### Q7: Why is verifying the Inverse NTT (Gentleman-Sande) harder, and how did you solve it?
- **Short Oral Answer (~35s):**  
  *"In the inverse Gentleman-Sande butterfly, the outputs are $r_0 = u + v$ and $r_1 = (v - u) \cdot \zeta$. Trying to formulate a direct algebraic invariant between $r_0$ and $r_1$ requires dividing by the twiddle factor $\zeta$, which requires an expensive modular inversion at runtime. We solved this by creating decoupled invariant checks: an adder rail that verifies $r_0$ against $(u_{\text{saved}} + v_{\text{saved}})$, and an independent multiplier rail that recomputes the expected product in the forward direction. This eliminates modular division entirely."*
- **Technical Deep Dive:**  
  - GS butterfly equations:
    $$r_0 = u + v \pmod q$$
    $$r_1 = (v - u) \cdot \zeta \pmod q$$
  - Inverting $\zeta$ would require precomputing or calculating $\zeta^{-1} \pmod{3329}$ for every butterfly, adding massive table overhead or division latency.
  - Decoupled solution in `mlkem_fault_hooks.c:819-827`:
    1. Adder Rail: $\Delta_{\text{add}} = (r_0 - (u_{\text{saved}} + v_{\text{saved}})) \pmod q \equiv 0$
    2. Multiplier Rail: $v_{\text{expected}} = \text{fqmul}(v_{\text{saved}} - u_{\text{saved}}, \zeta)$, then $\Delta_{\text{mul}} = (r_1 - v_{\text{expected}}) \pmod q \equiv 0$.
  - Both operations require only 1 addition, 1 subtraction, and 1 forward multiplication, with zero heap memory and zero division cycles.
- **Potential Follow-Up:** *"Does this decoupled check catch 100% of faults in the inverse transform?"*  
  *Answer:* Yes. Phase 7I and Phase 18 empirical results confirm 100% detection across all inverse butterfly fault injection loci `[DIRECTLY OBSERVED: raw_production_trials.csv]`.

---

## Category C: Fault Attacks & Threat Models

### Q8: What is the difference between a Transient Single-Event Upset (SEU) and a Persistent Fault?
- **Short Oral Answer (~30s):**  
  *"A transient SEU is a temporary bitflip caused by an ionizing particle striking a flip-flop or ALU register; the physical hardware is undamaged, and retrying the operation will succeed. A persistent fault is caused by cumulative radiation damage (Total Ionizing Dose) or latch-up that leaves a register bit permanently stuck at 0 or 1. Retrying a persistent fault will fail every time, requiring deterministic fail-stop escalation."*
- **Technical Deep Dive:**  
  - Transient SEU (Single-Event Upset): Modeled as a single-cycle bit inversion ($x \oplus 2^b$). The next clock cycle or recomputation operates on clean hardware. In our harness, transient faults trigger once (`trigger_count == 0`), allowing retry 1 to succeed ($F4$).
  - Persistent / Stuck-At Defect: Modeled as a permanent bitmask or force-value applied across all execution attempts (`persistent == true`). In our harness, persistent faults re-strike on retry 1 and retry 2 ($F5A, F5B$), enforcing the 2-retry threshold and triggering fail-stop implicit rejection.
- **Potential Follow-Up:** *"How many retries does your system allow before escalating to fail-stop?"*  
  *Answer:* Exactly 2 retries. If the invariant fails after 2 attempts, the system classifies the defect as persistent, stops recomputation, and escalates to implicit rejection `[DIRECTLY OBSERVED: AYUSH.md:69]`.

---

### Q9: What is Silent Data Corruption (SDC), and why is it catastrophic in cryptography?
- **Short Oral Answer (~30s):**  
  *"Silent Data Corruption occurs when a computational error modifies the output of an algorithm, but the system completes execution normally without raising any alarm or error flag. In cryptography, an SDC event means the decapsulation engine emits an incorrect or partially predictable shared key. If an attacker can inject faults and observe the resulting key, they can solve for private key coefficients and completely break the cryptosystem."*
- **Technical Deep Dive:**  
  - SDC in ML-KEM decapsulation is formally defined as:
    $$\text{Return Code} == 0 \quad \land \quad K_{\text{emitted}} \neq K_{\text{valid}} \quad \land \quad K_{\text{emitted}} \neq K_{\text{rej}}(c)$$
  - If $K_{\text{emitted}}$ matches neither the authentic session key nor the canonical FIPS 203 Section 7.3 implicit rejection key, the output is corrupt.
  - In our Phase 18 audit of 300 active production trials, **SDC = 0/300** ($95\%$ Wilson CI: $[0.00\%, 1.26\%]$). Across the 900-trial canonical campaign, **SDC = 0/750** active trials (one-sided $97.5\%$ Clopper-Pearson bound: $\le 0.49\%$) `[INDEPENDENTLY RECOMPUTED: raw_production_trials.csv, tfib_trial_level_results.csv]`.
- **Potential Follow-Up:** *"Can't downstream message authentication codes (MAC) or TLS record layers catch SDC anyway?"*  
  *Answer:* A downstream MAC catches data mismatch, but it causes session teardown. More critically, if the decapsulation engine emits an uncontained key, an attacker running a fault-injection side-channel attack can use the corrupted key exchange to deduce the long-term secret key $\hat{\mathbf{s}}$.

---

### Q10: What is Circular Verifier Blindness, and what did your research discover about it?
- **Short Oral Answer (~35s):**  
  *"A circular verifier is a fault-detection checker that reads its inputs directly from live output registers rather than isolated snapshots. In Phase 16, we tested 600 unshielded circular verifiers across 6 arithmetic corruption sites. We discovered that they suffered a 98.5% false-pass rate. When an arithmetic fault alters intermediate values, the corruption propagates symmetrically through both sides of the verification equation, causing the verifier to report that the calculation was valid. This proved that snapshot-isolated checking is strictly mandatory."*
- **Technical Deep Dive:**  
  - Evaluated in Phase 16 across 6 target loci (T1–T6) with 100 trials each ($N=600$ total):
    - T1 (CT Multiplier): 98/100 false passes ($98.0\%$)
    - T2 (CT Subtractor): 94/100 false passes ($94.0\%$)
    - T3 (GS Adder): 100/100 false passes ($100.0\%$)
    - T4 (GS Multiplier): 100/100 false passes ($100.0\%$)
    - T5 (Twiddle Scale): 99/100 false passes ($99.0\%$)
    - T6 (In-Place Array): 100/100 false passes ($100.0\%$)
  - Total Aggregate: **591/600 false passes (98.5% blindness)** `[DIRECTLY OBSERVED: phase16_targeted_evidence_closure/h1_activation_audit.csv]`.
  - Resolution: Operands must be snapshotted into registers *before* the butterfly operation executes (`u_saved, v_saved`), and verified against independent reference constants.
- **Potential Follow-Up:** *"What prevented your final implementation from suffering this blindness?"*  
  *Answer:* Our implementation saves $u_{\text{saved}}$ and $v_{\text{saved}}$ before the butterfly arithmetic executes in `poly.c:393-394`, and re-multiplies using independent reference twiddles from `tfib_zetas_ref`, maintaining strict domain isolation.

---

## Category D: Implementation & Technical Architecture

### Q11: Explain how localized register rollback works in code without heap allocation.
- **Short Oral Answer (~35s):**  
  *"In `poly.c`, right before each butterfly, the 16-bit coefficients $u$ and $v$ are copied into local stack variables, which compiler optimization maps to CPU registers. The butterfly executes in-place on the array. The monitor evaluates the invariants. If a mismatch occurs, the array elements are overwritten with the saved register values, and the butterfly is re-evaluated using reference constants. Because everything resides in CPU registers or on the immediate execution stack, dynamic heap allocation is strictly zero bytes."*
- **Technical Deep Dive:**  
  - Source lines: [`algorithms/source_ref/mlkem/src/poly.c:393-394`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L393-L394):
    ```c
    int16_t u_saved = r[j];
    int16_t v_saved = r[j + len];
    ```
  - Rollback lines: [`algorithms/source_ref/mlkem_fault_hooks.c:635-636`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L635-L636):
    ```c
    *r_j = u_saved;
    *r_j_len = v_saved;
    int16_t t_retry = monitor_fqmul(v_saved, zeta);
    *r_j = (int16_t)(u_saved + t_retry);
    *r_j_len = (int16_t)(u_saved - t_retry);
    ```
  - In ARM64 assembly under `-O3`, `u_saved` and `v_saved` reside in registers `w19`–`w22`. No stack push/pop or heap `malloc` occurs during normal or recovery execution.
- **Potential Follow-Up:** *"What happens if the register holding `u_saved` itself is hit by an SEU?"*  
  *Answer:* If `u_saved` is faulted, the retry invariant check `diff_retry` or `sum_retry` will fail, incrementing `persistent_count` and safely escalating to FIPS 203 implicit rejection. SDC is prevented.

---

### Q12: How does persistent fault handling quench intermediate outputs in `kem.c`?
- **Short Oral Answer (~35s):**  
  *"In `kem.c`, after the polynomial arithmetic and FO re-encryption finish, the code checks `ntt_native_monitor_get_persistent_count()`. If this count is greater than zero, the variable `fail` is unconditionally forced to `0xFF`. This bypasses candidate key selection and ensures that only the deterministic rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ is copied into the return buffer. Corrupted intermediate outputs are quenched and never released."*
- **Technical Deep Dive:**  
  - Source lines: [`algorithms/source_ref/mlkem/src/kem.c:484-494`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L484-L494):
    ```c
    extern uint32_t ntt_native_monitor_get_persistent_count(void);
    extern uint32_t invntt_native_monitor_get_persistent_count(void);
    if (ntt_native_monitor_get_persistent_count() > 0 ||
        invntt_native_monitor_get_persistent_count() > 0)
    {
      fail = 0xFF; /* Force implicit rejection */
      if (internal_status != NULL) {
        *internal_status = MLK_DECAPS_STATUS_FAULT;
      }
    }
    ```
  - Followed on line 519 by constant-time key multiplexing:
    ```c
    mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
    ```
    If `fail != 0`, `ss` retains $K_{\text{rej}}$; the valid key candidate `kr` is never moved into the output buffer.
- **Potential Follow-Up:** *"Why not just call `exit()` or `abort()` immediately when a persistent fault is detected?"*  
  *Answer:* In cryptographic implementations, sudden process aborts or variable execution termination leaks timing and side-channel information to an observer. Forcing FIPS 203 implicit rejection allows the routine to finish in standard fashion without exposing an oracle.

---

### Q13: What is Twiddle Factor Blindness (Theorem 1), and how did the v2 implementation resolve it?
- **Short Oral Answer (~40s):**  
  *"Theorem 1 proves that if an operational twiddle factor is corrupted in memory, a local monitor that consumes that same twiddle factor evaluates both the sum and difference invariants to zero—meaning 0% local detection. Our v2 architecture (TFIB-Ref) resolves this by creating an independent reference table in read-only memory, computing the canonical twiddle index independently from loop indices, and performing a direct cross-check. This raised twiddle fault detection from 0% to 100%."*
- **Technical Deep Dive:**  
  - Theorem 1 Proof: $\Delta_{\text{mul}} = 2(v \cdot \tilde{\zeta}) - 2(v \cdot \tilde{\zeta}) \equiv 0 \pmod q$.
  - Resolution in [`tfib_implementation/tfib_ref.c:41-66`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L41-L66):
    - Independent table: `const int16_t tfib_zetas_ref[128] = { ... };` in `.rodata`.
    - Canonical index mapping: `unsigned k = tfib_twiddle_idx_ntt(layer, b_idx);`
    - Reference twiddle lookup: `int16_t zeta_ref = tfib_zetas_ref[k];`
    - Mismatch detection: `bool twiddle_mismatch = (zeta_op != zeta_ref);`
    - In-place repair: if `zeta_op` was faulted, recompute using `zeta_repair = tfib_zetas_ref[k];`.
  - Results: Baseline detection was 0/50 (0.0%); TFIB-Ref detection is 50/50 (100.0%) with 50/50 genuine recoveries `[DIRECTLY OBSERVED: tfib_analysis.md:46]`.
- **Potential Follow-Up:** *"What happens if both tables are corrupted simultaneously?"*  
  *Answer:* If a common-mode fault flips the identical bit in both tables, local detection drops to 0.0%. However, downstream Fujisaki-Okamoto re-encryption comparison catches 96% of corruptions, with the remaining 4% absorbed by centered binomial decoding slack, yielding 0% SDC across all 900 trials `[INDEPENDENTLY RECOMPUTED: tfib_trial_level_results.csv]`.

---

## Category E: Experimental Methodology & Performance Verification

### Q14: How were faults injected into the implementation?
- **Short Oral Answer (~30s):**  
  *"Faults were injected using compiled source-level instrumentation hooks embedded directly into production C binaries. The hooks intercept butterfly execution at specific layers and operand loci, altering inputs, multiplier products, twiddle factors, or control flags using deterministic bitflips, force-values, or additive deltas, while maintaining strict isolation from the test harness."*
- **Technical Deep Dive:**  
  - Instrumentation hooks in [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c):
    - `hook_mid_ntt_pre_butterfly`: Targets input operands $u, v$ or twiddle factor $\zeta$ before arithmetic.
    - `hook_mid_ntt_post_mul`: Targets intermediate product $t$ after `mlk_fqmul`.
    - `hook_mid_ntt_butterfly`: Targets outputs $r_0, r_1$ after add/sub.
  - The experiment runner configures `g_mlkem_fault` with target stage (1..7), butterfly index (0..127), locus, bitmask, and persistence flag.
  - The compiled production object `mlkem768_inst.o` is linked against the test harness, ensuring that production code paths are evaluated without simulated mocking.
- **Potential Follow-Up:** *"Why use source-level hooks instead of assembly debugging tools like GDB or LLDB?"*  
  *Answer:* Source-level hooks allow exact, microsecond-level reproducibility of thousands of trials with precise mathematical control over operand values, which debugger breakpoints cannot achieve without introducing thousands of context-switch stalls.

---

### Q15: There were reports mentioning "38.10 µs unmonitored median", "141.80 µs v2 median", and "150,000 stress test operations". Did your audit verify these numbers?
- **Short Oral Answer (~40s):**  
  *"Our rigorous audit investigated those figures against all raw repository datasets. We found that 38.10 µs, 141.80 µs, and the 50,000-per-config benchmark are unverified external leads that do not exist in the raw empirical data. The 150,000 figure was a historical Phase 2 fault-injection campaign, not a stress benchmark. The actual verified numbers are: Phase 7I measured +16.9% overhead (129.51 µs vs 110.77 µs), Phase 7H measured DMR at +99.33%, and our 40,000-run sample audit measured baseline median latency at 145.96 µs and TFIB-Ref median latency at 173.15 µs."*
- **Technical Deep Dive:**  
  - Classified under Part 0 as `[UNKNOWN / UNVERIFIED]` for the specific latency figures `38.10 µs`, `141.80 µs`, `93.30 µs IQR`, and `17.03 µs IQR`.
  - The term `>150,000 trials` is `[DIRECTLY OBSERVED: docs/phase2-mlkem-fault-campaign-audit.md:111]` as an exploratory fault campaign across 117 ML-KEM parameter variations.
  - Actual empirical benchmark records:
    1. Phase 7I: $N = 2{,}000$ iterations on Apple M3 Pro (`-O3`): Baseline $110.77\,\mu\text{s}$, Monitored $129.51\,\mu\text{s}$ (+16.9% overhead) `[REPORTED BY PRIOR PHASE: phase7i_e2e_results.json]`.
    2. Phase 7H: $N = 2{,}000$ iterations: Baseline $46.65\,\mu\text{s}$, DMR $92.98\,\mu\text{s}$ (+99.33% overhead) `[DIRECTLY OBSERVED: phase7h_timing_distribution.json]`.
    3. TFIB Audit: $40{,}000$ timed runs ($10{,}000$ per condition) in `tfib_benchmark_raw.csv`: Baseline median $145.96\,\mu\text{s}$ (IQR $114.50\,\mu\text{s}$), TFIB-Ref median $173.15\,\mu\text{s}$ (IQR $117.64\,\mu\text{s}$), TFIB-Meta median $260.04\,\mu\text{s}$ (IQR $151.44\,\mu\text{s}$), TFIB-Ref recovery median $292.92\,\mu\text{s}$ (IQR $157.74\,\mu\text{s}$) `[INDEPENDENTLY RECOMPUTED: tfib_benchmark_raw.csv]`.
- **Potential Follow-Up:** *"Why is it important to distinguish verified data from external report leads?"*  
  *Answer:* Academic integrity requires that we never present ungrounded or AI-hallucinated figures as experimental proof. Every published metric must trace directly to an underlying raw CSV or JSON artifact.

---

### Q16: How did you calculate confidence intervals, and what do they demonstrate?
- **Short Oral Answer (~30s):**  
  *"For binary success proportions—like detection rate, recovery rate, and SDC rate—we calculated 95% Wilson Score Confidence Intervals. When observed events are zero (such as zero SDC across 750 trials), we computed exact one-sided 97.5% Clopper-Pearson upper confidence bounds. These statistical intervals prove that our zero SDC observation is not a small-sample anomaly, but bounds uncontained leakage below 0.49% with 97.5% confidence."*
- **Technical Deep Dive:**  
  - Wilson Score Interval: Used for binomial proportions $p = x/n$, especially near 0 or 1 where standard normal approximations ($\hat{p} \pm 1.96 \sqrt{\hat{p}(1-\hat{p})/n}$) break down:
    $$CI = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
  - In Phase 18:
    - Transient Recovery: $100/100 \to [96.30\%, 100.00\%]$
    - Persistent Fail-Stop: $200/200 \to [98.12\%, 100.00\%]$
    - Production SDC: $0/300 \to [0.00\%, 1.26\%]$
  - In Canonical Campaign ($N = 750$ active trials):
    - Clopper-Pearson exact one-sided $97.5\%$ upper bound for $x = 0$:
      $$p_{\text{upper}} = 1 - (1 - 0.975)^{1/750} = 1 - (0.025)^{1/750} \approx 0.004907 \implies \mathbf{0.49\%}$$
- **Potential Follow-Up:** *"Why not just claim that the SDC probability is mathematically zero?"*  
  *Answer:* In empirical science, you cannot claim a probability of mathematical zero from finite sampling. An empirical trial of 750 tests with zero failures proves with 97.5% confidence that the true defect rate is less than 0.49%.

---

## Category F: Critical Questions & Limitations

### Q17: Have you tested physical radiation in a cyclotron or tested laser fault injection?
- **Short Oral Answer (~35s):**  
  *"No, we have not tested physical cyclotron beam irradiation or laser fault injection. That is an explicit boundary of this research. Our work is a software-level architectural resilience study that models the consequence of an upset latched into CPU registers. While software bitflips cannot model semiconductor charge transport or analog clock glitches, they provide the necessary mathematical and software foundation before committing to multi-million-dollar cyclotron beam time."*
- **Technical Deep Dive:**  
  - Dodd & Massengill (IEEE TNS 2003) established that physical heavy ions generate electron-hole pairs along a track, causing charge collection, analog voltage transients, and multi-cell upsets (MCUs).
  - Software fault injection abstracts this physical phenomenon into discrete architectural register upsets ($r_i \oplus 2^b$).
  - Physical cyclotron testing requires dedicated facility beam access (e.g., Texas A&M Cyclotron or Lawrence Berkeley National Lab) with delidded microcontrollers and custom vacuum chambers.
  - This project is positioned at NASA/ESA Technology Readiness Level (TRL) 4 (component validation in laboratory software environment), not TRL 8/9 (flight-proven).
- **Potential Follow-Up:** *"If software bitflips don't model physics, why is this paper useful?"*  
  *Answer:* Because even with radiation-hardened hardware, single-bit latch upsets still escape into CPU datapaths. If the software running on the satellite cannot handle an arithmetic error gracefully, the mission will fail regardless of hardware shielding.

---

### Q18: What is the true novelty of your work if algebraic invariants were already known?
- **Short Oral Answer (~35s):**  
  *"While algebraic invariants were explored for custom FPGA hardware by Paul et al. at CHES 2023, translating them into pure software on general-purpose microprocessors was considered impractical due to modular division costs in inverse transforms and memory overhead. Our novelty lies in three breakthroughs: first, deriving decoupled inverse Gentleman-Sande checks that eliminate modular division; second, inventing localized single-butterfly register rollback that avoids full decapsulation restarts; and third, formally proving and solving Theorem 1 on Twiddle Factor Blindness."*
- **Technical Deep Dive:**  
  - Novelty 1 (Decoupled Inverse GS Invariants): Eliminates runtime $\zeta^{-1}$ modular inversion in software, allowing all 11 decapsulation transforms ($9{,}856$ butterflies) to be monitored with only $+16.9\%$ latency overhead.
  - Novelty 2 (Microsecond Localized Rollback): Traditional software fault tolerance uses coarse DMR ($+99.33\%$ overhead). We rollback a single butterfly ($0.0101\%$ operation ratio) using CPU register snapshots.
  - Novelty 3 (Theorem 1 Proof & Solution): Formally identified that baseline invariant monitors are $100\%$ blind to twiddle factor corruption; designed and evaluated TFIB-Ref to achieve $100\%$ twiddle fault detection.
  - Novelty 4 (Zero Dynamic Memory): Pure in-place execution requiring 0 Bytes heap allocation, making it deployable on bare-metal aerospace microcontrollers.
- **Potential Follow-Up:** *"Why couldn't an engineer just use DMR if their CPU is fast enough?"*  
  *Answer:* On small satellites (CubeSats) and edge devices, the processor operates under strict thermal dissipation limits and battery constraints. Running cryptography twice doubles energy consumption, reducing operational life.

---

### Q19: Does your implementation maintain constant-time execution under fault conditions?
- **Short Oral Answer (~30s):**  
  *"Under fault-free execution, our implementation maintains constant-time execution because it uses branch-free arithmetic primitives and fixed loop structures. However, during active recovery, retrying a butterfly adds approximately 119 microseconds of execution time. Therefore, we explicitly do NOT claim constant-time behavior under active fault injection. In non-adversarial radiation environments, this variable latency is completely acceptable to preserve communication availability."*
- **Technical Deep Dive:**  
  - In fault-free conditions:
    - Compares ciphertexts using constant-time `mlk_ct_memcmp`.
    - Selects keys using branch-free `mlk_ct_cmov_zero`.
    - Invariant checks execute identical modular arithmetic across all $9{,}856$ butterflies.
  - Under active fault conditions:
    - If a mismatch occurs, lines 631–663 in `mlkem_fault_hooks.c` branch into the retry block.
    - Timing benchmarks in Table 2 of `RESEARCH_PROGRESS_MASTER.md` show that active recovery median latency is $292.92\,\mu\text{s}$ compared to $173.15\,\mu\text{s}$ fault-free (a $+119.77\,\mu\text{s}$ timing difference).
    - An adversary observing microsecond-level execution times could determine whether a retry occurred. Hence, we explicitly bound our threat model to non-adversarial environmental SEUs.
- **Potential Follow-Up:** *"Could you make the recovery path constant-time?"*  
  *Answer:* Yes. One could execute dummy recomputation cycles on every butterfly regardless of status, but that would impose a $\approx +70\%$ latency overhead on every execution. In space environments, saving energy on the 99.99% of clean executions is preferred.

---

### Q20: What happens if the fault strikes the monitor itself?
- **Short Oral Answer (~35s):**  
  *"We explicitly audited checker-logic corruption in our canonical campaign across 100 trials. If a transient fault strikes the checker logic, it causes a harmless false-alarm retry, restoring valid state. If a persistent defect strikes the checker logic, the monitor detects an unresolvable mismatch and escalates to safe fail-stop implicit rejection. In all 100 checker-fault trials, zero SDC occurred."*
- **Technical Deep Dive:**  
  - Evaluated in `tfib_experiments/test_step2c_countermeasure_independence.c` (Tests 3, 4, 6) and `tfib_trial_level_results.csv`:
    - `CHECKER_LOGIC_TRANSIENT`: 50/50 trials triggered false-alarm retry, verified clean on retry 1, and returned `GENUINE_RECOVERY` ($100.0\%$).
    - `CHECKER_LOGIC_PERSISTENT`: 50/50 trials failed retry verification, incremented `persistent_fail_count`, and returned `SAFE_FAIL_STOP` ($100.0\%$).
    - Across all 100 checker corruption trials: **0 SDC events observed**.
  - Outer Cryptographic Safety Net: Even if a corrupted checker erroneously forces decapsulation to commit bad polynomial values, the outer Fujisaki-Okamoto re-encryption comparison (`mlk_ct_memcmp`) will detect ciphertext mismatch and force implicit rejection.
- **Potential Follow-Up:** *"Is it possible for a fault to strike both the butterfly and the monitor in a way that perfectly cancels out?"*  
  *Answer:* That requires correlated multi-point fault injection. In non-adversarial physical radiation, the probability of two independent particle strikes hitting specific matching registers within the same nanosecond clock cycle is on the order of $10^{-14}$.

---

## Category G: Quantum Entanglement Theory Background

### Q21: Does ML-KEM utilize quantum entanglement, and why is entanglement studied in this project?
- **Short Oral Answer (~35s):**  
  *"No, ML-KEM does NOT use quantum entanglement. ML-KEM is a classical algorithm running on classical silicon microprocessors. We study quantum entanglement as foundational background to understand the quantum threat. Quantum computers use entangled qubits to execute Shor's algorithm, which solves prime factorization and breaks classical RSA and ECC. ML-KEM was designed specifically to replace vulnerable algorithms with lattice problems that quantum computers cannot solve."*
- **Technical Deep Dive:**  
  - Superposition ($|\psi\rangle = \alpha |0\rangle + \beta |1\rangle$) and Entanglement ($|\Psi_{AB}\rangle \neq |\psi_A\rangle \otimes |\psi_B\rangle$) are physical quantum mechanical phenomena.
  - Shor's algorithm (1994) uses quantum phase estimation and quantum entanglement across $2n$ qubits to compute the modular order $r$ of $a^r \equiv 1 \pmod N$.
  - Post-Quantum Cryptography (PQC) is entirely classical:
    - ML-KEM-768 operates on 16-bit integers modulo 3329.
    - It runs on standard ARM, x86, or RISC-V microprocessors.
    - Its mathematical security relies on the hardness of high-dimensional lattice problems (M-LWE), where quantum superposition and entanglement provide no known polynomial-time advantage.
- **Potential Follow-Up:** *"What is the difference between Post-Quantum Cryptography and Quantum Key Distribution (QKD)?"*  
  *Answer:* QKD (like BB84) requires specialized physical quantum hardware, single-photon emitters, and dedicated fiber-optic or laser lines to distribute keys using quantum mechanics. PQC uses purely mathematical algorithms that run on existing standard computers and network cables with no quantum hardware required.

---

## Category H: Publication & Future Roadmap

### Q22: What is the current publication status of the manuscript, and why Elsevier?
- **Short Oral Answer (~35s):**  
  *"Our manuscript in `paper/manuscript.md` has completed its Phase 2S final audit and is classified as 'Ready with Explicit Limitations'. It contains 7,500 words, 4 formal tables, and 24 verified references. We are targeting Elsevier journals like Acta Astronautica or Computer Networks because our research addresses the intersection of aerospace avionics constraints and cryptographic implementation security. Our immediate next step is converting the markdown manuscript into Elsevier's official `elsarticle` LaTeX format."*
- **Technical Deep Dive:**  
  - Manuscript Evolution: 10 unbroken milestone revisions audited from Phase 2C through Phase 2S (SHA-256: `bb6d138a463347153385c69a6e7f2bf133708cdb8738ba66a325e420d58e0b4d`).
  - Strict evidence calibration:
    - Separated active production trials ($N=400$) from campaign trials ($N=900$) and KAT conformance ($N=100$).
    - Qualified operation-ratio recomputation ($0.0101\%$) from execution-time overhead ($+16.9\%$).
    - Explicitly clarified software bitflips vs. physical radiation.
  - Missing Elsevier artifact: The LaTeX document class `elsarticle.cls` is currently not in the repository. We will download the official Elsevier template, map our Markdown sections to the LaTeX structure, and compile the submission PDF.
- **Potential Follow-Up:** *"What are the final experiments needed before submission?"*  
  *Answer:* The empirical cryptographic core is complete. The remaining tasks are formatting `elsarticle.cls` and conducting an initial port to an ARM Cortex-M4 microcontroller simulator to report embedded cycle counts.

---

## Quick Defense Verbal Cheat-Sheet (Keep This in Mind Tomorrow!)

1. **The Core Number Triad:**
   - **$100.0\%$ Recovery** on transient SEUs ($F4$, retry 1).
   - **$0$ SDC Events** across 300 active production trials ($95\%$ CI: $[0.00\%, 1.26\%]$) and 750 campaign trials ($\le 0.49\%$).
   - **$+16.9\%$ Overhead** under `-O3` ($129.51\,\mu\text{s}$ vs $110.77\,\mu\text{s}$) with **$0\text{ Bytes}$ heap allocation**.
2. **The Key Mathematical Invariant:**
   - Cooley-Tukey sum cancels $t$: $r_0 + r_1 \equiv 2u \pmod q$.
   - Difference reveals the fault: $r_0 - r_1 \equiv 2t \pmod q \implies 2e_t \not\equiv 0$.
3. **The Core Novelty:**
   - Decoupled Gentleman-Sande checks (zero modular divisions).
   - Microsecond localized register rollback ($\approx 0.0101\%$ recomputation ratio).
   - Theorem 1 characterization and Twiddle Factor Integrity Binding (TFIB-Ref).
4. **The Honest Boundary:**
   - Software register abstraction, **NOT** cyclotron silicon irradiation.
   - Non-adversarial environmental faults, **NOT** physical laser side-channel attacks.

