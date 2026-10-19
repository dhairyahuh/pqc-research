# F2 Empirical Trace and Causal Audit Report

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Evidence Source:** [`phase9_reproducibility_audit/f2_trace_evidence.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_trace_evidence.csv) (100 trials)  
**Binary Executed:** [`phase9_reproducibility_audit/f2_tracer`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_tracer)  

---

## 1. Executive Summary

This audit establishes the empirical validity of the stage-dependent outcome split observed in Target F2 (+100 additive bias on `u_saved`). Across 100 trials, the recovery verifier was **blinded in 100% of trials** ($diff_{\text{retry}} == 0 \land sum_{\text{retry}} == 0$), yet the final decapsulation outcome split into:
- **30% Genuine Recovery (`RECOVERED_GENUINE`)**
- **70% Downstream Rejection (`REJECTED_DOWNSTREAM`)**

Every trial record in `f2_trace_evidence.csv` was verified, linking the injected fault, arithmetic result, polynomial diffusion footprint, ciphertext comparison, and final shared secret.

---

## 2. Empirical Stage Breakdown

*Data derived from 100 consecutive trials linking `bin/obj/mlkem768_inst.o`.*

| NTT Stage | Trial Count | Verifier Passed (`diff == 0 && sum == 0`) | Corrupted NTT Coefficients | Candidate Ciphertext Match (`memcmp == 0`) | FO Decision Flag (`fail`) | Decapsulation Status | Shared Secret Match | Cryptographic Outcome |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 1** | 15 / 100 | 15 / 15 (100%) | **128 / 256** | 15 / 15 (100%) | `0x00` (15/15) | `0x5A5A5A5A` (15/15) | 15 / 15 (100%) | **Genuine Recovery (15/15)** |
| **Stage 2** | 15 / 100 | 15 / 15 (100%) | **64 / 256** | 15 / 15 (100%) | `0x00` (15/15) | `0x5A5A5A5A` (15/15) | 15 / 15 (100%) | **Genuine Recovery (15/15)** |
| **Stage 3** | 14 / 100 | 14 / 14 (100%) | **32 / 256** | 0 / 14 (0%) | `0xFF` (14/14) | `0xA5A5A5A5` (14/14) | 0 / 14 (0%) | **Downstream Rejection (14/14)** |
| **Stage 4** | 14 / 100 | 14 / 14 (100%) | **16 / 256** | 0 / 14 (0%) | `0xFF` (14/14) | `0xA5A5A5A5` (14/14) | 0 / 14 (0%) | **Downstream Rejection (14/14)** |
| **Stage 5** | 14 / 100 | 14 / 14 (100%) | **8 / 256** | 0 / 14 (0%) | `0xFF` (14/14) | `0xA5A5A5A5` (14/14) | 0 / 14 (0%) | **Downstream Rejection (14/14)** |
| **Stage 6** | 14 / 100 | 14 / 14 (100%) | **4 / 256** | 0 / 14 (0%) | `0xFF` (14/14) | `0xA5A5A5A5` (14/14) | 0 / 14 (0%) | **Downstream Rejection (14/14)** |
| **Stage 7** | 14 / 100 | 14 / 14 (100%) | **2 / 256** | 0 / 14 (0%) | `0xFF` (14/14) | `0xA5A5A5A5` (14/14) | 0 / 14 (0%) | **Downstream Rejection (14/14)** |

---

## 3. Mathematical Origin of the 30% / 70% Split

In the experiment runner, trial $t \in [0, 99]$ assigns the target stage as:
$$\text{stage} = (t \bmod 7) + 1$$
Across 100 integer trials:
- $t \equiv 0 \pmod 7 \implies \text{Stage 1}$: occurs for $t \in \{0, 7, 14, \dots, 98\}$ (**15 trials**).
- $t \equiv 1 \pmod 7 \implies \text{Stage 2}$: occurs for $t \in \{1, 8, 15, \dots, 99\}$ (**15 trials**).
- $t \equiv 2 \pmod 7 \implies \text{Stage 3}$: occurs for $t \in \{2, 9, 16, \dots, 93\}$ (**14 trials**).
- $t \equiv 3 \pmod 7 \implies \text{Stage 4}$: occurs for $t \in \{3, 10, 17, \dots, 94\}$ (**14 trials**).
- $t \equiv 4 \pmod 7 \implies \text{Stage 5}$: occurs for $t \in \{4, 11, 18, \dots, 95\}$ (**14 trials**).
- $t \equiv 5 \pmod 7 \implies \text{Stage 6}$: occurs for $t \in \{5, 12, 19, \dots, 96\}$ (**14 trials**).
- $t \equiv 6 \pmod 7 \implies \text{Stage 7}$: occurs for $t \in \{6, 13, 20, \dots, 97\}$ (**14 trials**).

Because Stages 1 and 2 account for exactly $15 + 15 = 30$ trials, and Stages 3–7 account for $14 \times 5 = 70$ trials, the measured split is **exactly 30.0% genuine recovery and 70.0% downstream rejection**.

---

## 4. Separation of Direct Observation from Causal Theory

### Direct Empirical Facts (Independently Re-measured):
1. In 100/100 trials, the verifier evaluates $diff_{\text{retry}} = 0 \land sum_{\text{retry}} = 0$. (Measured fact).
2. The number of affected polynomial coefficients in the NTT domain is strictly $2^{8 - \text{stage}}$ (128 for Stage 1, 64 for Stage 2, down to 2 for Stage 7). (Measured fact).
3. In Stages 1 and 2, `memcmp(ct, tmp) == 0` evaluates to true in 30/30 trials. (Measured fact).
4. In Stages 3–7, `memcmp(ct, tmp) != 0` evaluates to false in 70/70 trials. (Measured fact).
5. In Stages 1 and 2, the returned shared secret matches the genuine key in 30/30 trials. (Measured fact).
6. In Stages 3–7, the returned shared secret is the implicit rejection key in 70/70 trials. (Measured fact).

### Causal Explanation (Theory Supported by Measurement):
- The discrete transition between Stage 2 and Stage 3 is caused by coefficient error diffusion falling below the rounding threshold of 10-bit polynomial compression ($\Delta_{\text{bin}} = \frac{3329}{1024} \approx 3.251$).
- When the $+100$ bias is divided among $\ge 64$ coordinates in the frequency domain, its inverse-NTT contribution per coefficient is smaller than the compression rounding bin, leaving the serialized ciphertext bytes unmodified.
- When concentrated among $\le 32$ coordinates, the perturbation exceeds the rounding bin in multiple coefficients, altering the ciphertext bytes and triggering the outer FO check.
