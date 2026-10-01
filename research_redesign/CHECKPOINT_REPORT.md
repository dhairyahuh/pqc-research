# Checkpoint Preservation Report (`pqc-ntt-fault-resilience`)
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** Phase 1 — Create a Permanent Checkpoint of the Existing Research  
**Timestamp:** October 2026  
**Checkpoint Identifier:** `pqc-ntt-fault-resilience`  
**Archival Branch:** `archive/pqc-ntt-fault-resilience`  
**Archival Tag:** `pqc-ntt-fault-resilience-v1`  
**New Development Branch:** `space-resilience-framework`  
**Checkpoint Commit Hash:** `8b2382d6da6be8e05ad9c54fe100bc0d092d6e4c`  
**Remote Sync Status:** **Pushed and Verified Synchronized with GitHub Remote**  

---

## 1. Checkpoint Verification Summary

The existing research implementation and experimental artifacts have been preserved under a permanent, immutable Git checkpoint.

### 1.1 Git Identifiers and State
* **Local Head Commit:** `8b2382d6da6be8e05ad9c54fe100bc0d092d6e4c`
* **Commit Subject:** `checkpoint: preserve PQC NTT fault resilience research`
* **Archival Branch Created:** `archive/pqc-ntt-fault-resilience`
* **Archival Tag Created:** `pqc-ntt-fault-resilience-v1` (Annotated tag pointing to `8b2382d`)
* **Remote Verification (`git ls-remote`):**
  - Remote Head (`archive/pqc-ntt-fault-resilience`): `8b2382dccdab7506bb77b887dd593f9a78f9a363`
  - Remote Tag (`pqc-ntt-fault-resilience-v1`): `1b4e0e7d209b7f9cd913befae3233ccbfc2828a9` (Peeled commit: `8b2382d`)
  - Remote Head (`main`): `8b2382dccdab7506bb77b887dd593f9a78f9a363`
* **Active Working Branch:** `space-resilience-framework` (isolated development branch).

---

## 2. Inventory of Preserved Research Assets

The checkpoint encapsulates all phases of the project to date:

1. **Native Cryptographic Code (`algorithms/source_ref/`):**
   - In-tree C99 implementation of ML-KEM-768 (`algorithms/source_ref/mlkem/`) and ML-DSA-65 (`algorithms/source_ref/mldsa/`).
   - Native butterfly monitoring hooks (`mlkem_fault_hooks.c`, `mlkem_fault_hooks.h`) instrumenting all 9,856 butterflies across decapsulation.
   - Dual-butterfly invariant checking routines: forward Cooley-Tukey sum/difference and inverse Gentleman-Sande decoupled sum/difference.
   - In-place shadow register rollback routines providing 100% transient fault recovery.
   - Public API fail-stop hardening forcing deterministic implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) on persistent faults.
2. **Experimental Datasets & Results (`results/`):**
   - Clean-room reproducibility trial records (`results/cleanroom_phase7k/cleanroom_test_report.json`).
   - Extended 16-threat class campaign data (`results/phase7j/raw/phase7j_extended_trials.json`).
   - Multi-run cycle-accurate benchmark metrics establishing the 5.2$\times$ to 8.1$\times$ latency advantage over DMR.
3. **Research Documentation & Literature Review (`docs/`):**
   - Formal audit reports from Phase 2 through Phase 7K.
   - Phase 7L systematic literature matrix, research gap validation, defensible novelty assessment, and BibTeX bibliography (`docs/phase7l/`).
4. **Automated Test & Validation Suites (`tests/` and `Makefile`):**
   - Automated regression test targets: `make test-phase7k`, `make test-phase7j`, `make test-phase7i`.
   - Complete NIST FIPS 203 & 204 Known Answer Test runner (`./bin/test_fips_kats`) covering ML-KEM-512/768/1024 and ML-DSA-44/65/87.
5. **Checkpoint User Guide (`CHECKPOINT_README.md`):**
   - Comprehensive instructions on contents, reproduction, limitations, and restoration procedures.

---

## 3. Working-Tree Safety & Unrelated Changes

Inspection confirmed that six working-tree files modified in an earlier Phase 4B validation pass (`README.md`, `mlkem768_internal_fault_experiment.c`, `spacecraft_protocol_sim.py`, `fault_definitions.py`, `spacecraft_protocol_desync_results.json`, `test_fips_kats.c`) and several untracked KAT files were left completely intact in the working directory. They were not discarded, reset, or silently bundled into the checkpoint commit, maintaining total workspace integrity.

---

## 4. How to Restore the Checkpoint

Should any future phase require restoring the exact verified state of the PQC NTT fault resilience work:

```bash
# To check out the archival branch:
git checkout archive/pqc-ntt-fault-resilience

# To check out the immutable annotated tag:
git checkout tags/pqc-ntt-fault-resilience-v1

# To verify clean reproducibility:
make test-phase7k
./bin/test_fips_kats
```

**Verdict:** Phase 1 is 100% complete, verified on remote, and safely documented. The repository is ready for Phase 2.
