# Phase 7B Claim Inventory and Evidence Mapping

**Auditor:** Independent Cryptographic Implementation Auditor  
**Target:** Phase 7 Layered Fault-Resilience Engineering for ML-KEM-768  
**Audit Date:** October 2026  

---

## 1. Claim Inventory Table

| Claim ID | Claim Description | Phase 7 Source Location | Required Evidence | Validation Method | Preliminary Result | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | Layered architecture achieves $\ge 96.7\%$ detection across all 8 threat classes. | `phase7_final_report.md` §1 | Reproducible injection across 8 classes in independent harness | Systematic rerun with full per-trial records | **PARTIALLY SUPPORTED** (Relies on test harness passing `expected_ss` oracle and external poly) | High |
| **CLM-02** | Average detection across all 8 threat classes is 99.6%. | `phase7_final_report.md` §1 | Arithmetic mean of per-class detection rates | Recompute from verified trial data | **REPRODUCED** (Under the specific harness setup: $(7\times 100\% + 96.7\%)/8 = 99.58\%$) | High |
| **CLM-03** | Layered architecture overhead is $+21.3\%$ to $+22.6\%$. | `phase7_final_report.md` §2, §5 | Measured decapsulation latency vs baseline over 2,000 iterations | Multi-run independent benchmark with warm-up & standard deviation | **REPRODUCED** | High |
| **CLM-04** | Unweighted parity invariant has an algebraic blind spot (0.0% detection) for intermediate butterfly faults ($t, \zeta$). | `ntt_complementary_check_analysis.md` §1 | Mathematical proof of even stride parity cancellation & empirical zero detection | Formal mathematical derivation + all-layer fault sweep | **MATHEMATICALLY ESTABLISHED & REPRODUCED** | Very High |
| **CLM-05** | Weighted inverse-zeta invariant detects 100% of tested Layer 7 intermediate faults. | `ntt_complementary_check_analysis.md` §2 | Mathematical derivation of $w_i = \zeta_i^{-1}$ + 128-butterfly injection sweep | Independent sympy/Python derivation + C injection | **MATHEMATICALLY ESTABLISHED & REPRODUCED** | Very High |
| **CLM-06** | Complementary NTT checks detect 14.0% of general intermediate butterfly faults across all layers. | `fault_coverage_results.md` §1 | Layer sweep across 7 layers ($1/7 \approx 14.3\%$) | Test each layer $L \in \{1..7\}$ independently | **REPRODUCED WITH SCOPE LIMITS** (Only Layer 7 is detected; Layers 1-6 are 0% without checkpoints) | High |
| **CLM-07** | CRC32 detects 100% of tested pre-invocation input corruptions. | `input_integrity_and_duplication.md` §3 | Random bit-flips in 1088-byte ciphertext buffer | Fault injection into $ct$ buffer against reference CRC | **REPRODUCED WITH SCOPE LIMITS** (Valid only under trusted reference model, not adversarial forgery) | Very High |
| **CLM-08** | Multi-rail gate remains independent in compiled machine code at `-O3`. | `compiled_control_flow_analysis.md` §2 | Disassembly showing independent registers and absence of single condition flag folding | AArch64 disassembly inspection of `clang -O3` output | **REPRODUCED** | High |
| **CLM-09** | Layered design detects all tested checker-state perturbations. | `fault_coverage_results.md` §1 | Single-bit flips in status tokens | Injection into `rail1` / `rail2` registers | **SUPPORTED WITH SCOPE LIMITS** (Harness tests token flip; doesn't test general ALU glitching) | Moderate |
| **CLM-10** | Layered design detects all tested control-flow gate flips. | `fault_coverage_results.md` §1 | Inversion of FO verification flag ($0 \to 1$) | Hook injection into `hook_decaps_verify_flag` | **SUPPORTED WITH SCOPE LIMITS** (Models Boolean flag override, not arbitrary branching) | Moderate |
| **CLM-11** | Layered design detects all tested persistent stuck-at faults. | `fault_coverage_results.md` §1 | Identical fault repeated across consecutive passes | Dual-pass fault injection | **REPRODUCED WITH SCOPE LIMITS** (Evaluated on specific ALU/register stuck faults) | Moderate |
| **CLM-12** | Retry mechanism safely recovers from the specified transient fault model. | `selected_protection_design.md` §2 | Transient fault disarmed on retry pass producing clean shared secret | Invalidate pass 1, disarm pass 2, verify key equality | **REPRODUCED** | High |
| **CLM-13** | Full duplicate decapsulation (DMR) fails (0.0% detection) against pre-invocation corruption and persistent stuck faults. | `input_integrity_and_duplication.md` §1 | Double-pass decapsulation under identical corrupted buffer | Run DMR on corrupted $ct$ and persistent ALU fault | **REPRODUCED** | Very High |
| **CLM-14** | Performance and memory overhead measurements are reproducible. | `performance_and_cost_results.md` §1, §2 | Measurement of binary size, stack, and LUT size | Static binary inspection + stack instrumentation | **REPRODUCED** | High |
| **CLM-15** | Protection mechanisms are fully integrated into the actual decapsulation call path. | `phase7_final_report.md` §1 | Inspection of `mlkem768_dec` source code | Inspect call graph in `poly.c`, `kem.c`, and harness | **IMPLEMENTATION MISMATCH** (Checks were wrapped around `mlkem768_dec` in harness, not built into `mlkem-native` library) | High |
| **CLM-16** | The stated research contribution and novelty claims are justified. | `novelty_and_contribution_review.md` §1 | Comparison against literature (ABFT, lattice fault detection) | Literature matrix analysis | **PARTIALLY SUPPORTED** (Theoretical results are novel; engineering elements are known ABFT adaptations) | High |

---

## 2. Summary of Critical Audit Observations

1. **The Implementation Mismatch in Integration (CLM-15):**  
   The Phase 7 report claims "Integrated 4-layer architecture." However, source code inspection of `experiments/phase7/phase7_layered_resilience.c` reveals that `mlkem768_dec` in `algorithms/source_ref/mlkem/` was **not modified to embed the NTT checks or the multi-rail gate internally**. Instead, `decaps_layered` is a wrapper function in the test harness that calls `crc32_ieee`, calls `mlkem768_dec`, evaluates `verify_complementary_ntt` on an external test polynomial, and compares `ss` against `expected_ss` passed as an argument!
2. **The `expected_ss` Oracle Dependency (CLM-01):**  
   In `decaps_layered`, `dec_fault` is determined by `memcmp(ss, expected_ss, SS_BYTES) != 0`. In actual cryptographic decapsulation, the decapsulating party does not possess `expected_ss`. To achieve true internal fault detection without an oracle, the FO re-encryption verification flag inside `kem.c` must be exposed.
3. **Unexecuted Butterfly Difference Check:**  
   `verify_complementary_ntt` contains code for the butterfly difference check, but in all experimental trials and benchmarks, `mid_stage_in` was passed as `NULL`, meaning this check was never active during data collection.
4. **Empty Raw Data (CLM-02):**  
   `results/phase7/raw/phase7_raw_trials.json` contains only a 5-line summary object without individual trial logs.
