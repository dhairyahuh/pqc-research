# Phase 2 Comprehensive Fault Campaign — Executive Summary

## Overview
- Total campaigns executed: 117
- Standard: NIST FIPS 203 (ML-KEM-512, ML-KEM-768, ML-KEM-1024)
- Pinned implementation: `mlkem-native` (fc269bc2d1068486625a3775310c2c1f28d74732)
- Cross-implementation oracle: `liboqs 0.16.0`
- Total injected trials: >150,000 across all campaigns and baseline controls

## Key Empirical Discoveries
1. **NTT Diffusion Tree Exactness (Phase 1 Claim 1 Verified)**:
   - Analytical prediction $N_\text{diffused}^\text{shared}(L) = 2^{8-L}$ and $N_\text{diffused}^\text{single}(L) = 2^{7-L}$ matches empirical observations across all 7 layers with **zero deviation**.
2. **Butterfly Locus Sensitivity Bifurcation**:
   - Single output register perturbations (`OUTPUT_ADD`) in ML-KEM-768/1024 have peak time-domain error $\|e_\text{time}\|_\infty = 524 < 832.25 = \lfloor q/4 \rfloor$. Re-encryption recovers $c'=c$ yielding **100% CORRECT** decapsulation.
   - Shared intermediate perturbations (`INTERMEDIATE_T`) propagate to both butterfly branches ($+t, -t$), resulting in peak time-domain error $\|e_\text{time}\|_\infty = 1048 > 832.25$. Message bits flip ($m' \neq m$), triggering **100% IMPLICIT_REJECTION**.
3. **Parameter-Set Sensitivity Divergence (ML-KEM-512 vs 768/1024)**:
   - In ML-KEM-512, noise parameter $\eta_1 = 3$ (vs $\eta_1 = 2$ in 768/1024), scaling base-multiplication error by $1.5\times$. This eliminates decapsulation slack and causes single output register faults to produce **100% IMPLICIT_REJECTION**.
4. **Secret-Key Memory Region Dissection**:
   - Polynomial vector $\mathbf{s}$: 100% `IMPLICIT_REJECTION`.
   - Public key bytes $pk$: 100% `EXPLICIT_ERROR` (via `check_pk` modulus/hash check).
   - Cached public key hash $H(pk)$: 100% `EXPLICIT_ERROR` (hash mismatch trap).
   - PRF rejection seed $z$: 100% `CORRECT` for valid ciphertexts (seed $z$ is isolated to the rejection path $c \neq c'$).
5. **Quantization Absorption & Local Tolerance (Phase 1 Claim 2 Verified)**:
   - Universal worst-case tolerance $T_\text{worst}(d, q) = 1$ for all tested bit-depths $d \in \{4, 5, 10, 11\}$. Any fault $\ge 1$ adjacent to a quantization boundary causes immediate bit-flip. Guaranteed non-zero margin does not exist.
