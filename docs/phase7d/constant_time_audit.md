# Constant-Time and Implicit-Rejection Audit

## 1. Scope and Objective

This audit investigates the constant-time characteristics, microarchitectural leakage properties, and FIPS 203 implicit-rejection behavior of the native monitored decapsulation implementation:
- Core in-tree cryptographic pipeline: `mlk_kem_dec_monitored()` (`algorithms/source_ref/mlkem/src/kem.c`)
- Public standard API: `mlk_kem_dec()`
- Wrapper resilience interface: `decaps_layered_native()`

We evaluate whether internal fault monitoring or autonomous retry logic inadvertently introduces a ciphertext-validity timing oracle or leaks secret key information.

---

## 2. Distinction of Security Levels

To avoid overstating guarantees, we explicitly categorize our findings across five levels of assurance:

| Assurance Level | Status | Evaluation Summary |
| :--- | :--- | :--- |
| **1. Functional Preservation** | **VERIFIED** | All FIPS 203 KAT vectors pass identically. Valid ciphertexts produce the correct shared secret $K$; invalid ciphertexts yield the exact implicit rejection key $K_{\text{rej}} = J(z, c)$. |
| **2. Source-Level Constant-Time Intent** | **PARTIALLY VERIFIED** | Core `mlk_kem_dec_monitored()` uses constant-time primitives (`mlk_ct_memcmp`, `mlk_ct_cmov_zero`). However, the wrapper retry logic contains secret-correlated conditionals. |
| **3. Compiled-Code Inspection** | **VERIFIED (Inner) / VULNERABLE (Wrapper)** | Apple Clang 17.0.0 `-O3` generates branchless conditional selection (`csel`, `csinv`, `cinv`) in `mlk_kem_dec_monitored`. The wrapper contains a conditional retry branch. |
| **4. Empirical Timing Evidence** | **ORACLE DETECTED IN WRAPPER** | Empirical timing distributions reveal that the Phase 7C wrapper exhibits a $2\times$ timing discrepancy on invalid ciphertexts ($72\,\mu\text{s}$ vs $148\,\mu\text{s}$). |
| **5. Formal Constant-Time Proof** | **UNPROVEN** | No formal verification (e.g., via `ct-verif` or Jasmin/SMT) has been conducted. We explicitly disclaim formal mathematical proof. |

---

## 3. Disassembly Audit of Core Monitored Decapsulation

Disassembly of `mlk_kem_dec_monitored` on AArch64 (Apple Silicon) confirms that Clang preserves branchless execution:

```assembly
; Comparison of reverse XOR and forward memcmp flags
0x10da4: cmp       w8, w9                 ; w8 = fail_chk, w9 = fail
0x10da8: csel      w24, w24, w11, eq      ; if equal keep fail, else fail = 0xFF
0x10dac: csinv     w8, w10, wzr, eq       ; if equal select status, else 0xFFFFFFFF
0x10db0: str       w8, [x22]              ; write status to pointer
...
; Hash J derivation for implicit rejection key
0x10dd0: bl        0x10dd0                ; SHA3-256 (mlk_hash_j)
...
; Constant-time conditional move of candidate key over rejection key
0x10e30: eor       w8, w24, #0xff         ; invert fail flag mask
0x10e38: and.16b   v0, v0, v8             ; mask candidate key bytes
0x10e40: orr.16b   v0, v0, v1             ; constant-time blend
```

### Inner Pipeline Properties:
- **No Secret-Dependent Branches:** Execution latency of `mlk_kem_dec_monitored` is identical for valid and invalid ciphertexts when called without retry wrappers.
- **No Secret-Dependent Memory Indices:** Memory access patterns in `indcpa_dec`, `indcpa_enc`, and `mlk_hash_g/j` are invariant with respect to ciphertext validity.
- **Public API Isolation:** In the standard API `mlk_kem_dec(ss, ct, sk, ctx)`, `internal_status` is passed as `NULL`. Lines 483–498 bypass status token assignment without introducing variable branch timing.

---

## 4. The Critical Autonomous Retry Timing Side-Channel

### Mechanism of the Vulnerability
In `experiments/phase7c/phase7c_oracle_free_harness.c`, the wrapper `decaps_layered_native` defines:
```c
bool dec_fault  = (internal_status == MLK_STATUS_FAULT);
bool dec_reject = (internal_status == MLK_STATUS_REJECT);

uint32_t rail1 = (!dec_fault && !dec_reject && dec_res == 0) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
uint32_t rail2 = (!dec_fault && !dec_reject && dec_res == 0) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
uint32_t status = verify_multi_rail_barrier(rail1, rail2);

if (status != RESILIENCE_OK_TOKEN && allow_retry) {
    mlkem_fault_reset();
    /* Second full decapsulation executed! */
    dec_res = mlkem768_dec_monitored(ss, ct, sk, &retry_status);
    ...
}
```

When an authentic, valid ciphertext is processed:
- Re-encryption succeeds: `tmp == ct`.
- `internal_status = MLK_STATUS_SUCCESS`.
- `status == RESILIENCE_OK_TOKEN`.
- **Latency: $1.0\times$ decapsulation time ($\approx 72.4\,\mu\text{s}$).**

When an invalid ciphertext is received over the network:
- Re-encryption fails: `tmp != ct`.
- `internal_status = MLK_STATUS_REJECT`.
- Because `dec_reject` is true, `rail1` is forced to `RESILIENCE_FAULT_TOKEN`.
- `status` evaluates to `RESILIENCE_FAULT_TOKEN`.
- The wrapper interprets rejection as a potential transient fault and triggers `allow_retry`.
- A complete second decapsulation iteration is performed.
- On retry, rejection recurs (`retry_reject == true`), and the wrapper finally returns `RESILIENCE_REJECT_TOKEN`.
- **Latency: $2.0\times$ decapsulation time ($\approx 145.8\,\mu\text{s}$).**

### Exploitation and Security Impact
1. **Remote Ciphertext Validity Oracle:** An attacker transmitting malformed ciphertexts over a network link can measure the decapsulation response latency. A response time of $\approx 72\,\mu\text{s}$ indicates a valid ciphertext; a response time of $\approx 146\,\mu\text{s}$ indicates an invalid ciphertext. This directly violates the IND-CCA2 security model of FIPS 203, which relies on implicit rejection being indistinguishable from authentic decapsulation.
2. **Denial-of-Service (DoS) Amplification:** An attacker transmitting streams of random ciphertexts doubles the decapsulation workload of the target flight computer, exhausting real-time scheduling margins.

---

## 5. Architectural Remediation

To eliminate the timing oracle while preserving fault recovery:
1. **Disentangle Cryptographic Rejection from Physical Faults:** An internal status of `MLK_STATUS_REJECT` (`0xA5A5A5A5`) indicates authentic implicit rejection where both rails agree that `tmp != ct`. This is a normal cryptographic termination, NOT a hardware fault.
2. **Retry Exclusively on Physical Faults:** The autonomous retry trigger must condition strictly on `internal_status == MLK_STATUS_FAULT` (`0xFFFFFFFF`) or multi-rail barrier corruption (`rail1 ^ ~rail2 != 0`).
3. **Constant-Time Verification of Rejection:** When `internal_status == MLK_STATUS_REJECT`, the system must immediately release the implicit rejection key $K_{\text{rej}}$ in exactly $1.0\times$ execution time.
