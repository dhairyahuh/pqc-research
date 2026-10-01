# NTT Forward Transform Diffusion Validation (ML-DSA Native 8 Layers)

| Layer $L$ | Locus | Mathematical Prediction | Observed Perturbed Coefficients | Diff | Structural Interpretation |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `INTERMEDIATE_T` (Shared) | $2^{9-1} = 256$ | 256 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 1 | `OUTPUT_ADD` (Single)     | $2^{8-1} = 128$ | 128 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 2 | `INTERMEDIATE_T` (Shared) | $2^{9-2} = 128$ | 128 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 2 | `OUTPUT_ADD` (Single)     | $2^{8-2} = 64$ | 64 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 3 | `INTERMEDIATE_T` (Shared) | $2^{9-3} = 64$ | 64 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 3 | `OUTPUT_ADD` (Single)     | $2^{8-3} = 32$ | 32 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 4 | `INTERMEDIATE_T` (Shared) | $2^{9-4} = 32$ | 32 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 4 | `OUTPUT_ADD` (Single)     | $2^{8-4} = 16$ | 16 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 5 | `INTERMEDIATE_T` (Shared) | $2^{9-5} = 16$ | 16 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 5 | `OUTPUT_ADD` (Single)     | $2^{8-5} = 8$ | 8 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 6 | `INTERMEDIATE_T` (Shared) | $2^{9-6} = 8$ | 8 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 6 | `OUTPUT_ADD` (Single)     | $2^{8-6} = 4$ | 4 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 7 | `INTERMEDIATE_T` (Shared) | $2^{9-7} = 4$ | 4 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 7 | `OUTPUT_ADD` (Single)     | $2^{8-7} = 2$ | 2 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
| 8 | `INTERMEDIATE_T` (Shared) | $2^{9-8} = 2$ | 2 | 0 | Exact match. Intermediate product diffuses into both butterfly branches. |
| 8 | `OUTPUT_ADD` (Single)     | $2^{8-8} = 1$ | 1 | 0 | Exact match. Unilateral register glitch propagates forward through sub-tree. |
