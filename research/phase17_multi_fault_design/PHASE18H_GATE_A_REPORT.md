# Phase 18H Report: Gate A Implementation — Vector Preflight and Rejection-Oracle Validation

**Document:** `research/phase17_multi_fault_design/PHASE18H_GATE_A_REPORT.md`  
**Date:** 2026-10-12  
**Governing Specification:** [PHASE18G_IMPLEMENTATION_GATE_PLAN.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18G_IMPLEMENTATION_GATE_PLAN.md) (§3.1 Gate A)  
**Historical Design References:**
- [PHASE18F_FINAL_SPECIFICATION_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18F_FINAL_SPECIFICATION_AUDIT.md)
- [PHASE17D_FINAL_PREREGISTRATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17D_FINAL_PREREGISTRATION.md) (§4.1–§4.3)
- [PHASE17H_OPERATOR_RATIFICATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md)  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** GATE A EXECUTED — VERDICT: PASS  

---

## Executive Summary & Final Verdict

# **GATE A VERDICT: PASS**

### Executive Statement:
Phase 18H implemented, executed, and completed **Gate A (Vector Preflight and Rejection-Oracle Validation)** in strict accordance with the mandatory anti-hallucination protocol and Gate A specification.

1. **Software-Only Execution:** Exactly **0** calls to `vm_protect` were made; zero virtual memory page protections were altered; zero twiddle tables were mutated; and the multi-fault campaign was not run.
2. **Corpus Scope:** Exactly **420 candidate vectors** were evaluated:
   - **Vector 0 (1 vector):** Official NIST FIPS 203 KAT reference vector (`references/test_vectors/mlkem_expected_kat.h`).
   - **Vectors 1..419 (419 vectors):** Locally generated deterministic test vectors derived via reproducible FIPS 202 SHAKE-256 PRF expansion.
3. **Validation Outcome:** Exactly **420 out of 420 candidate vectors (100.00%)** successfully passed all 8 preflight checks with **zero failures, zero mismatches, and zero discarded candidates**.
4. **Cross-Implementation Agreement:** Every vector achieved byte-for-byte identity between the System Under Test (`mlkem-native` fc269bc2d106) and the independent reference oracle (Open Quantum Safe `liboqs` v0.16.0) across public keys (1,184 bytes), secret keys (2,400 bytes), ciphertexts (1,088 bytes), and shared secrets (32 bytes).
5. **Rejection Oracle Compliance:** On every vector, SUT decapsulation on tampered ciphertext ($\tilde{c} = c \oplus 0x01$) produced the exact canonical FIPS 203 implicit rejection shared secret ($K_{\text{rej}} = \text{SHAKE256}(z \parallel \tilde{c}, 32)$) derived independently by TweetFIPS-202.

---

## 1. Baseline Cryptographic Specification and Oracle Provenance

### 1.1 Parameter Set and Buffer Length Verification `[DIRECTLY OBSERVED]`
Inspected directly in `algorithms/source_ref/mlkem/src/params.h`, `kem.h`, and `references/test_vectors/mlkem_expected_kat.h`:
- **Algorithm:** ML-KEM-768 (NIST FIPS 203 Module-Lattice-Based Key-Encapsulation Mechanism).
- **Public Key Length ($pk$):** Exactly **1,184 bytes** (`MLKEM768_PUBLICKEYBYTES`).
- **Secret Key Length ($sk$):** Exactly **2,400 bytes** (`MLKEM768_SECRETKEYBYTES`).
- **Ciphertext Length ($ct$):** Exactly **1,088 bytes** (`MLKEM768_CIPHERTEXTBYTES`).
- **Shared Secret Length ($ss$):** Exactly **32 bytes** (`MLKEM768_SSBYTES`).
- **Keypair Derandomization Seed ($d \parallel z$):** Exactly **64 bytes** ($32 + 32$ bytes).
- **Encapsulation Derandomization Seed ($m$):** Exactly **32 bytes**.

### 1.2 Structure of Secret Key and Rejection Secret $z$ `[DIRECTLY OBSERVED]`
Per FIPS 203 Algorithm 16 (`ML-KEM.KeyGen_internal`):
$$sk = \text{indcpa\_sk} \parallel pk \parallel H(pk) \parallel z$$
- $\text{indcpa\_sk}$ length: $12 \times 3 \times 256 / 8 = 1,152$ bytes (bytes $0..1151$).
- $pk$ length: 1,184 bytes (bytes $1152..2335$).
- $H(pk)$ length: 32 bytes (bytes $2336..2367$).
- **Rejection seed $z$:** Exactly **32 bytes**, located at bytes **$2368..2399$** (`sk + 2368`).
- **Source Code Verification:** In `algorithms/source_ref/mlkem/src/kem.c:513`, $z$ is explicitly read from offset:
  `sk + MLKEM_INDCCA_SECRETKEYBYTES - MLKEM_SYMBYTES` = `sk + 2400 - 32` = `sk + 2368`.

### 1.3 Independent Oracle Mechanism and Provenance Boundary `[DIRECTLY OBSERVED]`
- **Software Components:**
  1. Open Quantum Safe `liboqs` v0.16.0 (installed at `/opt/homebrew/lib/liboqs.dylib` / `/opt/homebrew/include/oqs/kem.h`).
  2. Standalone TweetFIPS-202 reference implementation (`tfib_experiments/phase11_oracle/fips202_ref.c`).
- **Rejection Key Derivation:**
  In `tfib_experiments/phase11_oracle/independent_oracle.c:59-79`, `independent_oracle_compute_rejection(ss_rej, sk, ct)`:
  1. Extracts 32-byte $z$ directly from $sk[2368..2399]$.
  2. Constructs input buffer $z \parallel ct$ (1,120 bytes).
  3. Passes $z \parallel ct$ to standalone `fips202_ref_shake256(ss_rej, 32, z_c, 1120)`.
  This strictly executes FIPS 203 Section 3.3 and Algorithm 17:
  $$K_{\text{rej}} = J(z \parallel c, 32) = \text{SHAKE256}(z \parallel c, 32)$$
- **Provenance Statement (Honest Scope Demarcation):**
  The oracle is **demonstrably independent in code** from `mlkem-native`:
  - It links against a separate external open-source library (`liboqs`) developed by the Open Quantum Safe project.
  - It computes the rejection hash via a standalone C file (`fips202_ref.c`) derived from TweetFIPS-202, sharing no build artifacts or compilation units with the SUT.
  - **Clean-Room Qualification:** This independence is an empirical, structural separation in software code and dynamic libraries. It is **not** a legally audited or formal clean-room engineering separation, and shall not be described as such.

---

## 2. Deterministic Corpus Specification Before Generation

### 2.1 Provenance Hierarchy
The 420-vector corpus is explicitly divided into two distinct provenance classes:
1. **Vector 0 (Official NIST Reference KAT):**
   - **Provenance:** `OFFICIAL_NIST_KAT_FIPS203`
   - **Source:** `references/test_vectors/mlkem_expected_kat.h`
   - **Keypair Seed ($d \parallel z$):** `test_vector_d` (32B) $\parallel$ `test_vector_z` (32B).
   - **Encapsulation Seed ($m$):** `test_vector_m` (32B).
   - **Purpose:** Anchors the test corpus to official NIST Known-Answer Test vectors.
2. **Vectors 1 through 419 (Locally Generated Candidate Vectors):**
   - **Provenance:** `LOCALLY_GENERATED_DETERMINISTIC_SHAKE256_PRF`
   - **Derivation Scheme:** Grounded directly in [combined_campaign.c:137-143, 210](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L137-L143).
   - For vector index $i \in [1, 419]$:
     $$\text{keygen\_seed}_i = \text{SHAKE256}(\text{"kemkp"} \parallel \text{uint64\_be}(i) \parallel 0_{64} \parallel 0_{64}, 64)$$
     $$\text{encaps\_seed}_i = \text{SHAKE256}(\text{"kemenc"} \parallel \text{uint64\_be}(i) \parallel 0_{64} \parallel 0_{64}, 32)$$
   - **Distinction Requirement:** Vectors 1–419 are deterministic local test vectors generated for experimental fault injection. They are **not official NIST-published vectors**.

---

## 3. Preflight Checks and Validation Outcomes

Every candidate vector $i \in [0, 419]$ was subjected to eight separate, non-collapsing checks:

| Check # | Check Name & Description | SUT API / Function | Oracle Reference | Evaluated | Passed |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **Check 1** | **Lengths & Offsets Verification**<br>Asserts key, ct, ss, and seed buffer sizes and $z$-offset ($2368$). | Static Assertions / `sizeof` | FIPS 203 Table 2 | 420 | **420** |
| **Check 2** | **SUT Deterministic Keypair Generation**<br>Generates $(pk, sk)$ from 64-byte seed; asserts return code 0. | `mlkem768_keypair_derand` | `mlkem-native` | 420 | **420** |
| **Check 3** | **Keypair Cross-Implementation Agreement**<br>Asserts $pk_{\text{SUT}} == pk_{\text{OQS}}$ (1,184B) and $sk_{\text{SUT}} == sk_{\text{OQS}}$ (2,400B). | `mlkem768_keypair_derand` | `independent_oracle_keypair_derand` (`liboqs`) | 420 | **420** |
| **Check 4** | **SUT Deterministic Encapsulation**<br>Generates $(ct, ss)$ from $pk$ and 32-byte seed; asserts return code 0. | `mlkem768_enc_derand` | `mlkem-native` | 420 | **420** |
| **Check 5** | **Encapsulation Cross-Implementation Agreement**<br>Asserts $ct_{\text{SUT}} == ct_{\text{OQS}}$ (1,088B) and $ss_{\text{SUT}} == ss_{\text{OQS}}$ (32B). | `mlkem768_enc_derand` | `independent_oracle_encaps_derand` (`liboqs`) | 420 | **420** |
| **Check 6** | **SUT Clean Decapsulation & Key Agreement**<br>Decapsulates clean $(ct, sk)$; asserts $ss_{\text{dec}} == ss_{\text{enc}}$ (32B) and rc 0. | `mlkem768_dec` | Encapsulated Shared Secret | 420 | **420** |
| **Check 7** | **Independent Rejection Oracle Derivation**<br>Computes $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct, 32)$; asserts $K_{\text{rej}} \neq ss$. | `independent_oracle_compute_rejection` | TweetFIPS-202 | 420 | **420** |
| **Check 8** | **Ciphertext-Tampering & Rejection Compliance**<br>Corrupts wire $\tilde{c} = ct \oplus 0x01$; asserts SUT decapsulation matches $K_{\text{rej}}(\tilde{c})$. | `mlkem768_dec` on $\tilde{c}$ | `independent_oracle_compute_rejection` on $\tilde{c}$ | 420 | **420** |

### 3.1 Epistemological Qualification of Ciphertext-Tampering (Check 8)
* **Observed Reality:** For all 420 candidate ciphertexts, introducing a single-bit alteration at byte 0 ($\tilde{c}[0] = ct[0] \oplus 0x01$) caused `mlkem768_dec` to return exit status 0 and output a 32-byte shared secret that matched the independently computed value $\text{SHAKE256}(z \parallel \tilde{c}, 32)$ byte-for-byte, while differing from the authentic shared secret.
* **Scope Boundary:** This confirms that the specific System Under Test (`mlkem-native`) implements FIPS 203 implicit rejection correctly on the tested bit-flipped inputs. **This is not asserted as a universal property of all arbitrary lattice implementations or arbitrary error patterns.**

---

## 4. Fail-Closed Audit and Integrity Verification

- **Total Candidates Generated:** **420**
- **Total Candidates Evaluated:** **420**
- **Total Candidates Fully Validated:** **420 (100.00%)**
- **Total Candidates Failed or Excluded:** **0**
- **Candidates Discarded or Re-sampled:** **0**
- **Harness Execution Time:** **98.64 ms** (average $0.23\text{ ms}$ per vector).
- **Harness Exit Code:** `0` (`EXIT_SUCCESS`).

---

## 5. Artifact Directory and SHA-256 Hashes `[DIRECTLY OBSERVED]`

All Gate A artifacts reside in the dedicated directory `research/phase18_gate_a/`:

| Artifact Path | SHA-256 Digest | Size (Bytes) | Role & Description |
| :--- | :--- | :---: | :--- |
| `research/phase18_gate_a/validate_vectors.c` | `518f45b427bcbe3942c877c86bc72c18d3d778e11bcdccd406ccc9846752e91a` | 27,357 | Standalone C validation harness |
| `research/phase18_gate_a/Makefile` | `edbb437cb64a0ae6e10eb538a6bb5463ba61923b17a5f2d00a0054417958fef6` | 836 | Build script with exact flags |
| `research/phase18_gate_a/gate_a_manifest.json` | `ae2d6341f378c24a214795878e6524b1161372c405e2f061e71a7e8351ca5f8f` | 174,797 | Deterministic vector specifications |
| `research/phase18_gate_a/gate_a_vector_corpus.json` | `19678a2f4183fc8bf1c166bf40d6bb17eabd457ba4b354d4083171d1f986be13` | 267,153 | Corpus of 420 validated vectors |
| `research/phase18_gate_a/gate_a_validation_records.jsonl` | `7868268a34a9b766ac58ca5ca20eea294d3ea6265f96c249f157fd3f7e39a149` | 305,211 | Per-vector records (420 lines) |
| `research/phase18_gate_a/gate_a_preflight_report.json` | `dd7ee21189ddb0fa1904b2f3b6236fceb18af71893f2f6a2e358a50ad6261a6e` | 1,014 | Machine-readable Gate A summary |
| `research/results/phase18_gates/gate_a_preflight_report.json` | `dd7ee21189ddb0fa1904b2f3b6236fceb18af71893f2f6a2e358a50ad6261a6e` | 1,014 | Mirrored Gate A summary artifact |

### 5.1 Verification Commands
To independently re-verify the Gate A harness and all 420 candidate vectors:
```bash
make -C research/phase18_gate_a clean
make -C research/phase18_gate_a run
```

---

## 6. Git Working Tree Status and Confirmation of Inaction `[DIRECTLY OBSERVED]`

```
 M Makefile
 M README.md
 M algorithms/source_ref/mlkem/src/poly.c
 M algorithms/source_ref/mlkem/src/zetas.inc
 M experiments/fault_injection/mlkem768_internal_fault_experiment.c
 M experiments/system_model/spacecraft_protocol_sim.py
 M fault_injection/fault_models/fault_definitions.py
 M results/phase7i/processed/phase7i_e2e_results.json
 M results/spacecraft_protocol_desync_results.json
 M tests/test_fips_kats.c
?? research/phase18_gate_a/
?? research/results/phase18_gates/
?? research/phase17_multi_fault_design/PHASE18H_GATE_A_REPORT.md
?? research/phase17_multi_fault_design/PHASE18H_CHANGELOG.md
```

### Confirmation of Inaction:
1. **Preservation of Tracked Changes:** All 10 pre-existing modified files in the working tree were preserved untouched.
2. **Zero Memory Mutations:** `vm_protect` was **never called**; virtual memory protection was unaltered.
3. **Zero Campaign Execution:** No trials under Gates B, C, D, or the full 1,680-trial campaign were executed.
4. **Zero Git Modification:** No files were staged, committed, pushed, reset, cleaned, or discarded.

---

## 7. Next-Phase Governance Boundary

Gate A is **formally completed with verdict PASS**.

However, under the governing implementation roadmap:
- **Proceeding to Gate B (Ledger Validator with Synthetic Fixtures) requires separate authorization.**
- **The full multi-fault campaign remains strictly unauthorized.**
