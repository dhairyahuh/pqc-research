# Phase 15F — Provenance Errata and Hash Reconciliation

**Author:** Skeptical Cryptographic Research Engineer  
**Date:** 2026-10-11  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Context:** Resolution of Phase 15E Finding F-15E-10 and Historical Provenance Reconciliation  
**Directory:** `research/phase14_persistent_arm_design/`

---

## 1. Executive Summary & Purpose

This errata document resolves Finding **F-15E-10** from the Phase 15E Independent Audit. It establishes the authoritative, independently computed SHA-256 digests for all research artifacts across Phases 15A through 15F.

In accordance with strict audit boundaries:
- Historical documents (`PHASE15D_REPORT.md`, `PHASE15B_REPORT.md`, `PHASE15B_TRIAL_LEDGER.csv`) are **preserved byte-for-byte** and are **not** rewritten in place.
- Historical claims are not altered retroactively; instead, errors in recorded hash values are formally identified, explained, and reconciled herein.
- No physical fault injection or live mutation trials were executed during Phase 15F.

---

## 2. Artifact Hash Reconciliation Ledger

The following table compares the SHA-256 digests recorded in `PHASE15D_REPORT.md` (Section 5) against the actual digests independently recomputed on disk during Phase 15F:

| Artifact Path | Digest Recorded in Phase 15D Report | Actual Digest Observed (Phase 15F) | Match Status | Provenance & Correction Analysis |
|:---|:---|:---|:---:|:---|
| `research/phase14_persistent_arm_design/pilot_runner.c` | `064e7b1f4f3ca19dc6d901a3a2885f9b306c71a3810d0f8ee70b152ee49d62cb` | `ea253b5bbde2406f3d93061e2e1652e78ba8b3f68c66cf7a774d29f59b18d95d` | **SUPERSEDED** | Phase 15D digest was verified for that version (`064e...`). File was subsequently updated in Phase 15F to resolve sentinel validation and CSV schema. Current authoritative hash is `ea25...`. |
| `research/phase14_persistent_arm_design/pilot_runner.c.phase15b_bak` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | **MATCH (PASS)** | Preserved byte-for-byte backup of the unhardened Phase 15B runner. |
| `bin/pilot_runner` | `db8c5f5823d0c7ce886ea8a88bb30afa2c891783f4d5f2ecaee3cc611a9d8298` | `8de41e4a7631535d60b1d8b193f518098870b4cf230481aaf0d5fda5f0c03afd` | **SUPERSEDED** | Recompiled in Phase 15F following sentinel and schema fixes. Current authoritative binary hash is `8de4...`. |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | **MATCH (PASS)** | Unaltered Phase 15A research build relocatable object. |
| `bin/test_fips_kats_research` | `01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf` | `01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf` | **MATCH (PASS)** | Unaltered research build KAT verification executable. |
| `research/phase14_persistent_arm_design/PHASE15A_REPORT.md` | `c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981` | `c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981` | **MATCH (PASS)** | Unaltered historical Phase 15A report. |
| `research/phase14_persistent_arm_design/PHASE15B_REPORT.md` | `c6bba92f0254c50c53d06ebef4fc9b17743d57b3bf97bf875185d34ffab3573c` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | **MISMATCH (CORRECTED)** | **Documentation defect in Phase 15D Report.** The actual file on disk has hash `0a53...`. The reported digest (`c6bb...`) was transcribed in error. The actual historical file bytes have remained unchanged. |
| `research/phase14_persistent_arm_design/PHASE15B_TRIAL_LEDGER.csv` | `7973715d2a33ebfe11bb3bbca6ee3a7cfbeafc04516ff8be7d9ae17351ff5606` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | **MISMATCH (CORRECTED)** | **Documentation defect in Phase 15D Report.** The actual file on disk has hash `5cf4...`. The reported digest (`7973...`) was transcribed in error. The actual historical file bytes have remained unchanged. |

---

## 3. Supplementary Documentation Hashes

For complete auditable provenance, the SHA-256 digests of all subsequent audit and changelog artifacts are recorded below:

```text
271f026dc8e8a1ea1802b239c2c162a1d54fa3fa3995b44794a3f7689384cd58  research/phase14_persistent_arm_design/PHASE15C_AUDIT.md
015f8257ca21ea1a103febe93e0d3332a784e0137e1530a0c5e586cf332ff802  research/phase14_persistent_arm_design/PHASE15C_EVIDENCE_MATRIX.md
d7aa35ee06f3e60124671603113f269bd1cf990c5070d9284746bf07bff6cd02  research/phase14_persistent_arm_design/PHASE15D_REPORT.md
accb7e1a4d852b6210e5efcc347b03958d07f631262db9b70ce8d1fe6cce759b  research/phase14_persistent_arm_design/PHASE15D_CHANGELOG.md
18d63baeeca5d6e1c00c08eccb98c06f48d1e5047f7a8868d8aee235d86adc8f  research/phase14_persistent_arm_design/PHASE15E_AUDIT.md
ba26f2257ff0dde4eee14b428a8e6b35ed94af48e9d0eb7e0b49151aeae6bdfe  research/phase14_persistent_arm_design/PHASE15E_FINDINGS_MATRIX.md
```

---

## 4. Limitations and Boundaries

1. **Root Cause of Mismatch:** The mismatched digests in `PHASE15D_REPORT.md` arose from manual transcription or uncommitted scratch hashing during report drafting. The underlying files (`PHASE15B_REPORT.md` and `PHASE15B_TRIAL_LEDGER.csv`) have **not** been modified since Phase 15B.
2. **Preservation Guarantee:** In accordance with audit instructions, `PHASE15D_REPORT.md` is **not** edited retroactively. This standalone errata document serves as the official reconciliation.
3. **Epistemological Boundary:** Verifying that a file matches its recomputed hash proves data integrity at rest. It does not certify the empirical validity of claims contained inside historical reports.
