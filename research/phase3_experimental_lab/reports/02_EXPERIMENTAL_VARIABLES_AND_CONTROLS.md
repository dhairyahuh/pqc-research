# ASTRA-Sec Phase 3: Experimental Variables and Scientific Controls

## 1. Overview

To ensure academic rigor, valid causal inference, and strict reproducibility, the Phase 3 Experimental Laboratory formalizes all experimental variables into independent, dependent, and controlled categories, establishing an explicit control matrix across all campaigns.

---

## 2. Experimental Variable Classification

### 2.1. Independent Variables (Manipulated Factors)
1. **Cryptographic Configuration ($C$)**:
   - `BASELINE_A_NON_PQC`: AES-256-GCM + HMAC-SHA256 (pre-quantum control).
   - `BASELINE_B_UNMONITORED_PQC`: Unmonitored LibOQS ML-KEM-768 + ML-DSA-65.
   - `FULL_ASTRA_SEC`: Dual-transform monitored C ML-KEM-768 + LibOQS ML-DSA-65 + CBOR BPv7 DTN bundle encapsulation + ML-DSA-65 ACK.
2. **Payload Size ($S_p$)**:
   - 64 B (telemetry ping), 512 B (standard command/telemetry ADU), 4,096 B (sensor block), 65,536 B (dense payload).
3. **Channel Quality Impairments ($I$)**:
   - Propagation Delay ($\tau_d$): 0 ms to 500 ms (LEO to GEO relay links).
   - Jitter ($\sigma_\tau$): 0 ms to 50 ms.
   - Packet Loss Rate ($P_{loss}$): 0% to 25%.
   - Outage Duration ($T_{out}$): 0 s to 60 s.
4. **Fault Perturbations ($F$)**:
   - Fault Type: Transient single-event upset (SEU), stuck register bit, twiddle factor ROM corruption.
   - Fault Location: Forward NTT butterfly, Inverse NTT butterfly, wire ciphertext, signature block.
   - Fault Rate: $P_{inj} \in [0.0, 1.0]$.
5. **Concurrency Level ($M$)**:
   - Single-threaded sequential ($M=1$) vs. multi-threaded thread pool ($M=4$).

---

### 2.2. Dependent Variables (Measured Responses)
1. **End-to-End Latency ($T_{e2e}$)**: Elapsed time from initial application transmission call at GSA to verified receipt of ML-DSA-65 signed ACK at GSA ($\mu$s).
2. **Sub-Component Latencies**:
   - $t_{origin}$: GSA encapsulation, signing, and AEAD encryption latency ($\mu$s).
   - $t_{cbor}$: CBOR serialization and header generation latency ($\mu$s).
   - $t_{relay}$: Total transit time across intermediate relay nodes ($\mu$s).
   - $t_{dest}$: GSB verification, decapsulation, and AEAD decryption latency ($\mu$s).
   - $t_{ack}$: Return path ACK transit and verification latency ($\mu$s).
3. **Delivery Success Ratio ($R_{del}$)**: Percentage of dispatched messages successfully delivered and verified at destination without integrity or replay violation.
4. **Wire Overhead ($O_{wire}$)**: Total wire bundle bytes divided by application payload bytes ($B_{wire} / B_{payload}$).
5. **System Resource Utilization**:
   - Mean CPU consumption (% core).
   - Peak Resident Set Size (RSS in MB).
   - Persistent spool storage growth on disk (bytes).
6. **Fault Resilience Metrics**:
   - Fault Detection Rate ($D_r$): Fraction of injected faults detected by invariant monitoring or cryptographic verification.
   - Recovery Success Rate ($R_r$): Fraction of detected faults recovered within retry budget $K \le 2$.
   - Silent Data Corruption Rate ($SDC$): Fraction of corrupted messages accepted as valid plaintexts (target: $SDC = 0$).

---

### 2.3. Controlled Variables (Kept Constant)
1. **Network Topology**: 4-node linear store-and-forward topology:
   $$\text{GSA} \ (\text{dtn://gsa/app}) \longrightarrow \text{SAT1} \ (\text{dtn://sat1/relay}) \longrightarrow \text{SAT2} \ (\text{dtn://sat2/relay}) \longrightarrow \text{GSB} \ (\text{dtn://gsb/app})$$
2. **Cryptographic Parameter Sets**:
   - ML-KEM parameter set: $k=3$ (ML-KEM-768, FIPS 203, $q=3329$).
   - ML-DSA parameter set: $k=6, \ell=5$ (ML-DSA-65, FIPS 204, $q=8380417$).
   - Symmetric cipher: AES-256-GCM with 96-bit nonces and 128-bit authentication tag.
3. **DTN Protocol Standards**:
   - Bundle Protocol version 7 (RFC 9171).
   - Canonical CBOR deterministic encoding.
4. **Execution Environment**:
   - Same physical CPU hardware, OS Darwin arm64 kernel, Python 3.9 runtime.
   - Dedicated isolated temporary spool directories cleaned before and after each run.

---

## 3. Control Matrix Across Experimental Groups

| Group | Scenario ID | Cryptographic Adapter | Payload | Channel Impairment | Fault Injection | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | `EXP-A01-CONVENTIONAL` | Baseline A (AES + HMAC) | 512 B | Clean ($\tau_d=0, P_l=0$) | None | Pre-quantum reference |
| **B** | `EXP-B01-UNMONITORED` | Baseline B (LibOQS PQC) | 512 B | Clean ($\tau_d=0, P_l=0$) | None | Unmonitored PQC reference |
| **D** | `EXP-D01-FULL-ASTRA` | Full ASTRA-Sec (Monitored C) | 512 B | Clean ($\tau_d=0, P_l=0$) | None | Primary treatment evaluation |
| **E** | `EXP-E01-PAYLOAD-4KB` | Full ASTRA-Sec | 4,096 B | Clean ($\tau_d=0, P_l=0$) | None | Payload scaling impact |
| **F** | `EXP-F01-CONCURRENCY-4` | Full ASTRA-Sec | 512 B | Clean | None ($M=4$ threads) | Multi-threading stress |
| **G** | `EXP-G01-IMPAIRMENT` | Full ASTRA-Sec | 512 B | $\tau_d=50\text{ms}, \sigma=5, P_l=0.1$ | None | Disruption tolerance |
| **J** | `EXP-J01-FAULT-SEU` | Full ASTRA-Sec | 512 B | Clean | SEU transient bit flip ($P_{inj}=1.0$) | SDC suppression & containment |
