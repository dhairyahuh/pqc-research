# Phase 4 combined-fault — PILOT statistics (frame-relative)

- seeds analysed (paired, complete-case): 20; dropped seeds: 0
- total condition-trials: 80

## per-condition P(key established) [bootstrap 95% CI over seeds]
- C00: 100.0%  [100.0%, 100.0%]  (n=20)
- C10: 40.0%  [20.0%, 60.0%]  (n=20)
- C01: 50.0%  [30.0%, 70.0%]  (n=20)
- C11: 20.0%  [5.0%, 40.0%]  (n=20)

## interaction  Delta = p11 - p10 - p01 + p00
- Delta_hat = +0.3000  [bootstrap 95% CI +0.1000, +0.5000]
- conditional on channel PERSISTENT: Delta=+0.6000 (n=10)
- conditional on channel TRANSIENT: Delta=+0.0000 (n=10)

## masking accounting — MASKED_BY_CHANNEL is NOT a recovered memory fault
- memory-injection status in C11 (denominator |C11|=20): {'ACTIVATED': 11, 'MASKED_BY_CHANNEL': 9}
- masking rate = 9/20 = 45.0% (memory armed + channel armed, memory never reached activation)
- established among MASKED = 2/9 (completion here is governed by the CHANNEL retry, not memory recovery)
- established among ACTIVATED = 2/11

_Frame-relative Monte-Carlo estimand over the pre-registered distribution F. NOT a physical probability, significance, or causal claim. Logical-value memory + simulated channel only; no persistent-storage/radiation/RF/qualification claim._
