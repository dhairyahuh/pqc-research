# Phase 6B: Multi-Rail Control-Flow Robustness and Compiler Optimization Audit

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6B — Independent Adversarial Validation and Scientific Audit  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Candidate D Architecture and Claims

Candidate D proposed using 32-bit Hamming-separated status tokens (`RESILIENCE_OK_TOKEN = 0x5A5AA5A5`, `RESILIENCE_FAULT_TOKEN = 0xA5A55A5A`, $d_H = 32$) to eliminate single-bit return-code and decision-flag vulnerabilities.

The source implementation evaluated in Phase 6 was:
```c
static uint32_t verify_multi_rail_gate(uint32_t raw_status_code) {
    uint32_t rail1 = RESILIENCE_FAULT_TOKEN;
    uint32_t rail2 = RESILIENCE_FAULT_TOKEN;
    
    if (raw_status_code == 0) {
        rail1 = RESILIENCE_OK_TOKEN;
    }
    if ((raw_status_code ^ 0xFFFFFFFFu) == 0xFFFFFFFFu) {
        rail2 = ~RESILIENCE_FAULT_TOKEN; /* Equals 0x5A5AA5A5u */
    }
    
    if (rail1 == RESILIENCE_OK_TOKEN && rail2 == RESILIENCE_OK_TOKEN && (rail1 ^ rail2) == 0) {
        return RESILIENCE_OK_TOKEN;
    }
    return RESILIENCE_FAULT_TOKEN;
}
```

---

## 2. Compiler Optimization Collapse (Assembly Audit)

We disassembled the machine code produced by Apple clang 21.0.0 under the project's standard production optimization flag (`-O3` on AArch64):

```assembly
_verify_multi_rail_gate:
	cmp	w0, #0
	mov	w8, #42405                      ; w8 = 0xa5a5
	movk	w8, #23130, lsl #16            ; w8 = 0x5a5aa5a5 (RESILIENCE_OK_TOKEN)
	cinv	w0, w8, ne                     ; If w0 != 0, w0 = ~w8 (0xa5a55a5a)
	ret
```

### 2.1 Critical Vulnerability Discovery
1. **Total Elimination of Redundant Rail:**
   - The compiler's algebraic pass recognized that `(raw_status_code ^ 0xFFFFFFFFu) == 0xFFFFFFFFu` is mathematically identical to `raw_status_code == 0`.
   - The compiler eliminated `rail2`, eliminated the XOR check `(rail1 ^ rail2) == 0`, and eliminated both redundant comparisons.
2. **Collapse to a Single Hardware Flag:**
   - At runtime, the entire dual-rail mechanism is executed as **one comparison instruction (`cmp w0, #0`)** followed by a conditional inversion (`cinv`).
   - A single physical fault flipping the CPU's `PSTATE.Z` condition flag (Zero Flag) or an instruction skip glitch over `cmp` completely bypasses the gate, forcing `cinv` to return `0x5A5AA5A5` (SUCCESS) on an invalid status.
3. **Disparity Between Code and Binary:**
   - At the **source-code level**, there is an apparent multi-rail check with $d_H = 32$.
   - At the **binary machine-code level**, there is strictly a single scalar condition flag evaluation with zero redundancy.

---

## 3. Necessary Engineering Fix: Compiler Optimization Barriers

To preserve dual-rail redundancy in production binaries, compiler memory barriers or volatile qualifiers must be enforced:

```c
static uint32_t verify_multi_rail_gate_hardened(uint32_t raw_status_code) {
    volatile uint32_t rail1 = RESILIENCE_FAULT_TOKEN;
    volatile uint32_t rail2 = RESILIENCE_FAULT_TOKEN;
    
    if (raw_status_code == 0) {
        rail1 = RESILIENCE_OK_TOKEN;
    }
    /* Force independent evaluation via inline assembly barrier */
    uint32_t inverted = ~raw_status_code;
    __asm__ volatile("" : "+r"(inverted));
    
    if (inverted == 0xFFFFFFFFu) {
        rail2 = RESILIENCE_OK_TOKEN;
    }
    
    if (rail1 == RESILIENCE_OK_TOKEN && rail2 == RESILIENCE_OK_TOKEN && (rail1 ^ rail2) == 0) {
        return RESILIENCE_OK_TOKEN;
    }
    return RESILIENCE_FAULT_TOKEN;
}
```

Disassembly of this hardened version confirms that clang maintains both independent memory comparisons, independent branch checks, and the XOR cross-validation instruction.

---

## 4. Audit Conclusion on Candidate D

- **Theoretical Token Distance:** Confirmed ($d_H = 32$). Single-bit flips in the token itself cannot forge an OK code.
- **Unoptimized Implementation:** Fragile under optimizing compilers. The Phase 6 implementation was **eliminated by compiler optimization**, leaving the runtime binary vulnerable to single-flag glitches.
- **Recommendation:** Multi-rail software protection must explicitly incorporate compiler barriers (`volatile` / `asm volatile`) to prevent optimization collapse.
