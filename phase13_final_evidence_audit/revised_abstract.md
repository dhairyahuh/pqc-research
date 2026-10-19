# Revised Academic Abstract

**Title:** On the Resilience Boundaries of Local Recovery Verifiers and the Fujisaki-Okamoto Transform in ML-KEM-768  
**Target Venue:** IEEE Transactions on Information Forensics and Security (TIFS) / CHES  
**Authors:** Research Team  
**Date:** October 2026  

---

## Abstract

Implementing post-quantum cryptography on physical embedded devices requires resilience against both transient radiation-induced upsets and deliberate fault injection attacks. Recent proposals incorporate local retry-and-verify arithmetic monitors into the Number Theoretic Transform (NTT) to recover from single-event upsets without full decapsulation restart. This paper presents an independent, skeptical experimental audit of the resilience boundaries of the native ML-KEM-768 decapsulation engine under compiled production and simulated fault models.

We evaluate two fundamental security hypotheses: whether localized recovery verifiers can falsely declare success when reference operands are corrupted ($H_1$), and whether such internal blindness can cause an invalid shared secret to be accepted at the decapsulation API boundary ($H_2$). Using a clean-room Keccak-f[1600] / SHAKE256 output oracle verified independently against NIST FIPS 202/203 rate-boundary vectors, we evaluate 1,300 trials across 13 fault configurations. We demonstrate that in software models where snapshot state is perturbed, in-place recovery verifiers exhibit complete verifier blindness in 93.5% of trials (561/600, 95% Wilson CI: [91.2%, 95.2%]) due to algebraic cancellation. 

Conversely, in authentic compiled production binaries, the in-tree monitor achieves 100% genuine recovery under transient butterfly bit-flips (100/100) and 100% safe fail-stop under recurring bit-inversions and software force-value faults (200/200). Across all 1,300 evaluated trials, zero instances of Silent Data Corruption occurred ($H_2 = 0.0\%$, 95% Wilson CI: [0.0%, 0.28%]). We prove that the outer Fujisaki-Okamoto re-encryption transform functions as an unconditional cryptographic firewall, reliably trapping internal arithmetic corruptions and emitting the canonical FIPS 203 implicit rejection key ($K_{\text{bar}} = \text{SHAKE256}(z \parallel c, 32)$). Our findings establish the fundamental defense-in-depth provided by the FIPS 203 protocol structure while identifying critical architectural constraints for future hardware-isolated recovery verifiers.
