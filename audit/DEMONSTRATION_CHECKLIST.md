# ASTRA-Sec: Live Demonstration Script & Verification Checklist

**Target Audience:** Research Supervisors, Thesis Examiners, Technical Evaluators, Colloquium Demonstrations  
**Estimated Run Time:** 5–10 minutes  
**Prerequisites:** Python 3.9+, Clang C compiler, `make`, Web Browser (Chrome, Firefox, Safari)

---

## 1. Quick Launch Summary

To run the complete automated technical test suite:
```bash
make test
```
To launch the interactive Mission Control Dashboard:
```bash
make dashboard
```
Access the dashboard at: **`http://localhost:8000`**

---

## 2. Step-by-Step Demonstration Script

### Scene 1: Baseline Verification & Health Diagnostic (Terminal)
**Action:** Run system diagnostic check.
```bash
make health-check
```
**Expected Output:**
```
=========================================================================
 ASTRA-Sec System Diagnostic Health Report — Version 0.1.0
=========================================================================
 Node EID:        dtn://gsa/app
 Node Role:       originator
 Overall Status:  OK
 Component Breakdown:
   [PASS] configuration      : PASS
   [PASS] storage            : PASS
   [PASS] c_crypto_engine    : PASS
=========================================================================
```
**Key Talking Point:** Confirms zero static allocation, clean runtime initialization, and active native C cryptographic engines.

---

### Scene 2: Interactive Web Dashboard & Network Topology
**Action:**
1. Start the dashboard:
   ```bash
   make dashboard
   ```
2. Open `http://localhost:8000` in your web browser.
3. Observe:
   - **Network Topology Graph:** Active line-of-sight connectivity between `GSA` $\to$ `SAT1` $\to$ `SAT2` $\to$ `GSB`.
   - **Node Telemetry Cards:** Real-time public key fingerprints for ML-KEM-768 and ML-DSA-65.
   - **FDIR Counters:** Total NTT butterflies executed (0 initial), transient recoveries (0), fail-stop state (`NORMAL`).

---

### Scene 3: Clean Multi-Hop Post-Quantum Message Dispatch
**Action:**
1. In the **Mission Control: Dispatch Command** panel on the dashboard:
   - Destination EID: `dtn://gsb/app`
   - Payload: `COMMENCE_ORBITAL_MANEUVER_BURN_VECTOR_99`
   - TTL: `300`
   - Transient Fault Simulation: **Disabled (Unchecked)**
2. Click **"Dispatch Encrypted Command"**.
3. Observe:
   - Green notification: *Envelope Dispatched & Delivered to GSB in ~1.5 ms*.
   - Live Audit Ledger records:
     1. `COMMAND_DISPATCHED`: Packaging canonical AAD + AES-256-GCM + ML-DSA-65 signature (3,309 B).
     2. `MESSAGE_FORWARDED`: SAT1 routes to SAT2 without decrypting payload.
     3. `MESSAGE_FORWARDED`: SAT2 routes to GSB.
     4. `MESSAGE_DELIVERED`: GSB verifies ML-DSA signature, decapsulates ML-KEM secret, checks AEAD tag, and returns signed ACK.
     5. `ACK_VERIFIED`: GSA cryptographic verifier validates GSB receipt signature.

---

### Scene 4: Space Radiation Fault Injection & Real-Time Recovery
**Action:**
1. In the **Mission Control: Dispatch Command** panel:
   - Payload: `RADIATION_SEU_TEST_SAMPLE_ALPHA`
   - Transient Fault Simulation: **Enabled (Checked)**
2. Click **"Dispatch Encrypted Command"**.
3. Observe:
   - Command delivers successfully to GSB with **zero data loss**.
   - **FDIR Telemetry Card Updates Instantly**:
     - *Transient Recoveries*: Increments from `0` $\to$ `1`.
     - *NTT Butterflies Monitored*: Increments by `9,856`.
     - *SDC Prevention*: `ACTIVE (100% Suppression)`.
   - Audit stream records `FAULT_DETECTED` followed by `TRANSIENT_FAULT_RECOVERED` via localized snapshot rollback ($K=1$).
**Key Talking Point:** Demonstrates the core research contribution: dual-transform NTT butterfly invariant monitoring detects radiation bit-flips mid-execution and restores valid state without retransmitting over the space channel.

---

### Scene 5: Orbital Disruption & Store-Carry-Forward Delivery
**Action:**
1. In the **Network Topology** panel, click **"Sever Inter-Satellite Link (ISL)"**.
2. Notice the link between SAT1 and SAT2 turns red (`DOWN`) and SAT1 status transitions to `INTERRUPTED`.
3. In the Dispatch panel, send command: `QUEUED_TELEMETRY_PACKET_DURING_BLACKOUT`.
4. Click **"Dispatch Encrypted Command"**.
5. Observe:
   - Message **does not fail**.
   - SAT1 Spool Depth increments to `1 pending bundle`.
   - Audit stream records `MESSAGE_SPOOLED_WAITING_CONTACT`.
6. Click **"Restore Inter-Satellite Link (ISL)"**.
7. Observe:
   - SAT1 flushes its SQLite WAL spool.
   - Message delivers to GSB, verified and decrypted.
   - SAT1 Spool Depth returns to `0`.
**Key Talking Point:** Proves RFC 9171 delay tolerance and persistent non-volatile spooling; communication continuity survives link occultation.

---

## 3. Demonstration Troubleshooting & FAQ

| Symptom / Question | Solution / Response |
| :--- | :--- |
| **Port 8000 already in use** | Run on alternate port: `python3 -m uvicorn astra_sec.dashboard.app:app --port 8080`. |
| **"Is this calling real post-quantum cryptography?"** | Yes. Inspect `tests/unit/test_crypto_adapters.py` or run `make test-c`. All operations execute standardized NIST FIPS 203 ML-KEM-768 and FIPS 204 ML-DSA-65. |
| **"Are the relays seeing the message text?"** | No. Relays inspect only `EnvelopeHeader` metadata (EIDs, TTL). Plaintext is encrypted under AES-256-GCM; tampering by a relay causes instant AEAD tag failure at destination. |
| **"Where are the empirical results stored?"** | In `data/benchmarks/benchmark_results.json` and `data/benchmarks/campaign_results.jsonl`. |

---

## 4. Teardown & Post-Demonstration Cleanup

To terminate background processes and clean temporary demonstration artifacts:
```bash
# 1. Stop web server (press Ctrl+C in dashboard terminal)

# 2. Clean temporary demonstration spool files
rm -f /tmp/audit_sat1.db /tmp/audit_sat2.db

# 3. Verify clean system health
make health-check
```
