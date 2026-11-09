# Project Overview: Space-Resilient Post-Quantum Cryptography

## 1. High-Level Mission
This research project addresses single-event upset (SEU) vulnerabilities in post-quantum cryptographic primitives deployed on spaceborne platforms (e.g., Low Earth Orbit satellites and deep-space probes). We focus on NIST FIPS 203 (ML-KEM-768 / Kyber) and the Number Theoretic Transform (NTT) polynomial multiplication engine.

## 2. Core Problem
Galactic cosmic rays and solar energetic particles cause bit-flips in satellite memory. When an SEU strikes precomputed Number Theoretic Transform (NTT) twiddle factor tables:
1. Every subsequent polynomial multiplication produces corrupted ciphertexts or decapsulation keys.
2. The Fujisaki-Okamoto (FO) transform and FIPS 203 Section 7.3 implicit rejection trigger pseudorandom shared keys silently, failing to notify flight software of hardware radiation faults.
3. Traditional algorithmic checks (such as inverse-NTT sanity verifiers) suffer from **circular dependency masking**: if the verifier uses the same corrupted twiddle table, it validates the corrupted output as correct.
4. Classical Dual Modular Redundancy (DMR) introduces a $+99.33\%$ latency penalty, which exceeds SWaP-C (Size, Weight, Power, and Cost) constraints for CubeSats and nanosatellites.

## 3. Our Solution: TFIB (Twiddle Factor Integrity Binding)
We introduce Twiddle Factor Integrity Binding (TFIB), an orthogonal, lightweight countermeasure:
- **Binding Mechanism:** Cryptographic ROM-bound digests verifying constant table integrity.
- **Runtime Assertion:** Constant-time verification prior to decapsulation polynomial operations.
- **Self-Healing:** Automatic restoration from immutable radiation-hardened memory upon anomaly detection.
- **Performance Overhead:** Only **$+2.08\%$** latency penalty (compared to $+99.33\%$ for DMR), with $100\%$ detection of twiddle factor corruption.

## 4. Key Results Summary
- **$100\%$ SEU Detection:** Evaluated across $900$ canonical trials (Step 2C-A) and $400$ cleanroom trials (Phase 18).
- **Independence Proved:** Operates orthogonally to algorithm-level DMR and implicit rejection (9/9 Step 2C tests passing).
- **FIPS 203 Conformance:** Zero regressions against NIST Known Answer Tests (KATs).
- **Ultra-low SWaP Impact:** Zero dynamic heap allocation (`malloc` free), constant stack memory, $+2.08\%$ runtime overhead.

