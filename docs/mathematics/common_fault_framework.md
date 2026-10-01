# Common Mathematical Fault Framework for Post-Quantum Lattice Cryptography

**Standards:** NIST FIPS 203 (ML-KEM) & NIST FIPS 204 (ML-DSA)  
**Document Version:** 1.0.0-FRAMEWORK  
**Date:** October 1, 2026  
**Status:** FORMAL RESEARCH SPECIFICATION  

---

## 1. Scope and Objective

This framework defines a unified mathematical and implementation-level representation of computational and data faults across lattice-based Post-Quantum Cryptographic (PQC) schemes. 

It establishes an 8-stage formal pipeline separating the physical or simulated disturbance from its high-level security consequence:

$$\text{Operation } (\mathcal{O}) \longrightarrow \text{State } (\mathcal{S}) \longrightarrow \text{Fault } (\mathcal{F}) \longrightarrow \text{Perturbation } (\Delta) \longrightarrow \text{Propagation } (\mathcal{P}) \longrightarrow \text{Detection/Rejection } (\mathcal{D}) \longrightarrow \text{Outcome } (\mathcal{Y}) \longrightarrow \text{Security Impact } (\mathcal{X})$$

Crucially, this framework avoids forcing artificial mathematical symmetry onto operations that are structurally disparate (e.g., lossy ciphertext compression vs. exact signature hint generation; deterministic Fujisaki-Okamoto re-encryption vs. iterative rejection sampling).

---

## 2. Algebraic Setting & Common Substrate

Both ML-KEM and ML-DSA operate over cyclotomic quotient polynomial rings of the form:

$$R_q = \mathbb{Z}_q[X] / (X^n + 1)$$

where $n = 256$ is invariant. The underlying parameters differ as follows:

| Parameter | ML-KEM (FIPS 203) | ML-DSA (FIPS 204) | Mathematical Consequence |
|:---|:---:|:---:|:---|
| **Modulus $q$** | $3329$ | $8,380,417$ | $q_{\text{DSA}} \approx 2517 \times q_{\text{KEM}}$ |
| **Splitting Condition** | $q \equiv 1 \pmod{256}$, but $q \not\equiv 1 \pmod{512}$ | $q \equiv 1 \pmod{512}$ | ML-DSA factors into linear terms; ML-KEM factors into quadratic terms. |
| **NTT Factorization** | $X^{256} + 1 = \prod_{i=0}^{127} (X^2 - \zeta^{2i+1})$ | $X^{256} + 1 = \prod_{i=0}^{255} (X - \zeta^{2i+1})$ | ML-KEM uses 7 layers; ML-DSA uses 8 layers. |
| **NTT Base Multiplication** | Degree-1 polynomial multiplication modulo $(X^2 - \zeta^{2r+1})$ | Pointwise scalar multiplication modulo $q$ | ML-KEM requires 4 multiplications and 2 additions per block; ML-DSA requires 1 multiplication. |
| **Vector Dimension $k \times l$** | $k \in \{2, 3, 4\}$ | $k \times l \in \{4\times 4, 6\times 5, 8\times 7\}$ | Matrix dimension and accumulator depth. |

---

## 3. The 8-Stage Fault Pipeline

Every fault event in this research is uniquely characterized by a tuple across eight strictly defined stages:

### Stage 1: Algorithm-Level Operation ($\mathcal{O}$)
The standardized cryptographic procedure executing when the disturbance occurs:
- **ML-KEM:**
  - $\text{KeyGen}(d, z)$
  - $\text{Encaps}(pk, m)$
  - $\text{Decaps}(sk, c) \equiv \text{INDCPA.Dec}(sk, c) + \text{INDCPA.Enc}(pk, m') + \text{FO.Verify}$
- **ML-DSA:**
  - $\text{KeyGen}(\xi)$
  - $\text{Sign}(sk, M) \equiv \text{MatrixExpand} + \text{SampleCandidate } \mathbf{y} + \text{Commit } \mathbf{w}_1 + \text{RejectionLoop}(\mathbf{z}, \mathbf{w}_0, \mathbf{h})$
  - $\text{Verify}(pk, M, \sigma) \equiv \text{Reconstruct } \mathbf{w}_1 + \text{HashChallenge } c_2 + \text{Compare } (c \stackrel{?}{=} c_2)$

### Stage 2: Implementation-Level State ($\mathcal{S}$)
The concrete C data structure, CPU register, or memory buffer holding the operand:
- Polynomial coefficient array (`int16_t coeffs[256]` or `int32_t coeffs[256]`)
- Intermediate butterfly registers (`int32_t t`, `int16_t r[j]`)
- Accumulator registers (`int32_t t[0]`, `int64_t acc`)
- Serialized byte buffers (`uint8_t ct[1088]`, `uint8_t sig[3309]`, `uint8_t sk[4032]`)
- Control flags and predicate variables (`int fail`, `int cmp`, `int norm_failed`)

### Stage 3: Fault Injection Location ($\mathcal{L}$)
The precise code execution point, defined by source file, line number, and execution context:
$$\mathcal{L} = (\text{Module}, \text{Function}, \text{Instruction/Hook}, \text{Sub-Loop Index})$$

Categorized under the project taxonomy:
- `LOCUS_INPUT`: Pre-operation input buffer.
- `LOCUS_TWIDDLE`: Multiplicative root of unity parameter $\zeta$.
- `LOCUS_INTERMEDIATE`: Internal product or accumulator register before reduction.
- `LOCUS_OUTPUT`: Post-arithmetic destination register.
- `LOCUS_PREDICATE`: Boolean condition or comparison variable.

### Stage 4: Fault Magnitude, Duration, and Type ($\mathcal{F}$)
The mathematical transformation applied to the targeted state:
$$x' = f(x, \Delta)$$

Types:
1. **Additive Glitch:** $x' = x + \Delta \pmod q$
2. **Single Bit Flip:** $x' = x \oplus (1 \ll b)$
3. **Random Byte Corruption:** $x'[i] = \text{rand8}()$
4. **Zeroing / Stuck-At:** $x' = 0$
5. **Predicate Inversion:** $x' = (x == 0) ? 1 : 0$

Duration:
- **Transient (SEU):** Perturbs exactly one operational cycle or loop iteration.
- **Persistent (MBU / Hard Fault):** Remains in memory across all subsequent iterations or retries.

### Stage 5: Propagation Mechanics ($\mathcal{P}$)
The mathematical transfer function governing how the perturbation spreads through subsequent transformations:
$$\mathcal{P}: \Delta \longrightarrow \Delta_{\text{out}}$$

1. **Radix-2 Butterfly Tree Diffusion:**
   - In Cooley-Tukey forward NTT, a fault at layer $L$ propagates across a strict binary tree:
     $$N_{\text{diffused}}^{\text{single}}(L) = 2^{L_{\text{max}} - L}, \quad N_{\text{diffused}}^{\text{shared}}(L) = 2^{L_{\text{max}} - L + 1}$$
     where $L_{\text{max}} = 7$ for ML-KEM and $L_{\text{max}} = 8$ for ML-DSA.
   - For any non-modular-zero additive perturbation $\Delta \not\equiv 0 \pmod q$, all $N$ descendant coefficients are non-zero.
2. **Inverse NTT Scaling & Linear Dispersion:**
   - In inverse NTT, scaling by $n^{-1} \pmod q$ disperses time-domain errors across the entire polynomial ring basis.
3. **Lossy Compression Quantization:**
   - $\text{Compress}_d(x + \Delta)$ absorbs perturbations if $x + \Delta$ remains within the boundary margins:
     $$\Delta \in [-M^-(x), M^+(x)]$$
   - For diffused multi-coefficient vectors, joint absorption scales exponentially:
     $$P(\text{joint}) = \prod_{i=1}^W P(\text{absorbed}(e_i)) \approx P_{\text{single}}^W \longrightarrow 0$$
4. **Norm Expansion:**
   - In ML-DSA, arithmetic errors in $\mathbf{y}$ or $\mathbf{A}\mathbf{z}$ translate directly into infinity-norm inflation:
     $$\|\mathbf{z}'\|_\infty = \|\mathbf{y} + \Delta + c \mathbf{s}_1\|_\infty \le \|\mathbf{z}\|_\infty + \|\Delta\|_\infty$$

### Stage 6: Detection, Containment, or Rejection ($\mathcal{D}$)
The algorithmic or system mechanism that intercepts the perturbed state:
1. **Input Validation:** Modulus checks and hash validation on public keys ($pk, H(pk)$).
2. **Infinity-Norm Bounding:** ML-DSA rejection sampling checks:
   $$\text{CheckNorm}(\mathbf{z}, \gamma_1 - \beta) \stackrel{?}{=} 0, \quad \text{CheckNorm}(\mathbf{w}_0, \gamma_2 - \beta) \stackrel{?}{=} 0$$
3. **Deterministic Re-Encryption Verification:** ML-KEM Fujisaki-Okamoto check:
   $$\text{fail} = \text{ct\_memcmp}(c, c')$$
4. **Challenge Hash Commitment:** ML-DSA verification hash check:
   $$\text{cmp} = \text{ct\_memcmp}(c, H(\mu, \mathbf{w}_1))$$
5. **Decoding Slack Absorption:** Natural algebraic masking in ML-KEM message decoding:
   $$\|e_{\text{time}}\|_\infty \le \lfloor q/4 \rfloor = 832.25$$

### Stage 7: Observable Implementation Outcome ($\mathcal{Y}$)
The concrete program execution result observed at the API boundary:
- `CORRECT_OUTPUT`: Nominal execution output produced (fault completely absorbed or masked).
- `IMPLICIT_REJECTION`: ML-KEM decapsulation completes cleanly but outputs pseudorandom key $K_{\text{rej}} = H(z, c)$.
- `EXPLICIT_REJECTION`: ML-DSA verification returns `MLD_ERR_INVALID_SIGNATURE` (-1).
- `SIGNING_RETRY`: ML-DSA signing loop discards candidate attempt and increments counter.
- `ATTEMPT_EXHAUSTION_DOS`: ML-DSA signing loop reaches attempt limit (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`).
- `DECISION_OVERRIDE`: Invalid signature or payload accepted due to Boolean decision flag inversion.
- `GARBLED_PAYLOAD_MISMATCH`: Corrupted candidate shared secret selected ($K_{\text{cand}} \neq K_{\text{ground}} \neq K_{\text{rej}}$).
- `INPUT_VALIDATION_ERROR`: Function terminates early with error return code.
- `PROCESS_CRASH` / `TIMEOUT`: Segmentation fault, illegal memory access, or non-terminating loop.

### Stage 8: Security Consequence ($\mathcal{X}$)
The cryptographic and mission impact:
- **No Impact:** State remains mathematically identical to nominal execution.
- **Availability Loss (Denial of Service):** Authentication or key establishment fails, requiring retry or session termination.
- **Silent Desynchronization:** Decapsulating entity produces an out-of-sync session key without notifying the sender or generating telemetry.
- **Integrity Violation (Unauthenticated Command Execution):** Simulated verification bypass allows unauthorized or corrupted commands to pass the verification barrier.
- **Side-Channel Leakage Risk:** Out-of-bounds signature emission violates zero-knowledge distribution invariance, exposing private key coefficients to lattice analysis.

---

## 4. Cross-Algorithm Structural Contrast

```mermaid
graph TD
    subgraph ML-KEM Pipeline
        K1[Ciphertext c] --> K2[INDCPA.Dec: InvNTT]
        K2 --> K3{e_time < q/4?}
        K3 -- Yes: Slack Masked --> K4[m' = m]
        K3 -- No: Error --> K5[m' != m]
        K4 --> K6[Re-encrypt: c' = c]
        K5 --> K7[Re-encrypt: c' != c]
        K6 --> K8[FO Verify: fail = 0]
        K7 --> K9[FO Verify: fail = 1]
        K8 --> K10[K = H(Kcand, H(c)) -> Correct]
        K9 --> K11[K = H(z, c) -> Implicit Rejection]
    end

    subgraph ML-DSA Pipeline
        D1[Signing Attempt y] --> D2[NTT + PolyMul]
        D2 --> D3[Response z = y + c*s1]
        D3 --> D4{Norm Check: ||z|| < gamma1-beta?}
        D4 -- Fail: Out of Bounds --> D5{Attempt < Limit?}
        D5 -- Yes --> D1
        D5 -- No --> D6[Fail-Closed: Attempt Exhaustion DoS]
        D4 -- Pass: In Bounds --> D7[Emit Signature]
        D7 --> D8[Verify: Reconstruct w1]
        D8 --> D9{Arithmetic Error in w1?}
        D9 -- Yes: Any Delta >= 1 --> D10[H(mu, w1) != c -> Explicit Rejection]
        D9 -- No: Clean Math --> D11[H(mu, w1) == c -> Explicit Accept]
    end
```

---

## 5. Formal Definitions for Implementation-Level Modeling

### Definition 1 (Decoding Slack Margin)
In ML-KEM message decoding ($\text{Compress}_1(w)$), the decoding margin for bit $i \in \{0, \dots, 255\}$ is:
$$\mu_i = \left| w_i - \frac{q}{4} \right| \pmod{\frac{q}{2}}$$
The nominal decoding slack is bounded by $\tau = \lfloor q/4 \rfloor = 832$. A computational error $e \in R_q$ flips bit $i$ if and only if:
$$|e_i| > \tau - |e_{\text{nominal}, i}|$$

### Definition 2 (Rejection Sampling Norm Barrier)
In ML-DSA signing, the norm verification operator $\mathcal{N}: R_q^l \to \{0, 1\}$ is defined as:
$$\mathcal{N}(\mathbf{z}) = \begin{cases} 0 & \text{if } \|\mathbf{z}\|_\infty < \gamma_1 - \beta \\ 1 & \text{if } \|\mathbf{z}\|_\infty \ge \gamma_1 - \beta \end{cases}$$
An arithmetic perturbation $\Delta \in R_q^l$ forces an attempt retry if $\mathcal{N}(\mathbf{z} + \Delta) = 1$. If the implementation's retry budget is $R_{\text{max}}$, a persistent perturbation forces $\text{Sign} \to \text{MLD\_ERR\_SIGN\_ATTEMPTS\_EXHAUSTED}$.

### Definition 3 (Verification Hash Barrier)
In ML-DSA verification, the commitment comparison operator $\mathcal{V}: \{0, 1\}^* \to \{0, 1\}$ is:
$$\mathcal{V}(\mathbf{w}_1, \mu, c) = \text{ct\_memcmp}(c, H(\mu \parallel \mathbf{w}_1))$$
Because $H$ is modeled as a random oracle, for any perturbed commitment $\mathbf{w}_1' \neq \mathbf{w}_1$:
$$\Pr[\mathcal{V}(\mathbf{w}_1', \mu, c) = 0] = 2^{-256}$$
ML-DSA verification therefore possesses zero arithmetic slack.

---

## 6. Summary

This common framework establishes rigorous mathematical boundaries for both schemes:
1. **ML-KEM** possesses continuous algebraic slack that completely masks small arithmetic errors ($|\Delta| \le 12$) in decapsulation, failing closed to pseudorandom keys when errors exceed the slack.
2. **ML-DSA** possesses zero verification slack, relying on discrete rejection sampling during signing and collision-resistant random oracles during verification to fail closed.
