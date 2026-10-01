# NTT Forward Transform Diffusion Validation (Phase 1 vs Phase 2)

| Layer $L$ | Locus | Phase 1 Analytical Prediction | Phase 2 Empirical Observed | Difference | Interpretation |
|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | `INTERMEDIATE_T` (Shared) | $2^{8-1} = 128$ | 128 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 1 | `OUTPUT_ADD` (Single)     | $2^{7-1} = 64$ | 64 | 0 | Exact agreement. Unilateral register perturbation. |
| 2 | `INTERMEDIATE_T` (Shared) | $2^{8-2} = 64$ | 64 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 2 | `OUTPUT_ADD` (Single)     | $2^{7-2} = 32$ | 32 | 0 | Exact agreement. Unilateral register perturbation. |
| 3 | `INTERMEDIATE_T` (Shared) | $2^{8-3} = 32$ | 32 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 3 | `OUTPUT_ADD` (Single)     | $2^{7-3} = 16$ | 16 | 0 | Exact agreement. Unilateral register perturbation. |
| 4 | `INTERMEDIATE_T` (Shared) | $2^{8-4} = 16$ | 16 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 4 | `OUTPUT_ADD` (Single)     | $2^{7-4} = 8$ | 8 | 0 | Exact agreement. Unilateral register perturbation. |
| 5 | `INTERMEDIATE_T` (Shared) | $2^{8-5} = 8$ | 8 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 5 | `OUTPUT_ADD` (Single)     | $2^{7-5} = 4$ | 4 | 0 | Exact agreement. Unilateral register perturbation. |
| 6 | `INTERMEDIATE_T` (Shared) | $2^{8-6} = 4$ | 4 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 6 | `OUTPUT_ADD` (Single)     | $2^{7-6} = 2$ | 2 | 0 | Exact agreement. Unilateral register perturbation. |
| 7 | `INTERMEDIATE_T` (Shared) | $2^{8-7} = 2$ | 2 | 0 | Exact agreement. Shared twiddle product perturbs both branches. |
| 7 | `OUTPUT_ADD` (Single)     | $2^{7-7} = 1$ | 1 | 0 | Exact agreement. Unilateral register perturbation. |
