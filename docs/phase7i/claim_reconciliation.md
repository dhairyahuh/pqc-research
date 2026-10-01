# Phase 7I: Research Claim Reconciliation & Master Evidence Matrix

## 1. Evolution of Claims Across Project Phases

The fault resilience investigation of NIST FIPS 203 ML-KEM-768 decapsulation has evolved through rigorous experimental and mathematical scrutiny:

| Phase | Milestone Focus | Claimed Recovery | Transform Coverage | Measured Decaps Overhead | Methodological Verification Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Phase 7E** | Theoretical Prototype | 100% (1,050 trials) | Forward NTT | +20.26% | **Disproved in 7F**: Prototype bypassed, null callbacks used, overhead did not include active monitor. |
| **Phase 7F** | Independent Audit | Disproved | None | N/A | **Confirmed Defect**: No native hooks in compiled library; simulated status flags used. |
| **Phase 7G** | Native Integration | 100% (transient) | Forward NTT (5,376 bflies) | +11.8% | **Genuinely Integrated**: First true native in-place rollback. Left inverse NTT unmonitored. |
| **Phase 7H** | Independent Verification | 100% (fwd transient)| Forward NTT (5,376 bflies) | +11.8% | **Audit Confirmed**: Verified native rollback; identified unmonitored InvNTT and public API fail-stop defect. |
| **Phase 7I** | **Inverse NTT & End-to-End**| **100% (transient)** | **Full (9,856 bflies: Fwd + Inv)**| **+16.79%** | **Rigorous Final Reconciliation**: Derived GS invariant, patched public API fail-stop, 1,400 trials, CT verified. |

---

## 2. Master Claim Reconciliation Matrix

| Domain / Dimension | Prior Understanding (Phase 7H) | Phase 7I Verified Reality | Evidence & Reference |
| :--- | :--- | :--- | :--- |
| **Transform Coverage** | Forward Cooley-Tukey NTT only (5,376 butterflies). Inverse NTT completely unmonitored. | **Complete decapsulation coverage**: 5,376 forward + 4,480 inverse = **9,856 butterflies monitored**. | `results/phase7i/processed/phase7i_e2e_results.json` |
| **GS Inverse Invariant** | Assumed forward difference invariants could be applied to inverse NTT. | **Mathematically Disproved**: Proved linear combination cannot eliminate $\zeta$ without multiplication. Derived dual $S$ & $D$ invariant. | `docs/phase7i/mathematical_derivation.md` |
| **Public API Fail-Stop** | Defect identified: `internal_status == NULL` bypassed fail-stop under persistent faults. | **Hardened**: Unconditional `fail = 0xFF` enforced in `kem.c` regardless of pointer state. | `algorithms/source_ref/mlkem/src/kem.c`, `docs/phase7i/public_api_validation.md` |
| **Transient Recovery** | 100% on forward intermediate $t$ and output registers. | **100% across all 7 transient arithmetic classes** (forward + inverse + symmetric/anti-symmetric). | 700 / 700 trials recovered, `docs/phase7i/experimental_results.md` |
| **Recovery vs Rejection** | Risk of conflating implicit rejection with native recovery. | **Strictly Separated**: Recovery = in-place retry emitting $K_{\text{valid}}$ (700 trials). Safe Reject = fail-stop emitting $K_{\text{rej}}$ (583 trials). | `docs/phase7i/fault_injection_methodology.md` |
| **Twiddle Factor Blind Spot** | Forward twiddle bypass confirmed. | **Inverse twiddle bypass also confirmed**: Local butterfly cannot detect $\zeta$ corruption; FO transform catches 88%–95%. | Classes C02 & C05, 0% undetected corruption. |
| **Runtime Overhead** | Forward-only: +11.8% vs Baseline. DMR: +134.9%. | **Combined (Fwd + Inv): +16.79%** (79.18 µs vs 67.79 µs). **8.1x lower overhead than DMR (+135.69%)**. | `docs/phase7i/benchmark_results.md` |
| **Side-Channel Timing** | Sequential block timing showed similar means. | **Randomized-order interleave (1,000 trials)**: Ratio $1.0000\times$, Cohen's $d = 0.019$, assembly verified branchless. | `docs/phase7i/timing_analysis.md` |

---

## 3. Explicit Research Limitations & Negative Results

To maintain university research integrity, the following negative results and boundaries are explicitly affirmed:

1. **Twiddle Factors Require Systemic Protection**:
   - The native butterfly monitor operates purely on operand relationships. A corrupted twiddle factor $\zeta$ scales the butterfly correctly according to the corrupted constant, evading the local arithmetic check. Although Fujisaki-Okamoto re-encryption catches this downstream as a ciphertext discrepancy, butterfly-level twiddle resilience requires separate table checksumming (e.g. CRC or parity trees).
2. **Recovery Bound**:
   - In-place recovery is limited to transient faults ($N_{\text{retry}} = 1$). Persistent hardware faults (e.g. permanent stuck-at line) cannot be recovered by local retry; they are safely quenched to zero and rejected.
3. **Software Fault Injection vs Physical Particle Radiation**:
   - Software fault injection models bit flips and stuck-at registers in arithmetic logic. High-energy heavy ion radiation in space environments may induce multi-node upsets (MNU) across multiple bus lines simultaneously or clock glitching across pipelined execution stages.
