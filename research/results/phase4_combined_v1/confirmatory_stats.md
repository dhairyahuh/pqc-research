# Phase 4 combined-fault — CONFIRMATORY statistics (frame-relative)

- seeds analysed (paired, complete-case): 500; dropped seeds: 0
- total condition-trials: 2000

## per-condition P(key established) [bootstrap 95% CI over seeds]
- C00: 100.0%  [100.0%, 100.0%]  (n=500)
- C10: 48.0%  [43.6%, 52.4%]  (n=500)
- C01: 56.4%  [52.0%, 60.8%]  (n=500)
- C11: 26.0%  [22.2%, 30.0%]  (n=500)

## interaction  Delta = p11 - p10 - p01 + p00
- Delta_hat = +0.2160  [bootstrap 95% CI +0.1800, +0.2520]
- conditional on channel PERSISTENT: Delta=+0.4186 (n=258)
- conditional on channel TRANSIENT: Delta=+0.0000 (n=242)

## masking accounting — MASKED_BY_CHANNEL is NOT a recovered memory fault
- memory-injection status in C11 (denominator |C11|=500): {'ACTIVATED': 297, 'MASKED_BY_CHANNEL': 203}
- masking rate = 203/500 = 40.6% (memory armed + channel armed, memory never reached activation)
- established among MASKED = 57/203 (completion here is governed by the CHANNEL retry, not memory recovery)
- established among ACTIVATED = 73/297

_Frame-relative Monte-Carlo estimand over the pre-registered distribution F. NOT a physical probability, significance, or causal claim. Logical-value memory + simulated channel only; no persistent-storage/radiation/RF/qualification claim._
