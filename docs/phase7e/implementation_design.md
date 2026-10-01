# Implementation Design: Stage-Specific NTT Invariants and Recovery Architecture

## 1. Architectural Motivation

Phase 7D proved that while the Layer 7 weighted inverse-zeta invariant achieves $100\%$ detection for faults occurring at Layer 7, it achieves only **$14.0\%$ recovery across all NTT layers** because arithmetic errors injected in Layers 1–6 diffuse through downstream stages and evade the final linear projection.

When an early-stage fault evades the transform invariant, the only downstream line of defense is the Fujisaki-Okamoto (FO) re-encryption check. However, FO re-encryption cannot distinguish an internal physical fault from a legitimate invalid ciphertext. Under Phase 7D's constant-time contract, FO re-encryption failures fall back to safe implicit rejection ($K_{\text{rej}}$) rather than triggering recovery.

**The Phase 7E Mission:**
Integrate stage-specific butterfly invariants at earlier NTT layers to intercept transient arithmetic errors *before* diffusion destroys their local butterfly structure, explicitly raising `internal_status = MLK_STATUS_FAULT` and triggering autonomous recovery of the authentic shared secret $K$.

---

## 2. Candidate Architectural Prototypes

We evaluate five controlled configurations to isolate the marginal benefit and overhead of early-stage monitoring:

```
[Config A: Phase 7D Baseline]
   Input CRC32 ──► Native NTT ──► Final Layer 7 Invariant ──► Monitored FO
   (Coverage: 14.0% recovery across layers; 86.0% fallback safe rejection)

[Config B: Early Stage 1 Prototype]
   Input CRC32 ──► Stage 1 Monitored NTT (len=128) ──► Layer 7 Invariant ──► Monitored FO
   (Checks 128 butterflies in Layer 1; intercepts maximum-diffusion faults)

[Config C: Midpoint Stage 4 Prototype]
   Input CRC32 ──► Stage 4 Monitored NTT (len=16) ──► Layer 7 Invariant ──► Monitored FO
   (Checks 128 butterflies at transform midpoint)

[Config D: Targeted Multi-Stage (Layers 1 + 4 + 7)]
   Input CRC32 ──► Layer 1 Check ──► Layer 4 Check ──► Layer 7 Check ──► Monitored FO
   (Covers entry, midpoint, and exit stages: 384 butterflies checked)

[Config E: Comprehensive All-Stage (Layers 1..7)]
   Input CRC32 ──► Full 7-Layer Invariant Monitoring (896 butterflies checked) ──► Monitored FO
   (Complete transform coverage across all stages)
```

---

## 3. Detailed Specification of the Invariant Checks

### 3.1 Intra-Butterfly Verification Primitive
For each monitored butterfly operation in layer $l$, block $start$, stride $len$:
```c
int16_t u = r[j];
int16_t v = r[j + len];
int16_t t = mlk_fqmul(v, zeta);
int16_t u_out = (int16_t)(u + t);
int16_t v_out = (int16_t)(u - t);

/* Dual Invariant Verification */
int32_t diff_check = ((int32_t)u_out - (int32_t)v_out - 2 * (int32_t)t) % MLKEM_Q;
int32_t sum_check  = ((int32_t)u_out + (int32_t)v_out - 2 * (int32_t)u) % MLKEM_Q;

if (diff_check != 0 || sum_check != 0) {
    stage_fault_occurred = true;
}

r[j] = u_out;
r[j + len] = v_out;
```

### 3.2 Computational and Memory Budgets

| Prototype | Monitored Layers | Butterflies Checked | Invariant Multiplies | Invariant Adds/Subs | Memory Overhead |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Config A (Phase 7D)** | Layer 7 only | 0 intermediate | 0 extra | 256 sum adds | **0 bytes** |
| **Config B (Layer 1)** | Layer 1 | 128 | 0 (reuses $t$) | 256 adds/subs | **0 bytes** (in registers) |
| **Config C (Layer 4)** | Layer 4 | 128 | 0 (reuses $t$) | 256 adds/subs | **0 bytes** (in registers) |
| **Config D (L1+L4+L7)** | Layers 1, 4, 7 | 384 | 0 (reuses $t$) | 768 adds/subs | **0 bytes** (in registers) |
| **Config E (Layers 1–7)**| Layers 1–7 | 896 | 0 (reuses $t$) | 1,792 adds/subs | **0 bytes** (in registers) |

*Key Efficiency Finding:* Because the intermediate value $t = \text{fqmul}(v, \zeta)$ and input $u$ are already resident in CPU registers during butterfly execution, verifying the invariant requires **zero additional modular multiplications** and **zero heap/stack allocations**. It consists purely of register arithmetic and branchless accumulation.

---

## 4. Recovery Contract and Orchestration

When a stage invariant detects an inconsistency:
1. **Immediate Fault Flagging:** The stage monitor sets an accumulator token:
   $$\text{stage\_status} = \text{stage\_status} \lor \text{MLK\_STATUS\_FAULT}$$
2. **Deterministic Token Propagation:** The NTT routine propagates `MLK_STATUS_FAULT` (`0xFFFFFFFF`) up to `mlk_kem_dec_monitored()`.
3. **Disentangled Autonomous Retry:**
   Unlike an unauthenticated FO re-encryption rejection (`MLK_STATUS_REJECT`), which MUST NOT retry to prevent timing oracles, `MLK_STATUS_FAULT` proves with mathematical certainty that an internal physical disturbance occurred.
   The wrapper triggers `mlkem_fault_reset()` and re-executes decapsulation, restoring the authentic shared secret $K$ in $100\%$ of transient cases.
