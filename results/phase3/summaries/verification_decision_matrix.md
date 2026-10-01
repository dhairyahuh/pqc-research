# Verification Decision Boundary Transition Matrix

| Security Level | Injected Predicate Fault | Input State | Observed Output State | Rate (95% CI) | Security Implication |
|:---|:---|:---:|:---:|:---:|:---|
| ML-DSA-44 | `Control (No-Fault)` | **VALID** | **ACCEPT** | 100.00% [99.62, 100.00] | Nominal valid signature acceptance. |
| ML-DSA-44 | `Tampered Sig Control` | **INVALID** | **REJECT** | 100.00% [99.62, 100.00] | Nominal invalid signature rejection. |
| ML-DSA-44 | `Forced Reject Gate` | **VALID** | **REJECT** | 100.00% [99.62, 100.00] | Denial of service; valid transaction rejected. |
| ML-DSA-44 | `Forced Accept Gate` | **INVALID** | **ACCEPT** | 100.00% [99.62, 100.00] | CRITICAL: Signature forgery bypass; attacker accepts forged payload. |
| ML-DSA-65 | `Control (No-Fault)` | **VALID** | **ACCEPT** | 100.00% [99.62, 100.00] | Nominal valid signature acceptance. |
| ML-DSA-65 | `Tampered Sig Control` | **INVALID** | **REJECT** | 100.00% [99.62, 100.00] | Nominal invalid signature rejection. |
| ML-DSA-65 | `Forced Reject Gate` | **VALID** | **REJECT** | 100.00% [99.62, 100.00] | Denial of service; valid transaction rejected. |
| ML-DSA-65 | `Forced Accept Gate` | **INVALID** | **ACCEPT** | 100.00% [99.62, 100.00] | CRITICAL: Signature forgery bypass; attacker accepts forged payload. |
| ML-DSA-87 | `Control (No-Fault)` | **VALID** | **ACCEPT** | 100.00% [99.62, 100.00] | Nominal valid signature acceptance. |
| ML-DSA-87 | `Tampered Sig Control` | **INVALID** | **REJECT** | 100.00% [99.62, 100.00] | Nominal invalid signature rejection. |
| ML-DSA-87 | `Forced Reject Gate` | **VALID** | **REJECT** | 100.00% [99.62, 100.00] | Denial of service; valid transaction rejected. |
| ML-DSA-87 | `Forced Accept Gate` | **INVALID** | **ACCEPT** | 100.00% [99.62, 100.00] | CRITICAL: Signature forgery bypass; attacker accepts forged payload. |
