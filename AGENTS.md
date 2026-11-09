# ASTRA-Sec: Agent and Contributor Engineering Guidelines

This document establishes the mandatory engineering standards, architectural rules, safety boundaries, and development protocols for any autonomous AI agent or human contributor working on the **ASTRA-Sec** codebase.

---

## 1. Permanent Research Identity

The overarching permanent research project title is:
**"Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems"**

The end-to-end mission-level protocol is:
**"ASTRA-Sec: Post-Quantum End-to-End Secure Messaging and Delay-Tolerant Cryptographic Resilience for Space Networks"**

The foundational low-level software case study is:
**"Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment"**

> [!IMPORTANT]
> Never rename or alter the permanent research title in papers, presentations, or top-level project documentation.

---

## 2. Architectural Invariants (7-Layer Model)

All implementations must conform to the 7-layer architecture specified in [`docs/architecture.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/architecture.md):

| Layer | Responsibility | Invariants & Constraints |
| :--- | :--- | :--- |
| **L1** | Application & Telemetry | Produces validated `ApplicationDataUnit` (ADU) objects. No direct network access. |
| **L2** | End-to-End Security | Envelope encryption (AES-256-GCM) with canonical AAD binding. Header cannot be modified in transit. |
| **L3** | Post-Quantum Services | Key agreement via ML-KEM-768; signatures via ML-DSA-65. Double Ratchet key evolution. |
| **L4** | Fault-Resilient Execution | Dual-transform NTT butterfly invariant checking ($r \equiv t\zeta \pmod q$), snapshot rollback ($K \le 2$), TFIB-Ref. |
| **L5** | DTN Transport | RFC 9171 Bundle Protocol v7, RFC 9172 BPSec, disruption tolerance. Relays inspect routing only, never decrypt L2 payload. |
| **L6** | Disruption Recovery | Persistent transactional spooling, bounded retry backoff, reordering resistance, epoch synchronization. |
| **L7** | FDIR & Audit | Real-time telemetry, SDC suppression verification, fail-stop escalation, ground-station audit logging. |

---

## 3. C Implementation Coding Standards

For all C components in `algorithms/` and `src/`:

1. **Zero Dynamic Allocation on Flight Path**:
   - `malloc()`, `calloc()`, `realloc()`, and `free()` are **strictly forbidden** in operational cryptographic pathways (NTT, polynomial multiplication, hashing, encapsulation, decapsulation, verification).
   - All buffers must be stack-allocated or statically bounded fixed-size buffers.
2. **Constant-Time Execution**:
   - Branching on secret key material or intermediate ciphertext coefficients is strictly prohibited.
   - Use constant-time conditional selections (e.g., bitwise multiplexing) instead of `if/else` on secret data.
3. **Bounded Loops**:
   - Every loop must have an explicit, compile-time demonstrable upper bound (no unbounded `while` loops).
4. **Fault Recovery Budget**:
   - Local rollback retry budget is strictly bounded: $K \le 2$. Upon second failure, the system must trigger fail-stop suppression (implicit rejection / random seed output).
5. **Standard Compliance**:
   - Target C99/C11 standards with `-Wall -Wextra -Werror` clean compilation.

---

## 4. Python Implementation Coding Standards

For all Python components in `astra_sec/` and `tests/`:

1. **Type Annotations**:
   - All function signatures, method parameters, and return types must be fully typed (`typing`, `Optional`, `List`, `Dict`, etc.).
2. **Schema & Configuration Validation**:
   - Use **Pydantic v2** (`BaseModel`, `Field`, `field_validator`) for all protocol envelopes, headers, configuration models, and telemetry records.
3. **Structured Logging**:
   - Use JSON-structured logging via `astra_sec.core.logging.configure_logging`.
   - Never log raw cryptographic keys, nonces, or unencrypted plaintext.
4. **Exception Handling**:
   - Raise explicit subclasses of `AstraError` (e.g., `ConfigurationError`, `SchemaValidationError`, `ProtocolError`, `ReplayDetectedError`).
5. **No Secrets in Code**:
   - No hardcoded private keys, shared secrets, or operational passwords. All credentials must load via environment variables or explicitly passed secure files.

---

## 5. Development & Verification Workflow

Agents must execute the standard verification pipeline before finalizing any task:

```bash
# 1. Run Python unit and integration test suites
make test-python

# 2. Run C Known Answer Tests and fault injection campaigns
make test-c

# 3. Comprehensive verification (both C & Python)
make test

# 4. Check system health
make health-check

# 5. Linting and static syntax checks
make lint
```

---

## 6. Git & Commit Guidelines

- **Branching**: All development for ASTRA-Sec occurs on branch `astra-sec`.
- **Commit Format**: Conventional Commits standard:
  - `feat(...)`: New feature or protocol layer
  - `fix(...)`: Bug fix or security patch
  - `test(...)`: Adding or updating test suites
  - `docs(...)`: Documentation or paper updates
  - `chore(...)`: Tooling, CI, dependencies, or scaffolding
- **Diff Hygiene**: Never commit unnecessary whitespace modifications or overwrite user-created experiment artifacts.
