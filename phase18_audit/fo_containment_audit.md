# Workstream 4: Outer Fujisaki-Okamoto Containment Audit

**Auditor:** Independent Cryptographic Software Implementation & Security Auditor  
**Date:** October 2026  
**Audited Source File:** `algorithms/source_ref/mlkem/src/kem.c` (lines 403–525)  
**Standard Baseline:** NIST FIPS PUB 203 Section 7.3 (`ML-KEM.Decaps_internal`)  

---

## 1. Executive Summary

This audit examined the exact implementation of the Fujisaki-Okamoto (FO) ciphertext verification and implicit rejection pathway in `kem.c` to evaluate the manuscript's claim that the outer FO re-encryption check functions as an independent, second-tier containment boundary for arithmetic faults.

### Key Audit Findings:
1. **FIPS 203 Rejection Compliance:** The rejection key is computed strictly according to NIST FIPS 203 Section 7.3 as $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ via `mlk_hash_j()`, where $z$ is the private seed stored at the end of the secret key and $c$ is the input ciphertext.
2. **True Algorithmic Independence:** When an arithmetic fault evades local butterfly monitors (such as twiddle table corruption or harness-level snapshot corruption), the resulting decrypted message $m'$ is corrupted. Re-encrypting $m'$ produces a candidate ciphertext $c' \neq c$. The ciphertext comparison `mlk_ct_memcmp(ct, tmp)` detects this discrepancy and forces implicit rejection **completely independently of the local monitor's status counters**.
3. **Dual-Rail Verification Defense:** The reverse comparison loop (`kem.c:477-481`) effectively prevents software-level bit-corruption from flipping a non-zero `fail` flag to zero.
4. **Physical Attack Boundaries (Untested Scenarios):** The FO containment mechanism relies on the CPU correctly executing `mlk_ct_cmov_zero` and memory integrity for $z$. Physical instruction skipping (e.g., skipping the conditional move or branch) and physical glitching of the Keccak-f[1600] permutation remain untested and outside the software model.

---

## 2. Line-by-Line Code Analysis of the FO Pathway

### 2.1. Primary Ciphertext Comparison (`kem.c:466`)
```c
fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);
```
- Compares the received ciphertext `ct` ($1{,}088$ bytes) against candidate ciphertext `tmp` reconstructed via `mlk_indcpa_enc`.
- `mlk_ct_memcmp` evaluates the bitwise OR of differences across all bytes in constant time.

### 2.2. Dual-Rail Reverse Comparison Check (`kem.c:477-481`)
```c
uint8_t fail_chk = 0;
for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
  fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
}
fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);
```
- An independent loop iterates backward through the ciphertext buffers.
- If a transient upset corrupts the accumulator register during `mlk_ct_memcmp`, `fail != fail_chk` triggers line 497:
  ```c
  if (fail != fail_chk) {
    fail = 0xFF; /* Reverse dual-rail predicate mismatch forces implicit rejection */
  }
  ```

### 2.3. Monitor Counter Integration (`kem.c:486-494`)
```c
if (ntt_native_monitor_get_persistent_count() > 0 ||
    invntt_native_monitor_get_persistent_count() > 0)
{
  fail = 0xFF; /* Force implicit rejection regardless of internal_status pointer */
}
```
- If the arithmetic monitor flagged persistent failure, `fail` is forced to `0xFF` before key selection.

### 2.4. Rejection Key Generation and Constant-Time Selection (`kem.c:513-519`)
```c
/* Compute rejection key: tmp = z || c */
mlk_memcpy(tmp, sk + MLKEM_INDCCA_SECRETKEYBYTES - MLKEM_SYMBYTES, MLKEM_SYMBYTES);
mlk_memcpy(tmp + MLKEM_SYMBYTES, ct, MLKEM_INDCCA_CIPHERTEXTBYTES);
mlk_hash_j(ss, tmp, MLKEM_SYMBYTES + MLKEM_INDCCA_CIPHERTEXTBYTES);

/* Copy true key (kr) to return buffer (ss) if fail is 0; otherwise leave rejection key */
mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
```
- `mlk_hash_j` computes $\text{SHAKE256}(z \parallel c, 32)$.
- `mlk_ct_cmov_zero` copies the valid shared secret `kr` into `ss` if and only if `fail == 0`. If `fail != 0`, `ss` retains the freshly hashed rejection key.

---

## 3. Evaluated vs. Untested Containment Scenarios

| Fault Scenario | Exercised Mechanism | Observed Behavior | Containment Status |
|:---|:---|:---|:---:|
| **Transient Multiplier Fault ($F4$)** | Local NTT monitor rollback & retry | Local monitor repairs coefficient; authentic $c' == c$ reconstructed; valid key emitted | **CONTAINED (Tier 1 Recovery)** |
| **Persistent Multiplier Fault ($F5A, F5B$)** | Local monitor persistent escalation + FO check | `persistent_count > 0` forces `fail = 0xFF`; FO check also catches corrupted $c' \neq c$; emits $K_{\text{rej}}$ | **CONTAINED (Dual Protection)** |
| **Twiddle Factor Corruption ($C02, C05$)** | Local monitor blind; FO re-encryption active | Local monitor passes corrupted state; reconstructed ciphertext $c' \neq c$; FO forces $K_{\text{rej}}$ | **CONTAINED (Tier 2 Failsafe)** |
| **Harness Verifier Blindness ($H_1$)** | Local snapshot corrupted; FO re-encryption active | Local verifier passes corrupted state; FO check detects $c' \neq c$; forces $K_{\text{rej}}$ | **CONTAINED (Tier 2 Failsafe)** |
| **Ciphertext Input Bit-Flip ($C10$)** | Standard FIPS 203 implicit rejection | Re-encrypted $c'$ fails equality match; emits $K_{\text{rej}}$ matching reference oracle | **CONTAINED (NIST Conformance)** |
| **Single-Rail Comparator Glitch** | Dual-rail reverse comparison check | Forward and reverse flags disagree (`fail != fail_chk`); forces `fail = 0xFF` | **CONTAINED (Dual-Rail Defense)** |
| **Physical Laser Instruction Skip on `mlk_ct_cmov_zero`** | None (Hardware attack outside model) | Program counter skips branch or conditional move; potentially emits secret buffer | **UNTESTED / OUT OF SCOPE** |
| **Memory Corruption of Rejection Seed $z$** | None (Assumes honest RAM for secret key) | Emitted rejection key differs from standard $J(z \parallel c)$, causing protocol desynchronization | **UNTESTED / OUT OF SCOPE** |
| **Glitch during SHAKE256 Re-encryption Hash** | None (Hash sponge integrity assumed) | False ciphertext match or corrupted rejection key | **UNTESTED / OUT OF SCOPE** |

---

## 4. Conclusion on FO Containment

The claim that the outer Fujisaki-Okamoto re-encryption check functions as an independent failsafe boundary is **strongly supported by source inspection and empirical testing for internal algorithmic and arithmetic faults**. 

Specifically, in all cases where an arithmetic fault evaded the local butterfly monitor (such as twiddle table faults $C02/C05$ and snapshot corruption $H_1$), the downstream ciphertext discrepancy was reliably caught by `mlk_ct_memcmp`, preventing Silent Data Corruption. However, the manuscript must explicitly maintain the distinction that this containment applies to **computational arithmetic faults within the polynomial pipeline**, and does not constitute universal hardware fault immunity against physical laser instruction skipping or memory-bus tampering.
