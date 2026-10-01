# ML-KEM (FIPS 203) vs ML-DSA (FIPS 204) Fault Sensitivity Comparison

| Structural / Cryptographic Property | ML-KEM (Key Encapsulation) | ML-DSA (Digital Signatures) | Cross-Algorithm Implication |
|:---|:---|:---|:---|
| **NTT Layer Count** | 7 Layers ($q = 3329$, 128 degree-2 blocks) | 8 Layers ($q = 8380417$, 256 degree-1 blocks) | ML-DSA decomposes fully; error diffusion extends one layer deeper ($2^{9-L}$). |
| **Internal Decapsulation / Signing Structure** | Forward linear pipeline + re-encryption check | Non-deterministic / Rejection sampling loop | Faults in ML-DSA cause attempt looping and potential DoS before signature emission. |
| **Fault Containment Barrier** | Fujisaki-Okamoto (FO) transform implicit rejection | Norm checking bounds ($\|z\|_\infty, \|w_0\|_\infty$) + hint bound | Both algorithms fail-closed naturally; ML-KEM returns pseudorandom key, ML-DSA retries or aborts. |
| **Tolerance to Small Register Glitches** | Slack budget $\lfloor q/4 \rfloor = 832$ masks single `OUTPUT_ADD` faults in 768/1024 | Zero slack: arithmetic perturbation in verification alters hash commitment $c'$ | ML-KEM has local decapsulation error tolerance; ML-DSA verification has zero error tolerance. |
| **Verification / Acceptance Bypass** | N/A (Decapsulation produces valid or pseudorandom key) | Critical vulnerability: flipping `cmp` produces `INVALID -> ACCEPT` (100%) | ML-DSA verification gate is a single-point-of-failure vulnerable to control glitches. |
| **Private Key Memory Regions** | $\mathbf{s}, pk, H(pk), z$ | $\rho, K, tr, \mathbf{s}_1, \mathbf{s}_2, \mathbf{t}_0$ | Different layouts; seed $z$ in ML-KEM vs seed $K$ in ML-DSA have contrasting fault behaviors. |
