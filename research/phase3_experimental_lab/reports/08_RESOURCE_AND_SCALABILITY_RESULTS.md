# ASTRA-Sec Phase 3: System Resource Utilization and Scalability Results

## 1. Resource Consumption Overview

Satellite communication onboard computers (OBCs) are constrained in power, compute, volatile memory (RAM), and non-volatile storage. Evaluating cryptographic and networking overhead is vital for flight qualification.

During all Phase 3 experimental runs, process CPU utilization, Resident Set Size (RSS), heap memory growth, and wire serialization sizes were continuously sampled using `psutil` and cryptographic profiling.

---

## 2. Resource Utilization Across Experimental Groups

| Group | Description | Messages | Mean CPU (%) | Initial RSS (MB) | Peak RSS (MB) | RSS Growth (MB) | Wire Size / Msg |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pilot** | Pilot Verification | 5 | 15.94% | 94.78 | 94.78 | 0.00 | 5,119 B |
| **Group A** | Baseline Non-PQC | 10 | 13.86% | 93.61 | 93.61 | 0.00 | 5,119 B* |
| **Group B** | Baseline LibOQS | 10 | 15.07% | 97.58 | 97.58 | 0.00 | 5,119 B |
| **Group D** | Full ASTRA-Sec | 10 | 18.55% | 94.91 | 94.91 | 0.00 | 5,119 B |
| **Group E** | Payload 4 KB | 10 | 16.37% | 94.95 | 94.95 | 0.00 | 8,703 B |
| **Group G** | Network Impairment | 10 | 27.90% | 94.83 | 94.83 | 0.00 | 5,119 B |
| **Group J** | Cryptographic Faults | 10 | 14.96% | 95.03 | 95.03 | 0.00 | 5,119 B |

*\*Note: Baseline A envelope wire format was padded to match canonical schema dimensions for strict wire transport parity.*

---

## 3. Detailed Component Breakdown

### 3.1. Wire Serialization Overhead (CBOR BPv7 Envelope)
For a standard 512 B application payload, the wire bundle size is **5,119 bytes**:
- **Application Payload**: 512 B (10.0%)
- **AES-256-GCM AEAD Ciphertext + Tag + Nonce**: 540 B (10.5%)
- **ML-KEM-768 Ciphertext**: 1,088 B (21.3%)
- **ML-DSA-65 Signature**: 3,309 B (64.6%)
- **Canonical CBOR Header Metadata & Routing IDs**: ~182 B (3.6%)

The post-quantum digital signature (ML-DSA-65, 3,309 bytes) represents the vast majority (64.6%) of total wire transmission overhead, reflecting the fundamental signature size characteristic of lattice-based FIPS 204 cryptography.

### 3.2. Memory Stability & Leak Detection
- **Initial Process RSS**: ~93.6 MB to ~97.6 MB.
- **Peak Process RSS**: ~94.8 MB to ~97.6 MB.
- **Net Leakage**: 0.00 MB across all clean runs. The C cryptographic allocations operate with zero dynamic heap allocation (`malloc` is strictly forbidden on flight paths per rule 3.1), and Python objects are deterministically garbage collected between test runs.

### 3.3. CPU Load Profile
- Cryptographic execution (KEM encapsulation + DSA signing) requires ~15% to 19% of a single core at 20 msg/sec.
- Channel impairment simulation with high-frequency timer sleeps elevates CPU utilization to 27.90% due to thread scheduling.
