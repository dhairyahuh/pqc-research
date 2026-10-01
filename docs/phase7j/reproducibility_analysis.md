# Phase 7J: Reproducibility Analysis & Cryptographic Contract Audit

## 1. Independent Python Audit of Phase 7I Datasets

The Phase 7I raw dataset was subjected to an independent audit via `experiments/phase7j/audit_phase7i_analysis.py`:
- Ingestion of 1,400 raw JSON trial records from `results/phase7i/raw/phase7i_e2e_trials.json`.
- Verification of schema: every trial contains `trial_id`, `fault_class`, `stage`, `butterfly`, `status`, `recovered`, `mismatches`, and `outcome`.
- No ID collisions or gaps were found ($0 \le \text{trial\_id} \le 1399$).
- Outcome counts strictly recomputed without discrepancies.
- Verified that all 700 transient arithmetic trials achieved autonomous recovery, and all 583 unrecoverable trials resulted in safe rejection ($R_{\text{und}} = 0.00\%$).

---

## 2. Cryptographic Contract Clarification: Ciphertext-Bound Rejection

During the independent audit of the public API fail-stop contract, a critical cryptographic subtlety in NIST FIPS 203 was highlighted:

### Mathematical Definition of Implicit Rejection
In FIPS 203 Algorithm 17 (`ML-KEM.Decaps_internal`), when ciphertext re-encryption does not match the input ciphertext $c$, the rejection key is computed as:
$$K = J(z \parallel c, 32)$$
where $z$ is the 32-byte secret seed embedded in the secret key $sk$, and $c$ is the **exact ciphertext input provided to the decapsulation function**.

### Audit Finding on Test Methodology:
- In test harnesses evaluating safe rejection under a corrupted ciphertext $c_{\text{corrupt}}$, the expected rejection key is $K_{\text{rej}}(c_{\text{corrupt}}) = J(z \parallel c_{\text{corrupt}})$.
- In contrast, when evaluating a **persistent hardware fault occurring during decapsulation of a valid ciphertext** $c_{\text{valid}}$, the fail-stop mechanism forces `fail = 0xFF`. The resulting rejection key is $K_{\text{rej}}(c_{\text{valid}}) = J(z \parallel c_{\text{valid}})$.
- Comparing the output of a persistent fault on $c_{\text{valid}}$ against a fixed rejection key generated from a different ciphertext $c'$ would yield a false-positive mismatch.
- The Phase 7J validator implemented `get_rejection_key_for_ct(out_rej, ct, sk)` to dynamically evaluate the correct ciphertext-bound rejection key. The test proved that `mlkem768_dec(ss, ct_valid, sk)` under persistent faults emits **exactly** $K_{\text{rej}}(c_{\text{valid}})$, preserving standard cryptographic behavior without leaking private information.

---

## 3. Step-by-Step Reproducibility Instructions

To reproduce all Phase 7J findings from a clean checkout:

### 1. Compile the Independent Validator
```bash
make phase7j
```
*Compiler Flags*: `-O3 -Wall -Wextra -std=c11 -I. -Ialgorithms/source_ref/mlkem`  
*Artifact*: `bin/phase7j_independent_validator`

### 2. Run the Full Phase 7J Test and Audit Suite
```bash
make test-phase7j
```
This single make target:
1. Executes `experiments/phase7j/audit_phase7i_analysis.py` to audit Phase 7I raw data.
2. Executes `./bin/phase7j_independent_validator` to run all 16 extended threat classes (1,600 trials), multi-run benchmarks (6,000 iterations), and randomized-order timing (1,000 pairs).
3. Executes `python3 -m unittest discover -s tests/phase7j -v` to verify all assertions.

### 3. Verify Historical Phases and Known Answer Tests
```bash
make test-phase7i
python3 -m unittest discover -s tests/phase7h -v
python3 -m unittest discover -s tests/phase7g -v
python3 -m unittest discover -s tests/phase7f -v
./bin/test_fips_kats
```
All KAT vectors (ML-KEM-512/768/1024 and ML-DSA-44/65/87) pass with 100% precision.
