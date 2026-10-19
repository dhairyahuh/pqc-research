# Full-Text Extraction Template

Use this template for each PDF supplied for review. Copy this file and rename it for each paper (e.g., `sarker_2023_tcad.md`).

---

## 1. Bibliographic Details
- **Exact Title:**
- **Authors:**
- **Year:**
- **Venue (Journal/Conference):**
- **Volume/Issue/Pages:**
- **DOI:**
- **IEEE Xplore URL:**
- **Access date:**

## 2. Research Problem and Stated Contributions
- **Problem addressed:**
- **Stated contributions (numbered):**
  1.
  2.
  3.

## 3. Cryptographic Algorithm, Implementation, Platform, Fault Model
- **Algorithm(s):**
- **Implementation type:** (FPGA / ASIC / software / co-design)
- **Platform/device:**
- **Fault model:**
  - Fault type (transient/permanent/adversarial):
  - Fault location (register/ALU/memory/twiddle):
  - Injection method (simulation/laser/voltage glitch/SWIFI):
  - Single vs multi-fault:

## 4. Experimental Design
- **Baselines/controls:**
- **Sample sizes/trial counts:**
- **Statistical methods used:**
- **Reproducibility information:**

## 5. Fault Locations, Injection, Persistence, Activation
- **Specific fault targets:**
- **Injection timing (mid-NTT / pre-NTT / post-NTT / other):**
- **Persistence model:**
- **Activation conditions:**

## 6. Detection, Recovery, Safe Failure, SDC Definitions
- **Detection mechanism(s):**
- **Recovery mechanism(s):**
- **Safe failure definition:**
- **SDC definition:**
- **Detection coverage reported:**
- **Recovery success rate:**

## 7. Results and Quantitative Findings
| Metric | Value | Denominator | Uncertainty | Page/Table/Figure |
|:---|:---|:---|:---|:---|
| | | | | |

## 8. Performance Overhead
- **Area overhead (if hardware):**
- **Latency overhead:**
- **Power overhead:**
- **Comparison baseline:**

## 9. Limitations Acknowledged by Authors
1.
2.

## 10. Limitations Visible from Described Method
1.
2.

## 11. Relevance to Each Candidate Paper Track
### Track 1 (Internal Fault Detection)
- **Similarity:**
- **Difference:**
- **Claims strengthened:**
- **Claims weakened:**

### Track 2 (Cross-Layer) — if applicable
- **Relevance:**

### Track 3 (Persistent State) — if applicable
- **Relevance:**

## 12. Comparison Against Our Implementation
| Dimension | This Paper | Our Work |
|:---|:---|:---|
| Implementation domain | | Software C99 |
| NTT transforms covered | | Forward CT + Inverse GS (all 11) |
| Detection mechanism | | Algebraic invariant + snapshot |
| Recovery mechanism | | Single-butterfly rollback |
| Fail-stop mechanism | | FO implicit rejection |
| Performance overhead | | +16.9% (reported) |
| Fault model | | Non-adversarial SEU |

## 13. What Experiment Would Establish a Meaningful Distinction
-

## 14. Unanswered Questions
-

## 15. Citation Traceability
All extracted claims must include:
- Page number:
- Section/paragraph:
- Table/Figure reference:

> **RULE:** Do not infer numerical results absent from the full text. Mark uncertain extractions with `[UNCERTAIN]`.
> Distinguish: (a) direct findings, (b) our interpretation, (c) comparison against our work, (d) unanswered questions.
