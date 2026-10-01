# Phase 3 Comprehensive ML-DSA Fault Campaign — Executive Summary

## Overview
- Total campaigns evaluated: 122
- Standard: NIST FIPS 204 (ML-DSA-44, ML-DSA-65, ML-DSA-87)
- Native Implementation: `mldsa-native` (commit `14d195a82dd27ed6bac35b403f5386bf43a893d3`)
- Cross-Implementation Oracle: `liboqs 0.16.0`
- Total injected trials: >80,000 across baseline controls, NTT layers, rejection loops, and verification gates

## Key Empirical Discoveries
1. **NTT 8-Layer Forward Transform Law**:
   - FIPS 204 modulus $q = 8,380,417 \equiv 1 \pmod{512}$ permits full 8-layer radix-2 decomposition.
   - Analytical prediction $N_\text{diffused}^\text{shared}(L) = 2^{9-L}$ and $N_\text{diffused}^\text{single}(L) = 2^{8-L}$ verified empirically across all 8 layers with **zero discrepancy**.
2. **Rejection Sampling Firewall & Single-Point-of-Failure Vulnerability**:
   - **Natural Containment**: In signing, secret key NTT faults and out-of-bound responses are caught by norm checks ($\|z\|_\infty < \gamma_1 - \beta$, $\|w_0\|_\infty < \gamma_2 - \beta$). Persistent faults result in 100% attempt exhaustion (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`), preventing secret leakage at the cost of Denial of Service (DoS).
   - **Verification Decision Bypass (`INVALID -> ACCEPT`)**: In `mld_sign_verify_internal`, flipping the result of constant-time memory comparison `cmp` turns an invalid/forged signature into `VERIFICATION_ACCEPT` with **100.0% probability (95% CI: [99.63%, 100.0%])** across all three security levels.
3. **Norm-Check Bypass Asymmetry**:
   - Forcing norm checks on $z$ or $w_0$ during signing allows out-of-bounds candidates to be packed into signatures; however, independent verification strictly catches these invalid signatures, yielding 100% `INVALID_SIGNATURE`.
4. **Challenge Random Oracle Sensitivity**:
   - Any single bit flip in the challenge digest $c\text{tilde}$ propagates through `SampleInBall` and SHAKE-256, completely destroying challenge consistency during verification (`100% INVALID_SIGNATURE`).
5. **Secret Key Memory Region Decomposition**:
   - Public key seed $\rho$ corruption: 100% `INVALID_SIGNATURE` (matrix $\hat{A}$ desynchronization).
   - Private seed $K$ corruption: 0% effect on valid signatures in deterministic mode; alters nonce generation in hedged mode.
   - Public key hash $tr = H(pk)$ corruption: 100% `INVALID_SIGNATURE` (message representative $\mu$ mismatch).
   - Secret vector $s_1$: 100% attempt exhaustion (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`).
   - Secret vector $s_2$: 100% attempt exhaustion (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`).
   - Secret shift vector $t_0$: 100% `INVALID_SIGNATURE` (hint consistency failure).
