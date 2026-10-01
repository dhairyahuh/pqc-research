# ML-DSA Mathematical and Implementation Mapping

**Standard:** NIST FIPS 204 (Module-Lattice-Based Digital Signature Standard)  
**Implementation:** `mldsa-native`  
**Git Provenance:** Commit `14d195a82dd27ed6bac35b403f5386bf43a893d3` (PQCA C90 / CBMC-verified)  
**Cross-Implementation Oracle:** `liboqs 0.16.0`  
**Compiler:** Clang (`-O3 -Wall -Wextra -std=c11`)  
**Target Architectures:** Native Darwin ARM64 / x86_64  

---

## 1. Algorithmic Overview & Structural Comparison with ML-KEM

ML-DSA (FIPS 204) implements the "Fiat-Shamir with Aborts" signature paradigm over the polynomial ring $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$ with prime modulus:
$$q = 8380417 = 2^{23} - 2^{13} + 1$$
This modulus satisfies $q \equiv 1 \pmod{512}$, permitting a complete 8-layer Number Theoretic Transform (NTT) splitting into 256 linear factors $(X - \zeta_i)$, unlike ML-KEM which uses $q = 3329 \equiv 1 \pmod{256}$ and stops at 7 layers.

```mermaid
graph TD
    subgraph Key Generation
        KG_Seed[Seed 32B] --> ExpandSK[Expand Mask / SHAKE256]
        ExpandSK --> MatrixA[ExpandA rho -> Matrix A]
        ExpandSK --> VectorS[Sample s1, s2 in [-eta, eta]]
        VectorS --> Committ0[Compute As1 + s2 = t1*2^d + t0]
        Committ0 --> PackKeys[Pack pk = rho||t1, sk = rho||K||tr||s1||s2||t0]
    end

    subgraph Signing Loop: Rejection Sampling
        Sign_Input[Message M, sk] --> DerivMu[mu = H tr || M]
        DerivMu --> DerivRho[rhoprime = H K || rnd || mu]
        DerivRho --> LoopStart[Attempt Loop: kappa = attempt * L]
        LoopStart --> SampleY[y = ExpandMask rhoprime, kappa]
        SampleY --> MatMultW[w = invNTT A * NTT y]
        MatMultW --> HighBitsW[w1 = HighBits w, Decompose w0]
        HighBitsW --> ChallengeH[ctilde = H mu || w1]
        ChallengeH --> SampleBall[c = SampleInBall ctilde]
        SampleBall --> CompZ[z = y + c * s1]
        CompZ --> NormCheckZ{||z||_inf >= gamma1 - beta?}
        NormCheckZ -- YES (Reject) --> LoopStart
        NormCheckZ -- NO (Pass) --> LowBitsCheck{||w0 - c*s2||_inf >= gamma2 - beta?}
        LowBitsCheck -- YES (Reject) --> LoopStart
        LowBitsCheck -- NO (Pass) --> MakeHint[h = MakeHint -c*t0, w - c*s2 + c*t0]
        MakeHint --> HintWeightCheck{Weight h > omega?}
        HintWeightCheck -- YES (Reject) --> LoopStart
        HintWeightCheck -- NO (Pass) --> SigEncode[sig = ctilde || z || h]
    end

    subgraph Verification
        Verify_Input[Message M, pk, sig] --> CheckNormZ{||z||_inf >= gamma1 - beta?}
        CheckNormZ -- FAIL --> RejectSig[INVALID_SIGNATURE]
        CheckNormZ -- PASS --> ReconstructMu[mu = H H pk || M]
        ReconstructMu --> UnpackHint[Unpack h, Validate Format]
        UnpackHint --> ReconstructW1[w1' = UseHint h, A*z - c*t1*2^d]
        ReconstructW1 --> RecomputeC[c2 = H mu || w1']
        RecomputeC --> FinalCmp{ct_memcmp ctilde == c2?}
        FinalCmp -- EQUAL --> AcceptSig[VALID_SIGNATURE]
        FinalCmp -- NOT EQUAL --> RejectSig
    end
```

---

## 2. Parameter Set Specifications (FIPS 204)

| Parameter | Algebraic Meaning | ML-DSA-44 | ML-DSA-65 | ML-DSA-87 |
|:---|:---|:---:|:---:|:---:|
| **Security Level** | NIST Post-Quantum Category | Category 2 (AES-128) | Category 3 (AES-192) | Category 5 (AES-256) |
| **Ring Modulus $q$** | Prime field modulus | 8,380,417 | 8,380,417 | 8,380,417 |
| **Ring Degree $n$** | Polynomial degree | 256 | 256 | 256 |
| **Matrix Dimension $K \times L$** | Rows $K$, Columns $L$ | $4 \times 4$ | $6 \times 5$ | $8 \times 7$ |
| **Secret Noise Bound $\eta$** | Support of $s_1, s_2$ | 2 | 4 | 2 |
| **Challenge Hamming Weight $\tau$** | Non-zero entries in $c$ | 39 | 49 | 60 |
| **Norm Bound $\beta$** | Bound on $\tau \cdot \eta$ | 78 | 196 | 120 |
| **Masking Bound $\gamma_1$** | Sampling range of $y$ | $2^{17} = 131,072$ | $2^{19} = 524,288$ | $2^{19} = 524,288$ |
| **Decomposition Bound $\gamma_2$** | Low-bits modulus | $(q-1)/88 = 95,232$ | $(q-1)/32 = 261,888$ | $(q-1)/32 = 261,888$ |
| **Max Hints $\omega$** | Max 1s in hint vector $h$ | 80 | 55 | 75 |
| **Public Key Size** | $\rho \parallel t_1$ (bytes) | 1,312 | 1,952 | 2,592 |
| **Secret Key Size** | $\rho \parallel K \parallel tr \parallel s_1 \parallel s_2 \parallel t_0$ (bytes) | 2,560 | 4,032 | 4,896 |
| **Signature Size** | $\tilde{c} \parallel z \parallel h$ (bytes) | 2,420 | 3,309 | 4,627 |
| **NTT Stages** | Complete binary tree layers | **8 Layers** | **8 Layers** | **8 Layers** |

---

## 3. Mathematical Operations to Implementation Mapping

| Mathematical Operation | Source Function | Source File | Concrete Data Structure | Fault-Relevant State | Observable Outcomes |
|:---|:---|:---|:---|:---|:---|
| **Forward NTT Butterfly** | `mld_ntt_butterfly_block` | `src/poly.c:216` | `int32_t r[256]` | `zeta`, $t = \text{fqmul}(r[j+\text{len}], \zeta)$, $r[j] \pm t$ | Diffuses to $2^{9-L}$ coefficients; signing retry or invalid signature |
| **Forward NTT Stage Loop** | `mld_ntt_layer` | `src/poly.c:266` | `int32_t r[256]` | Layer index $L \in \{1 \dots 8\}$, twiddle index $k$ | Stage-level diffusion divergence |
| **Inverse NTT Butterfly** | `mld_invntt_layer` | `src/poly.c:360` | `int32_t r[256]` | Intermediate $t = r[j]$, difference $r[j] - r[j+\text{len}]$, scaling | Time-domain coefficient dispersion |
| **Matrix-Vector Expansion** | `mld_polyvec_matrix_expand` | `src/polyvec.c:13` | `mld_polymat mat` | Pseudo-random matrix entries $\mathbf{A}_{i,j} \in R_q$ | Corrupted commitment $w$ |
| **Mask Sampling ($y$)** | `mld_yvec_init` | `src/poly_kl.c:15` | `mld_yvec y` | Uniform coefficient in $[-\gamma_1+1, \gamma_1]$ | Changes commitment $w$; shifts response $z$ |
| **Pointwise Mult & Accumulate** | `mld_polyvec_matrix_pointwise_montgomery_yvec` | `src/polyvec.c:85` | `mld_polyveck w0` | Accumulator $w = \mathbf{A} \cdot y$ in NTT domain | Fails norm checks; triggers rejection loop |
| **HighBits / LowBits Decompose** | `mld_polyveck_decompose_pack_w1` | `src/poly_kl.c:120` | `uint8_t w1_packed[]` | HighBits $w_1$, LowBits $w_0$ | Distorts commitment hash $\tilde{c}$ |
| **Challenge Hash ($\tilde{c}$)** | `mld_H` | `src/sign.c:57` | `uint8_t challenge_bytes[]` | SHAKE256 digest buffer $\tilde{c} \in \{0,1\}^{256}$ | Incompatible challenge polynomial $c$ |
| **Sample in Ball ($c$)** | `mld_poly_challenge` | `src/poly.c:512` | `mld_poly cp` | Trinary polynomial with $\tau$ non-zero coefficients | Incorrect sparse challenge representation |
| **Response Vector ($z = y + c s_1$)** | `mld_compute_pack_z` | `src/sign.c:58` | `mld_polyvecl z` | Response vector $z$, norm bound $\gamma_1 - \beta$ | Triggers norm rejection; retries signing |
| **Response Norm Check** | `mld_polyvecl_chknorm` | `src/polyvec.c:210` | Boolean return flag | Flag $z_{\text{invalid}} = (\|z\|_\infty \ge \gamma_1 - \beta)$ | Fault bypass produces invalid signature |
| **LowBits Norm Check** | `mld_poly_chknorm` | `src/poly.c:650` | Boolean return flag | Flag $w_{0,\text{invalid}} = (\|w_0 - c s_2\|_\infty \ge \gamma_2 - \beta)$ | Triggers rejection retry |
| **Hint Generation ($h$)** | `mld_pack_sig_h` / `mld_make_hint` | `src/packing.c:280` | Bit vector $h$ | Hint bits $h_{i,j} \in \{0, 1\}$, weight bound $\omega$ | Signature packaging failure / rejection |
| **Verification Norm Check** | `mld_polyvecl_chknorm` | `src/sign.c:1236` | `int ret` | Verification check on unpacked $z$ | Immediate `MLD_ERR_INVALID_SIGNATURE` (-6) |
| **Verification Hint Unpack** | `mld_sig_unpack_hints` | `src/packing.c:350` | `mld_poly tmp` | Decoded hint structure $h$ | Malformed hint returns invalid signature |
| **Verification Reconstruction** | `mld_poly_use_hint` | `src/poly.c:710` | `mld_poly w1` | Reconstructed high bits $w_1' = \text{UseHint}(h, \mathbf{A}z - c t_1 2^d)$ | Hash mismatch in verification |
| **Verification Decision Flag** | `mld_ct_memcmp` | `src/sign.c:1309` | `int cmp` | Constant-time memcmp between $\tilde{c}$ and $\tilde{c}_2$ | **ACCEPT (0)** vs **REJECT (-6)** |

---

## 4. Fundamental Cryptographic Failure Surfaces

1. **Rejection Sampling Vulnerability Surface:**
   - In signing, candidates failing $\|z\|_\infty < \gamma_1 - \beta$ or $\|r_0\|_\infty < \gamma_2 - \beta$ are normally rejected.
   - A computational fault in the norm calculation can force acceptance of an out-of-bounds candidate (producing a signature that fails verification or leaks information) or force infinite retries (Denial of Service / Single-Event Functional Interrupt).
2. **Deterministic vs. Hedged Signing Surfaces:**
   - Deterministic mode derives $\rho' = \text{SHAKE256}(K \parallel 0 \parallel \mu)$. A fault at the same location produces repeatable signatures and repeatable rejection counts.
   - Hedged (randomized) mode injects 32 bytes of fresh entropy: $\rho' = \text{SHAKE256}(K \parallel \text{rnd} \parallel \mu)$, varying attempts across runs.
3. **Verification Acceptance Decision Boundary:**
   - Verification evaluates a single boolean equality `cmp = ct_memcmp(c, c2, CTILDEBYTES)`.
   - A control-flow upset inverting `cmp` or bypassing the branch allows an invalid signature to be accepted (`INVALID -> ACCEPT`).
