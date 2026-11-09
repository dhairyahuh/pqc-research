# TFIB Implementation (Twiddle Factor Integrity Binding)

This directory contains the core C99 source implementation and static library for TFIB (Twiddle Factor Integrity Binding) v2.

## File Manifest
- [`tfib_ref.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.h): Primary API header declaring `tfib_assert_integrity()` and `tfib_restore_from_gold()`.
- [`tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c): Canonical reference implementation of lightweight table verification and golden restoration.
- [`tfib_core.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_core.h) & [`tfib_core.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_core.c): Core cryptographic digest calculator and state machine.
- [`tfib_common.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_common.h): Common types, status codes, and constants.
- [`tfib_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_hooks.c): Instrumentation hooks for research campaign tracking.
- [`libtfib.a`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/libtfib.a): Precompiled static library.

## Performance & Operational Characteristics
- **Integrity Check Latency:** $\approx 0.015\ \mu\text{s}$ per pre-assertion.
- **Self-Healing Latency:** $< 0.1\ \mu\text{s}$ via microsecond block copy from ROM.
- **Overall Decapsulation Overhead:** $+2.08\%$ relative to unhardened baseline ML-KEM-768.
- **Fault Detection Rate:** $100\%$ across all single-bit and double-bit SEU faults in `zetas`.

