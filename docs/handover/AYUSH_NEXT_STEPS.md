# Ayush's Onboarding Guide & Research Roadmap

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  

Welcome to the project, Ayush! This guide is designed to get you up to speed immediately, providing a prioritized, step-by-step path to take over ownership of this research without guesswork.

---

## 1. First Day: Orientation & Mental Model (2 Hours)

Your goal on Day 1 is to understand the core research question, branch state, and architecture:

1. **Read `AYUSH.md` completely:** It is your central reference manual.
2. **Read [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md):** The primary paper is concise (386 lines). Note how Section 3 (Derivations), Section 4 (Architecture), Section 6 (Results), and Section 7 (Boundaries) fit together.
3. **Verify Git State:**
   - Confirm active branch: `space-resilience-framework`.
   - Run `git status` to see the 10 pre-existing modified files. Do not reset or revert them!
4. **Inspect Core C Source Files:**
   - Open [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) around lines 510 and 656.
   - Open [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) around lines 462–525 (`mlk_kem_dec_monitored`).
   - Open [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) to inspect the invariant checking math and snapshot/rollback logic.

---

## 2. First Research Session: Low-Risk Reproductions (Half-Day)

Before designing new experiments, reproduce existing, verified results:

### Step 2.1: Run the NIST FIPS 203 & 204 KAT Runner
```bash
make clean
make bin/test_fips_kats
./bin/test_fips_kats
```
*Expected Result:* Clean PASS across all ML-KEM (512, 768, 1024) and ML-DSA (44, 65, 87) parameter sets.

### Step 2.2: Compile and Run the Production Reproducer
```bash
clang -O3 -Wall -Wextra -std=c11 -I. -Ialgorithms/source_ref/mlkem \
  phase18_audit/production_reproducer.c bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o phase18_audit/production_reproducer
./phase18_audit/production_reproducer
```
*Expected Result:* Executes 400 cleanroom trials; confirms 100% recovery for F4 transient faults and 100% fail-stop containment for F5 persistent faults.

### Step 2.3: Recompute Confidence Intervals
Run the Python statistical validator:
```bash
python3 -c '
import math

def wilson(k, n, z=1.95996):
    p = k/n; d = 1 + z**2/n; c = (p + z**2/(2*n))/d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2))/d
    return max(0.0, c-hw), min(1.0, c+hw)

print("F4 Recovery (100/100):", [f"{x*100:.2f}%" for x in wilson(100, 100)])
print("F5 Containment (200/200):", [f"{x*100:.2f}%" for x in wilson(200, 200)])
print("Production SDC (0/300):", [f"{x*100:.2f}%" for x in wilson(0, 300)])
print("Campaign SDC (0/750 97.5% CP):", f"{(1 - (0.025)**(1/750))*100:.2f}%")
print("Circular Blindness (591/600):", [f"{x*100:.1f}%" for x in wilson(591, 600)])
'
```
*Expected Output:*
- F4: `['96.30%', '100.00%']`
- F5: `['98.12%', '100.00%']`
- Production SDC: `['0.00%', '1.26%']`
- Campaign SDC: `0.49%`
- Circular Blindness: `['97.2%', '99.2%']`

---

## 3. Second Week: Future Research Roadmap

Once onboarding is complete, prioritize these high-value research directions:

### Priority 1: 32-Bit Embedded Cross-Compilation & Benchmarking
- **Hypothesis:** Single-butterfly localized rollback delivers equal or greater latency advantage on embedded microcontrollers (where full decapsulation is 10–50x slower in absolute time).
- **Target Platforms:** ARM Cortex-M4 (e.g., STM32F4 Discovery board or QEMU), RISC-V RV32IM.
- **Measurable Outcomes:** Cycle count overhead under `-O3`, peak dynamic stack memory growth.
- **Impact:** Directly bridges the platform limitation stated in Section 8 Item 2 of the manuscript.

### Priority 2: Microarchitectural Timing Leakage Analysis (TVLA / dudect)
- **Hypothesis:** In fault-free execution, source-level branch-free mask accumulation exhibits zero detectable timing leakage across $100{,}000$ fixed-vs-random ciphertexts.
- **Tools:** Use `dudect` (Dude, is my code constant time?) or chipwhisperer TVLA harness.
- **Impact:** Provides empirical backing for side-channel security in fault-free execution.

### Priority 3: Expanded Twiddle Factor Memory Corruption Campaign
- **Hypothesis:** Downstream Fujisaki-Okamoto re-encryption maintains 100% implicit rejection containment across arbitrary random keys, arbitrary ciphertexts, and multi-bit twiddle perturbations.
- **Experiment:** Expand Phase 15Q from 16 trials on 1 vector to 500 trials across randomized keypairs.
- **Impact:** Elevates the twiddle factor boundary from a controlled pilot to a multi-orbit statistical distribution.

### Priority 4: Conference / Journal Submission Formatting
- **Target Venues:** IEEE Transactions on Computer-Aided Design (TCAD), ACM TECS, IEEE Transactions on Nuclear Science (TNS), or IACR TCHES.
- **Action:** Export `paper/manuscript.md` into the IEEE/ACM LaTeX template (`paper/references.bib` already contains all 18 BibTeX citations). Preserve all footnotes and limitation disclosures verbatim.

---

## 4. Strict Protocol: What NOT to Do

1. **Do not modify `paper/manuscript.md` unnecessarily:** The manuscript has undergone 10 rigorous audit iterations and is formally verified as **READY WITH EXPLICIT LIMITATIONS**. Do not perform cosmetic text rewrites.
2. **Do not claim physical radiation tolerance:** We evaluate software architectural bitflips. Do not write "space-qualified" or "radiation-hardened" without cyclotron beam data.
3. **Do not claim certified constant-time binary execution:** Always maintain the disclosure in Section 7 Item 4.
4. **Do not delete backups or raw CSVs:** Never clean or prune `paper/manuscript.md.backup_*` or root-level `phase*` folders. They are required to prove provenance.
5. **Do not force-push or rewrite Git history:** Always use clean, forward commits.
