# Formal Research Questions and Hypotheses

## Primary Research Question
> **How do standardized post-quantum cryptographic implementations behave under controlled computational and memory faults representative of fault conditions that occur in space-based computing environments, and can lightweight algorithmic resilience mechanisms mitigate critical failure modes with minimal system overhead?**

---

## Secondary Research Questions (RQs)

### RQ1: Space Fault Mapping & Relevance
*What computational and memory fault representations are most faithful to space-radiation Single Event Effects (SEEs) when applied to software-based lattice cryptographic implementations?*
- **Hypothesis 1:** Single Event Upsets (SEU) modeled as single-bit flips and burst memory upsets disproportionately impact operations with wide intermediate data structures (e.g., polynomial vectors with $k \times 256 \times 16$ bits) compared to compact scalar operations.

### RQ2: Differential Algorithmic Response
*How do key encapsulation mechanisms (ML-KEM) and digital signature algorithms (ML-DSA) differ fundamentally in their sensitivity and response to transient memory and computational faults?*
- **Hypothesis 2:** ML-DSA exhibits significantly greater structural vulnerability during signing due to its rejection sampling loops and strict infinity-norm bound checks ($\|z\|_\infty < \gamma_1 - \beta$), whereas ML-KEM decapsulation exhibits higher rates of Silent Data Corruption (SDC) due to the Fujisaki-Okamoto implicit rejection masking failure indications.

### RQ3: Vulnerability Distribution Across Cryptographic Sub-Routines
*Which specific cryptographic sub-routines (e.g., NTT butterfly stages, Keccak sponge squeezes, rejection sampling, modular reductions, serialization) are most sensitive to faults?*
- **Hypothesis 3:** Corruptions in the early stages of the Number Theoretic Transform (NTT) or in the Keccak state diffuse rapidly across all output coefficients, whereas corruptions during polynomial coefficient compression/decompression cause localized, bounded perturbations.

### RQ4: Failure Mode Taxonomy and Silent Failure Prevalence
*What is the quantitative distribution of fault outcomes across the five standardized failure classifications:*
1. **CORRECT:** Fault had no effect on functional output (e.g., fault in unused padding or masked bit).
2. **DETECTED_FAILURE:** Fault detected by algorithm or system integrity checks and cleanly reported.
3. **RECOVERED:** Fault detected and autonomously corrected via retry or checkpoint restoration.
4. **INCORRECT_OUTPUT / SILENT_FAILURE (SDC):** Computation terminates with exit code 0 but produces an invalid or desynchronized cryptographic output.
5. **CRASH / EXCEPTION:** Segmentation fault, bus error, memory abort, or illegal instruction.

### RQ5: Efficacy of Selective Algorithmic Resilience
*Can lightweight algorithmic resilience mechanisms (such as selective polynomial checksumming, NTT identity checking, and norm sanity boundaries) achieve high fault detection rates without incurring full duplex (200%) execution overhead?*
- **Hypothesis 5:** By protecting only the top 20% most vulnerable sub-routines identified in RQ3 (selective redundancy), we can achieve >95% fault detection with <30% computational and memory overhead.

### RQ6: SWaP-C Overhead Quantification
*What are the precise computational latency, memory footprint, and power/throughput penalties introduced by these resilience mechanisms across space-grade processor architectures?*
