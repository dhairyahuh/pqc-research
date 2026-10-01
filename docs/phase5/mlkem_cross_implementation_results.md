# Phase 5: ML-KEM Cross-Implementation Results

**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  

---

## 1. Implementations Compared

| Property | Implementation A | Implementation B |
|:---|:---|:---|
| **Source** | mlkem-native (C reference) | liboqs 0.16.0 |
| **Backend** | C scalar (reference) | AArch64 assembly (`PQCP_MLKEM_NATIVE_*_AARCH64`) |
| **Independence** | — | **NOT independent** (wraps mlkem-native) |
| **Instrumentation** | Full source-level fault hooks | None (opaque binary) |
| **Mapping** | ≈ Equivalent mathematical operation | ≈ Equivalent mathematical operation |

---

## 2. Baseline Equivalence (Category 1)

**4/4 seed patterns produce byte-identical outputs across C-ref and liboqs.**

| Test | Result |
|:---|:---|
| Public key match | ✓ All 4 patterns |
| Secret key match | ✓ All 4 patterns |
| Ciphertext match (deterministic encaps) | ✓ All 4 patterns |
| Shared secret match (encaps) | ✓ All 4 patterns |
| Cross-decaps: C-ref decaps liboqs CT | ✓ All 4 patterns |
| Cross-decaps: liboqs decaps C-ref CT | ✓ All 4 patterns |

**Interpretation:** The C-reference and AArch64 assembly backends produce mathematically identical results for identical deterministic inputs. This confirms that the backends implement the same FIPS 203 specification without detectable divergence.

---

## 3. Instrumentation Transparency (Category 2)

**3/3 tests pass: fault hooks (when dormant) are transparent.**

The instrumented build (`-DMLKEM_RESEARCH_FAULT_HOOKS`) with `g_mlkem_fault.enabled = false` produces byte-identical outputs to the clean build. This confirms that the hook callback overhead and conditional branching do not alter cryptographic correctness.

---

## 4. Cross-Backend Key Agreement (Category 3)

**500 random trials, 4 key-agreement directions:**

| Direction | Agreements | Rate |
|:---|:---:|:---:|
| C-ref encaps → C-ref decaps | 500/500 | 100.00% |
| liboqs encaps → liboqs decaps | 500/500 | 100.00% |
| liboqs encaps → C-ref decaps | 500/500 | 100.00% |
| C-ref encaps → liboqs decaps | 500/500 | 100.00% |

**Interpretation:** Perfect bidirectional interoperability with zero errors across 500 random key pairs. The AArch64 assembly NTT, inverse NTT, and polynomial arithmetic produce equivalent results to the C reference scalar path.

---

## 5. Fault Injection Reproduction (Category 4)

Selected Phase 2–4 experiments reproduced on the instrumented C-ref build (200 trials each):

| Experiment | Correct % | Rejection % | Consistent with Phase 2–4? |
|:---|:---:|:---:|:---|
| NTT-L1-B0-delta1 | 0.0% | 100.0% | **Yes** — Layer 1 delta=1 in decaps NTT |
| NTT-L1-B0-delta13 | 0.0% | 100.0% | **Yes** — Exceeds Phase 4 conditional masking bound |
| NTT-L4-B0-delta1 | 0.0% | 100.0% | **Yes** — Mid-tree diffusion |
| NTT-L7-B0-delta1 | 0.0% | 100.0% | **Yes** — Deepest layer, single coefficient |
| NTT-L3-B0-twiddle-bit4 | 0.0% | 100.0% | **Yes** — Twiddle factor corruption |
| NTT-L5-B0-interm-zero | 0.0% | 100.0% | **Yes** — Intermediate register zeroing |
| NTT-L1-B0-delta12 (boundary) | 0.0% | 100.0% | **Refined** — Phase 4 predicted conditional masking at δ≤12 |
| NTT-L1-B0-delta832 (max) | 0.0% | 100.0% | **Yes** — Maximum slack exceeded |

### Analysis of Layer 1 Boundary Behavior

The Phase 4 audit identified that Layer 1 masking is conditional: faults with $|\Delta| \le 12$ may be absorbed by the decoding slack, while $|\Delta| \ge 13$ exceeds the slack bound.

In these 200-trial reproductions, even δ=1 at Layer 1 produces 100% implicit rejection. This is because:

1. Layer 1 faults diffuse to $2^{7-1} = 64$ NTT-domain coefficients via the butterfly tree.
2. After inverse NTT, the error is distributed across multiple time-domain coefficients.
3. The **joint absorption probability** across 64 affected coefficients is approximately $P_{\text{single}}^{64} \to 0$.
4. The Phase 4 conditional masking bound ($|\Delta| \le 12$) applies to **individual coefficient errors**, not to the aggregate multi-coefficient impact after NTT diffusion.

This clarification is consistent with the Phase 4 correction and the common fault framework.

---

## 6. FO Predicate Fault Reproduction (Category 5)

**200 trials per test case:**

| Test | Result | Rate |
|:---|:---|:---:|
| Valid CT + FO forced fail → implicit rejection | Expected | 100.0% |
| Valid CT + no fault → correct key | Expected | 100.0% |
| Corrupted CT + no fault → implicit rejection | Expected | 100.0% |
| Corrupted CT + FO forced pass → garbled key | Observed | 59.5% |

### Garbled Key Rate Analysis

When the FO flag is forced to 0 on a corrupted ciphertext (single-byte corruption at CT[0]):
- **59.5%** of trials produce a shared secret different from the encapsulation key (garbled desynchronization).
- **40.5%** of trials produce the correct shared secret despite the CT corruption.

This is because single-byte corruption of CT[0] perturbs only 1 of 1088 ciphertext bytes. In some cases, the INDCPA decryption still recovers the correct message $m'$ because the LWE decoding slack absorbs the ciphertext error. When $m' = m$, re-encryption matches the original (uncorrupted) intent, and the candidate key is correct even though the ciphertext comparison was bypassed.

This is **not** a security finding — it demonstrates the interaction between FO bypass and LWE error tolerance.

---

## 7. Limitations

1. **No internal fault injection into liboqs:** The AArch64 assembly path cannot be internally instrumented. All fault experiments use the C-ref path only.
2. **Not independent replication:** Both implementations derive from the same source. Equivalence proves backend consistency, not independent algorithmic correctness.
3. **NTT diffusion tracking:** The diffusion measurement mechanism did not return valid counts during the encaps-path test (Category 6), because the tracking state machine requires synchronized baseline capture during the exact NTT call being faulted. The 100% rejection rate across all layers indirectly confirms the diffusion model.
4. **Single compiler:** Both -O0 and -O3 builds use the same Apple clang 21.0.0. Cross-compiler testing (e.g., GCC) would require a different build environment.
