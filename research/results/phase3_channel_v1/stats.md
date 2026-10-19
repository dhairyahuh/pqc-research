# Phase 3 channel-fault — outcome statistics

- total sessions: 600
- INCONCLUSIVE: 0 (gate: expect 0)

## protocol_outcome (overall, Wilson 95% CI)
- KEY_ESTABLISHED: 100/600 = 16.7% [13.9%, 19.9%]
- MALFORMED_MESSAGE: 100/600 = 16.7% [13.9%, 19.9%]
- MESSAGE_LOST: 100/600 = 16.7% [13.9%, 19.9%]
- PROTOCOL_ABORT: 50/600 = 8.3% [6.4%, 10.8%]
- RECOVERED_ON_RETRY: 200/600 = 33.3% [29.7%, 37.2%]
- TIMEOUT_RETRY_EXHAUSTED: 50/600 = 8.3% [6.4%, 10.8%]

## crypto_verdict (SEPARATE dimension — not a protocol outcome)
- REJECT: 50
- UNAVAILABLE: 200
- VALID: 350

## per-suite protocol_outcome
- BIT_CORRUPTION_PERSISTENT (n=50): PROTOCOL_ABORT=50
- BIT_CORRUPTION_TRANSIENT (n=50): RECOVERED_ON_RETRY=50
- CLEAN_BASELINE (n=50): KEY_ESTABLISHED=50
- DELAY_PERSISTENT (n=50): TIMEOUT_RETRY_EXHAUSTED=50
- DELAY_TRANSIENT (n=50): RECOVERED_ON_RETRY=50
- DUPLICATION (n=50): KEY_ESTABLISHED=50
- INTERRUPTION_PERSISTENT (n=50): MESSAGE_LOST=50
- PACKET_LOSS_PERSISTENT (n=50): MESSAGE_LOST=50
- PACKET_LOSS_TRANSIENT (n=50): RECOVERED_ON_RETRY=50
- REORDER_PERSISTENT (n=50): MALFORMED_MESSAGE=50
- TRUNCATION_PERSISTENT (n=50): MALFORMED_MESSAGE=50
- TRUNCATION_TRANSIENT (n=50): RECOVERED_ON_RETRY=50

_Note: no statistical-significance or causal claim; counts describe a deterministic software emulator. Not real radio-link behavior, space qualification, or radiation._
