# Phase 7B Audit: Persistent Faults, Checker-State, and Control-Flow Gate Claims

**Auditor:** Independent Fault Modeling Critic & Auditor  
**Target:** Fault Injection Models in `experiments/phase7/phase7_layered_resilience.c`  
**Date:** October 2026  

---

## 1. Audit of Persistent Stuck-At Fault Modeling (Class 8)

### How Persistent Faults Were Implemented
In `experiments/phase7/phase7_layered_resilience.c`:
```c
/* Class 8: Persistent Faults (Stuck-At Hardware Fault) */
mlkem_fault_reset();
mlkem_fault_arm_mid_ntt_locus(4, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 50, 0);

/* DMR Test */
uint8_t ss1[SS_BYTES], ss2[SS_BYTES];
mlkem768_dec(ss1, ct, sk);
g_mlkem_fault.trigger_count = 0; /* Re-fires identically on Pass 2 */
mlkem768_dec(ss2, ct, sk);
if (memcmp(ss1, ss2, SS_BYTES) != 0) detected[3][7]++;
```

### Auditor Critique
1. **DMR Failure Mode:** Because `trigger_count = 0` re-arms the identical fault with the same parameters on Pass 2, both passes produce an identical corrupted secret key ($ss_1 == ss_2$). DMR's output comparison passes with 0% detection. This accurately models a permanent ALU or register latch-up.
2. **Layered Detection Mode:** In the layered configuration, the fault is detected because `verify_complementary_ntt` tests the polynomial against time-domain invariants that are independent of the faulted register.
3. **Limitation:** The persistent fault was modeled at an intermediate arithmetic stage (`OUTPUT_ADD`). If a persistent fault occurred in the memory bus holding the input ciphertext, or within the CPU comparator circuit itself, Layer 2 would not detect it.

---

## 2. Audit of Checker-State Perturbation (Class 6)

### How Checker Perturbation Was Implemented
```c
/* Class 6: Checker State Perturbation */
uint32_t glitched_rail1 = RESILIENCE_OK_TOKEN ^ (1u << (t % 32));
uint32_t glitched_rail2 = ~RESILIENCE_OK_TOKEN;
if (verify_multi_rail_barrier(glitched_rail1, glitched_rail2) == RESILIENCE_FAULT_TOKEN) {
    detected[4][5]++;
}
```

### Auditor Critique
1. **Model Scope:** This test simulates an SEU bit-flip inside the `rail1` status token variable *before* it enters `verify_multi_rail_barrier`.
2. **Result:** Because `rail1` no longer equals `0x5A5AA5A5`, `pass1` is evaluated as 0, and the barrier returns `RESILIENCE_FAULT_TOKEN`.
3. **Auditor Finding:** This confirms that the multi-rail gate has a **Hamming distance of 32**; a single bit-flip in either rail prevents false positive acceptance.
4. **Scope Limit:** The test does **not** corrupt the comparator instructions themselves, nor does it perturb the expected reference tokens during execution.

---

## 3. Audit of Control-Flow Gate Flips (Class 7)

### How Control-Flow Flips Were Implemented
```c
/* Class 7: Control Flow FO Gate */
mlkem_fault_reset();
mlkem_fault_arm_fo_flag(0); /* Forces fail flag 0 -> 1 inside kem.c */
```
In `algorithms/source_ref/mlkem_fault_hooks.c`:
```c
void hook_decaps_verify_flag(int *fail_flag) {
    if (g_mlkem_fault.fo_direction == 0) {
        *fail_flag = 1; // Force failure on valid CT
    }
}
```

### Auditor Critique
1. **Boolean Override vs Control Flow:**
   This hook injects a fault into an **in-memory integer flag** (`*fail_flag = 1`). It is a **data-flow perturbation of a predicate variable**, NOT a physical control-flow hijack (such as an instruction skip or branch target modification).
2. **Cryptographic Impact:**
   Forcing `fail_flag = 1` causes FIPS 203 implicit rejection to trigger on an authentic ciphertext, outputting pseudorandom key $K'$ instead of valid key $K$.
3. **Auditor Finding:**
   Describing this experiment as a "Control-Flow Integrity" test is technically imprecise. It is accurately classified as an **FO Predicate Data-Flow Fault**. The multi-rail gate successfully detects that a discrepancy occurred, but this does not evaluate physical CFI against ROP or instruction corruption.
