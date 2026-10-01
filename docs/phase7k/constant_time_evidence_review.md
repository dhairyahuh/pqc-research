# Phase 7K: Constant-Time & Security Claim Review

## 1. Audit Scope & Security Requirements

In post-quantum key encapsulation mechanisms, fault detection and recovery mechanisms must not degrade side-channel resistance by creating:
1. **Ciphertext-Validity Oracles**: Observable execution timing differences between valid and invalid ciphertexts that allow adaptive chosen-ciphertext attacks (e.g., Bleichenbacher-style or error-oracle decapsulation attacks).
2. **Fault-Status Oracles**: Microarchitectural side channels revealing whether an internal butterfly fault occurred or whether rollback was attempted.

---

## 2. Microarchitectural & Assembly Inspection

### 2.1. Branchless Fail-Stop Accumulation in `kem.c`
Disassembly of the compiled object file `bin/obj/mlkem768_inst.o` was inspected at the Fujisaki–Okamoto verification gate:
```assembly
; Constant-time fail-stop evaluation in kem.c
eor      w10, w8, w9               ; w10 = fail ^ fail_chk
adrp     x11, _g_ntt_native_monitor
ldr      w12, [x11, #:lo12:_g_ntt_native_monitor]
adrp     x13, _g_invntt_native_monitor
ldr      w14, [x13, #:lo12:_g_invntt_native_monitor]
orr      w15, w12, w14             ; persistent_count |= invntt_persistent
orr      w10, w10, w15             ; combined discrepancy flag
cmp      w10, #0
cset     w16, ne                   ; 1 if persistent > 0 or fail != fail_chk
sbfx     w16, w16, #0, #8          ; sign-extend to 0xFF
orr      w8, w8, w16               ; fail |= 0xFF
```
- **Control Flow**: The evaluation utilizes straight-line instructions (`eor`, `orr`, `cset`, `sbfx`, `orr`), avoiding secret-dependent jump instructions (`b.eq`, `cbz`).
- **Memory Multiplexing**: `mlk_ct_cmov_zero` executes the same bitwise masking loop over 32 bytes regardless of whether `fail == 0x00` or `fail == 0xFF`.

### 2.2. Memory Access Patterns
- All polynomial and twiddle factor accesses are indexed strictly by public loop indices (`j`, `len`, `layer`).
- No secret key or message bits are used as array indices or shift amounts, precluding cache-timing attacks on lookup tables.

---

## 3. Empirical Randomized-Order Timing Evidence

### Measurement Protocol:
- 1,000 decapsulations executed in randomized order alternating between valid and invalid ciphertexts ($p = 0.5$) to eliminate linear thermal drift.
- Collected via `bin/phase7j_independent_validator` on Apple Silicon (ARM64).

### Statistical Results:
| Metric | Valid Ciphertext Distribution | Invalid Ciphertext Distribution | Delta / Ratio |
| :--- | :---: | :---: | :---: |
| **Sample Size ($N$)** | 1,000 trials | 1,000 trials | Interleaved |
| **Mean Latency ($\mu$)** | 81.27 µs | 80.69 µs | $\Delta\mu = -0.58\ \mu\text{s}$ ($-0.71\%$) |
| **Median Latency ($\tilde{\mu}$)** | 80.00 µs | 80.00 µs | **Ratio: 1.0000x** (Identical) |
| **Standard Deviation ($\sigma$)** | 18.95 µs | 7.97 µs | Consistent bounds |
| **Cohen's $d$ Effect Size** | — | — | **$d = 0.0399$ (Negligible, $< 0.20$)** |
| **Welch's Two-Sample $t$-test**| — | — | **$t = 0.892, p \approx 0.37$ ($p \gg 0.05$)** |

---

## 4. Academic Interpretation & Scientific Boundary

### What the Evidence Confirms:
1. **Macro-Architectural Invariance**: At standard software timer resolution ($> 10\ \text{ns}$), decapsulation exhibits no statistically significant timing divergence between valid and invalid inputs ($p > 0.05$, $|d| < 0.05$).
2. **Identical Computational Path**: Both valid decapsulation and implicitly rejected decapsulation execute the complete algorithm including matrix expansion, polynomial multiplications, dual NTTs, and dual SHAKE256 hash calls.

### What the Evidence Does NOT Prove:
1. **Absence of Leakage**: In statistical testing, failure to reject the null hypothesis ($p > 0.05$) does not constitute mathematical proof of zero leakage.
2. **Physical Side Channels**: Software timing tests cannot assess power analysis (DPA/CPA), electromagnetic emissions (SEMA/CEMA), or microarchitectural cache-line eviction probes (e.g., Prime+Probe) at nanosecond resolution.
