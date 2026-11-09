# ASTRA-Sec Phase 3: Baseline and Treatment Definitions

## 1. Scope & Objective

To avoid misleading or artificially advantageous comparisons, this document rigorously defines each experimental baseline, the primary ASTRA-Sec treatment, and their comparability boundaries.

---

## 2. Detailed Specification of Baselines & Treatments

### 2.1. Baseline A: Conventional Pre-Quantum Control (`BASELINE_A_NON_PQC`)
* **Role**: Represents standard classical space mission telemetry encryption without post-quantum or hardware fault protections.
* **Primitives**:
  - Key Exchange / Derivation: Pre-shared key / HKDF-SHA256 (simulating conventional static key pairs).
  - Data Confidentiality & Integrity: AES-256-GCM.
  - Authentication / Integrity Signature: HMAC-SHA256.
  - Wire Format: To maintain strict transport comparability through the 7-layer pipeline, headers and envelopes conform to the canonical `PqcMessageEnvelope` schema (with HMAC and key parameters padded to canonical schema field widths: 1,088 B KEM / 3,309 B signature).
* **Fault Handling**: None. If a bit flip occurs in transit or memory, GCM authentication tag verification fails and drops the packet.

---

### 2.2. Baseline B: Standard Unmonitored Post-Quantum Control (`BASELINE_B_UNMONITORED_PQC`)
* **Role**: Represents modern post-quantum migration using standard open-source libraries (Open Quantum Safe / LibOQS) without hardware fault-tolerance or NTT invariant monitoring.
* **Primitives**:
  - Key Encapsulation: LibOQS `ML-KEM-768` (C reference implementation).
  - Digital Signatures: LibOQS `ML-DSA-65`.
  - Symmetric Encryption: AES-256-GCM envelope encryption.
  - DTN Transport: Full 4-node store-and-forward DTN pipeline with SQLite WAL persistent spooling.
* **Fault Handling**: Unprotected against internal computation faults. Bit flips during NTT computation or decapsulation result in SDC or implicit rejection without local recovery or fault telemetry.

---

### 2.3. Treatment: Full ASTRA-Sec Protocol (`FULL_ASTRA_SEC`)
* **Role**: The complete 7-layer resilient post-quantum security framework.
* **Primitives**:
  - Key Encapsulation: Native C `ML-KEM-768` with dual-transform NTT butterfly invariant verification ($r \equiv t\zeta \pmod q$) and bounded snapshot rollback ($K \le 2$).
  - Digital Signatures: `ML-DSA-65` binding canonical header metadata and AEAD ciphertext.
  - Symmetric Encryption: AES-256-GCM envelope encryption with canonical AAD binding.
  - DTN Transport: RFC 9171 BPv7 over 4 nodes with transactional WAL spooling and contact-schedule-aware routing.
  - End-to-End Delivery Assurance: Reverse-path `ML-DSA-65` signed delivery acknowledgments.
* **Fault Handling**: Active Layer 4 fault containment. Detects transient SEUs and persistent twiddle factor corruptions, performs localized register rollback up to $K=2$, and triggers deterministic fail-stop implicit rejection upon budget exhaustion.

---

## 3. Comparability Boundaries & Limitations

| Aspect | Baseline A | Baseline B | Full ASTRA-Sec | Comparability Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Transport Pipeline** | 4-node DTN (same) | 4-node DTN (same) | 4-node DTN (same) | **Identical**: All use same relay nodes, spooling, and forwarding logic. |
| **Wire Envelope** | Padded schema | Canonical schema | Canonical schema | **Equivalent**: Same byte length over wire ensures identical network transit overhead. |
| **KEM Algorithm** | Classical HMAC/AES | LibOQS ML-KEM-768 | Monitored ML-KEM-768 | **Direct comparison**: Directly isolates the cost of NTT monitoring. |
| **Fault Hooks** | None | None | C Layer 4 hooks | **Scientific isolate**: Faults injected at the C layer measure detection & containment efficacy. |
| **Execution Sandbox** | Python ctypes bridge | Python ctypes bridge | Python ctypes bridge | **Identical**: All cryptographic calls cross identical FFI boundaries. |
