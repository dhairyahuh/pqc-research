# Research Scope & Boundaries

## In-Scope

1. **Target Algorithms:**
   - NIST FIPS 203: ML-KEM-768 (Kyber-768) key encapsulation mechanism.
   - Comparative evaluation with ML-DSA (Dilithium) NTT structures.
2. **Threat Model:**
   - Single-event upsets (SEUs) and single-event transients (SETs) in space environments (LEO, GEO, deep space).
   - Bit-flips occurring in volatile SRAM/registers storing precomputed NTT twiddle factor tables (`zetas`).
   - Software fault injection simulating orbital radiation events.
3. **Countermeasure Architecture:**
   - Pre-computation integrity verification via cryptographically bound immutable ROM digests.
   - Microsecond self-healing restoration from write-protected storage.
   - Zero dynamic heap allocation (`malloc` free) compliant with NASA/ESA space flight software standards.
4. **Target Hardware / Toolchain:**
   - C99 standard compliant.
   - Apple M3 Pro benchmarking and embedded POSIX-compliant environments.

## Out-of-Scope (Deliberate Boundaries)

1. **Physical Beam Testing:** Physical heavy-ion accelerator or proton beam testing on actual silicon was not performed; all fault injections are software-simulated bit-flips modeled on standard Poisson particle strike distributions.
2. **Physical Side-Channel Attacks:** Power analysis (DPA/CPA) and electromagnetic radiation side-channels are not within the scope of this fault resilience study.
3. **Formal Verification Proofs:** Mechanized Coq/EasyCrypt proofs of constant-time execution and fault freedom are proposed future work, not claims of the current implementation.
4. **Non-NTT Post-Quantum Algorithms:** Hash-based (SLH-DSA) and stateful signature schemes that do not utilize NTT polynomial engines are excluded.

