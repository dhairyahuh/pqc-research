# Experimental Methodology and Metrics Framework

## 1. Experimental Protocol

To guarantee scientific rigor, auditability, and reproducibility, all experiments adhere to a four-stage protocol:

```text
[Stage 1: Manifest Definition]
  Define experiment configuration YAML:
  - Algorithm & security level (e.g. ML-KEM-768, ML-DSA-65)
  - Fault model (SEU bit-flip, burst, transient, persistent)
  - Target abstraction level (Input, Memory Buffer, Intermediate State)
  - PRNG master seed (fixed for deterministic replay)
  - Iteration count (N >= 10,000 for statistical significance)

[Stage 2: Deterministic Execution]
  For each iteration i in 0..N-1:
    1. Seed local cryptographic state generator
    2. Generate legitimate inputs/keys
    3. Trigger scheduled fault at target coordinate
    4. Execute cryptographic primitive to completion / exception
    5. Capture exact execution latency, memory delta, and exit code

[Stage 3: Multi-Criteria Outcome Classification]
  Evaluate output against golden ground truth:
  - If output matches ground truth exactly -> CORRECT
  - If exception / crash / abort -> CRASH
  - If error returned by algorithm / check -> DETECTED_FAILURE
  - If error caught and recomputed successfully -> RECOVERED
  - If completed with no error but output != ground truth -> SILENT_FAILURE (SDC)

[Stage 4: Statistical Synthesis & Confidence Intervals]
  Calculate metrics with 95% Wilson score confidence intervals.
  Emit structured JSON and CSV artifacts.
```

---

## 2. Formal Mathematical Metrics

### Fault Detection Rate (FDR)
$$\text{FDR} = \frac{N_{\text{detected}}}{N_{\text{injected}}} \times 100\%$$
Measures the proportion of injected faults that are explicitly flagged by error-checking mechanisms before corrupt data is committed.

### Silent Failure Rate (SFR) / Silent Data Corruption (SDC)
$$\text{SFR} = \frac{N_{\text{silent\_incorrect}}}{N_{\text{injected}}} \times 100\%$$
Critical safety metric for space systems: measures the rate at which faults silently alter cryptographic keys, ciphertexts, or signatures without detection.

### Recovery Rate (RR)
$$\text{RR} = \frac{N_{\text{recovered}}}{N_{\text{detected}}} \times 100\%$$
Measures the effectiveness of autonomous correction (e.g., algorithmic retry, rollback checkpointing) once a fault has been detected.

### Total Failure Rate (TFR)
$$\text{TFR} = \frac{N_{\text{silent\_incorrect}} + N_{\text{crash}} + N_{\text{detected\_unrecovered}}}{N_{\text{injected}}} \times 100\%$$

### Performance Overhead (PO)
$$\text{PO} = \frac{T_{\text{protected}} - T_{\text{baseline}}}{T_{\text{baseline}}} \times 100\%$$
Where $T$ is the median execution time measured over $M \ge 1,000$ runs.

### Memory Overhead (MO)
$$\text{MO} = \frac{\text{Mem}_{\text{protected}} - \text{Mem}_{\text{baseline}}}{\text{Mem}_{\text{baseline}}} \times 100\%$$
Measures peak heap and stack RAM consumption delta.

---

## 3. Four-Level Abstraction Hierarchy

| Level | Abstraction Domain | Injection Targets | Experimental Objective |
| :--- | :--- | :--- | :--- |
| **Level 1** | Input & Boundary | Public key, Secret key, Ciphertext, Signature, Message buffer | Baseline sanity, protocol desynchronization, boundary parsing validation |
| **Level 2** | Memory Buffers | Polynomial coefficient arrays, NTT output buffers, matrix vectors | Static SRAM bit upsets, radiation degradation of working memory |
| **Level 3** | Intermediate States | Butterfly calculations, modular reduction results, rejection sample values | Dynamic transient arithmetic disturbances, ALU logic faults |
| **Level 4** | Control & Execution | Loop counter bounds, branch predicates, instruction skips | SEFI simulation, control flow disruption, timing perturbation |
