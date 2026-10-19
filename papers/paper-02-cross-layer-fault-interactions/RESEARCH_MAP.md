# Paper Track 2 — Cross-Layer Fault Interactions

## RESEARCH MAP

**Status:** DEFER  
**Rationale:** The spacecraft protocol simulator exists but lacks independent validation, controlled experimental design, and sufficient evidence to stand alone. The cross-layer interaction concept enriches Paper Track 1 but is not ready as an independent publication.

---

## Provisional Title
"Cross-Layer Fault Propagation in Post-Quantum Cryptographic Protocol Stacks for Space Systems"

## Research Question
How do faults in ML-KEM NTT operations propagate through Fujisaki-Okamoto re-encryption, session key derivation, and protocol framing layers, and what are the cross-layer failure modes?

## Implementation Components
| Component | Location |
|:---|:---|
| Spacecraft protocol sim | `experiments/system_model/spacecraft_protocol_sim.py` (modified) |
| Protocol desync results | `results/spacecraft_protocol_desync_results.json` (modified) |

## Existing Evidence
- Spacecraft sim shows 100% FORMAT_REJECTED on desync `[REPORTED]`
- FO ciphertext comparison acts as outer failsafe `[REPORTED — strengthens Track 1]`

## Unverified Claims
- Cross-layer propagation paths not systematically characterized
- No independent reproduction of protocol sim results
- No controlled baseline comparison

## Provisional Decision: **DEFER**
- The FO containment finding should be folded into Paper Track 1
- Cross-layer analysis can be proposed as future work
