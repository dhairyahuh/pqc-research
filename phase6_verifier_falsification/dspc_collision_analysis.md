# Phase 6: Mathematical Collision Analysis and Adversarial Stress-Testing of DSPC

**Auditor:** Skeptical Cryptographic Implementation Researcher  
**Date:** October 2026  
**Artifact:** `phase6_verifier_falsification/dspc_collision_analysis.md`  
**Dataset Reference:** `phase6_verifier_falsification/raw_trial_results.csv` (`F9`, `F10`, `F11`)

---

## 1. Mathematical Structure of the DSPC Checksum

The Dual-Snapshot Parity Checksum (DSPC) proposed in Phase 5 computes an authenticated token over the snapshot pair $(u_{\text{saved}}, v_{\text{saved}})$:
$$T(u, v) = ((uint32\_t)u) \oplus (((uint32\_t)v) \ll 16) \oplus C$$
where $u, v \in \mathbb{F}_2^{16}$ and $C = \text{0xA55A5AA5} \in \mathbb{F}_2^{32}$.

### 1.1 Linearity of the Checksum
The token generation function $T : \mathbb{F}_2^{16} \times \mathbb{F}_2^{16} \to \mathbb{F}_2^{32}$ is a strictly **affine transformation** over the vector space $\mathbb{F}_2^{32}$. For any perturbations $\Delta u, \Delta v \in \mathbb{F}_2^{16}$:
$$T(u \oplus \Delta u, v \oplus \Delta v) = T(u, v) \oplus \Delta u \oplus (\Delta v \ll 16)$$

---

## 2. Collision Analysis and Attack Surfaces

### 2.1 Single-Point Snapshot Perturbations (DSPC Strong Zone)
Consider an isolated fault altering only the snapshot operands $(u, v)$ while the stored token $T_{\text{saved}}$ remains intact:
$$\Delta T = T(u \oplus \Delta u, v \oplus \Delta v) \oplus T(u, v) = \Delta u \oplus (\Delta v \ll 16)$$
- The lower 16 bits of $\Delta T$ are determined exclusively by $\Delta u$.
- The upper 16 bits of $\Delta T$ are determined exclusively by $\Delta v$.
- For any non-zero perturbation $(\Delta u, \Delta v) \neq (0, 0)$, $\Delta T \neq 0$.

**Conclusion:** For single-point faults localized to snapshot memory, DSPC guarantees **zero internal collisions**.
- **Empirical Validation (`F11_DSPC_CLEAN_CORRECTION`):** In 100 trials of single-bit snapshot corruption, DSPC detected 100/100 faults, achieving **100.0% safe fail-stop rejection** [96.3%, 100.0%].

---

### 2.2 Correlated Multi-Bit Collisions (DSPC Failure Mode 1: `F9`)
Because $T$ is linear, it possesses zero cryptographic preimage or second-preimage resistance against multi-bit or multi-locus disturbances.

**Mathematical Construction of 2-Bit Collision:**
Let an attacker inject an SEU or laser pulse that flips bit $b \in [0, 15]$ of $u_{\text{saved}}$ ($\Delta u = 2^b$), and simultaneously flips bit $b$ of the stored token $T_{\text{saved}}$ ($\Delta T_{\text{saved}} = 2^b$):
1. Recomputed test token:
   $$T_{\text{test}} = T(u \oplus 2^b, v) = T(u, v) \oplus 2^b$$
2. Corrupted stored token:
   $$T_{\text{stored}} = T_{\text{saved}} \oplus 2^b = T(u, v) \oplus 2^b$$
3. Validation predicate check:
   $$T_{\text{test}} \oplus T_{\text{stored}} = (T(u, v) \oplus 2^b) \oplus (T(u, v) \oplus 2^b) = 0$$

**Empirical Result (`F9_DSPC_COLLISION_MULTI_BIT`):**
- 100 trials executed with correlated 2-bit flips.
- **DSPC Bypass Rate:** **100 / 100 trials (100.0%)** [96.3%, 100.0%].
- In all 100 trials, the checksum comparison passed unconditionally (`test_token == snap_token`).
- In all 100 trials, the corrupted snapshot was restored into polynomial memory, causing 100% false recovery declarations (H1).

---

### 2.3 Control-Flow Glitch Bypass (DSPC Failure Mode 2: `F10`)
If the adversary executes an instruction skip (e.g., clock glitch or EM pulse on the CPU program counter) over the branch instruction:
```c
if (test_token != snap_token) {
    g_ntt_mon.persistent_count++;
    return;
}
```
the validation check is bypassed entirely, regardless of checksum value.

**Empirical Result (`F10_DSPC_STATE_BYPASS`):**
- 100 trials executed with bypassed branch comparison.
- **Bypass Rate:** **100 / 100 trials (100.0%)** [96.3%, 100.0%].

---

### 2.4 Blind Spot: Post-Checksum Retry Glitches
DSPC acts as a pre-condition check on rollback; it does NOT monitor the retry computation itself. If an arithmetic glitch strikes during retry recomputation (such as the multiplier error demonstrated in `F7`), DSPC has already completed and offers zero protection.

---

## 3. Summary of Countermeasure Boundary Conditions

| Attack Scenario | DSPC Behavior | Protection Status | Residual Vulnerability |
|---|---|---|---|
| **Single-Bit Snapshot Flip** | Detects token mismatch | **100% Protected** (100/100 safe rejects) | None under isolated single-bit model. |
| **Correlated 2-Bit Fault** | Collision occurs: $\Delta T = \Delta u$ | **0% Protected** (100/100 bypassed) | Vulnerable to 2-bit correlated faults. |
| **Control-Flow Instruction Skip** | Branch check bypassed | **0% Protected** (100/100 bypassed) | Vulnerable to instruction skip glitches. |
| **Fault During Checksum Calc** | Generates valid token for corrupt data | **0% Protected** | Checksum calculation window unprotected. |
| **Retry Arithmetic Glitch** | DSPC already completed | **0% Protected** | Relies on flawed verifier recomputation. |

### Verdict on DSPC:
DSPC effectively eliminates the unmitigated single-bit stack vulnerability identified in Phase 5, but researchers must NOT claim general fault tolerance. Against multi-bit correlated disturbances or control-flow glitches, linear software checksums provide zero barrier.
