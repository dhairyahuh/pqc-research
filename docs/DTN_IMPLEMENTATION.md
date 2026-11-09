# ASTRA-Sec: Delay-Tolerant Networking (DTN) Implementation Specification

This document details the Bundle Protocol v7 (BPv7) wire encoding, RFC 9172 BPSec integration, persistent SQLite WAL custody storage, and disruption recovery architecture in ASTRA-Sec.

---

## 1. Bundle Protocol v7 (RFC 9171) & BPSec (RFC 9172)

ASTRA-Sec implements RFC 9171 Bundle Protocol Version 7 wire framing formatted in Concise Binary Object Representation (CBOR).

```
+-----------------------------------------------------------------------------------+
|                        RFC 9171 PRIMARY BUNDLE BLOCK                              |
+-----------------------------------------------------------------------------------+
|  [0] Version: 7                                                                   |
|  [1] Bundle Processing Control Flags:                                             |
|        - BUNDLE_IS_USER_DATA (0x0001)                                             |
|        - BUNDLE_REQUIRES_STORAGE_ACKNOWLEDGEMENT (0x0040)                          |
|        - BUNDLE_CUSTODY_TRANSFER_REQUESTED (0x0080)                               |
|  [2] CRC Type: CRC32 (NIST/IEEE standard)                                         |
|  [3] Destination EID: dtn://gsb/app                                               |
|  [4] Source EID: dtn://gsa/app                                                    |
|  [5] Report-To EID: dtn://gsa/app                                                 |
|  [6] Creation Timestamp: [DTN Epoch Milliseconds, Monotonic Sequence ID]          |
|  [7] Lifetime: 86400 seconds (24 Hours)                                           |
+-----------------------------------------------------------------------------------+
|              BPSec BLOCK INTEGRITY BLOCK (BIB - RFC 9172)                         |
+-----------------------------------------------------------------------------------+
|  [0] Block Type Code: 11 (BPSec BIB)                                              |
|  [1] Block Number: 2 | Block Flags: 0                                             |
|  [2] Security Target: Block Number 1 (Payload Block)                              |
|  [3] Security Context Identifier: 204 (NIST FIPS 204 ML-DSA-65)                   |
|  [4] Security Result: 3,309 bytes signature over canonical wire bundle            |
+-----------------------------------------------------------------------------------+
|                        PAYLOAD BLOCK (Block Number 1)                             |
+-----------------------------------------------------------------------------------+
|  [0] Block Type Code: 1 (Payload Block)                                           |
|  [1] Block Number: 1 | Block Flags: 0                                             |
|  [2] Encapsulated PqcMessageEnvelope:                                             |
|        - ML-KEM-768 Ciphertext: 1,088 bytes                                       |
|        - AES-256-GCM Nonce: 12 bytes                                              |
|        - AEAD Encrypted ADU Payload: N bytes                                      |
|        - AES-256-GCM Tag: 16 bytes                                                |
+-----------------------------------------------------------------------------------+
```

---

## 2. Persistent Transactional Storage (SQLite Write-Ahead Logging)

Space relays (SAT-1 and SAT-2) store bundles in persistent SQLite databases located at `$ASTRA_SPOOL_DIR` (e.g., `/tmp/astra_sec/spool/sat1.db`).

### Database Schema:
```sql
CREATE TABLE IF NOT EXISTS bundle_spool (
    bundle_id TEXT PRIMARY KEY,
    source_eid TEXT NOT NULL,
    destination_eid TEXT NOT NULL,
    sequence_id INTEGER NOT NULL,
    created_timestamp REAL NOT NULL,
    expiry_timestamp REAL NOT NULL,
    payload_blob BLOB NOT NULL,
    wire_size_bytes INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('QUEUED', 'FORWARDED', 'EXPIRED')),
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_spool_status ON bundle_spool(status);
CREATE INDEX IF NOT EXISTS idx_spool_dest ON bundle_spool(destination_eid);
```

### ACID Storage Pragma Configurations:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA busy_timeout = 5000;
```
- **Crash Resilience**: If a spacecraft power reset occurs during an inter-satellite link outage, the WAL journal ensures zero database corruption and zero bundle loss upon reboot.

---

## 3. Disruption Handling & Custody Recovery Flow

1. **Nominal State**: Bundles arriving at SAT-1 are routed immediately to SAT-2 and transmitted over the inter-satellite crosslink (ISL).
2. **Disrupted State (ISL Severed)**:
   - When a link outage is detected (e.g., line-of-sight occultation), the next-hop router queues the bundle into `bundle_spool` with status `QUEUED`.
   - SAT-1 retains custody of the bundle in non-volatile storage.
3. **Contact Window Restoration**:
   - The link monitor detects ISL restoration.
   - SAT-1 executes a transactional flush query (`SELECT * FROM bundle_spool WHERE status='QUEUED' ORDER BY sequence_id ASC`).
   - Bundles are forwarded sequentially to SAT-2.
   - Upon successful receipt, status updates to `FORWARDED`.

---

## 4. Replay Attack & Out-of-Order Delivery Protection

Destination Ground Station Bravo (GSB) maintains an ACID anti-replay sequence log:
```sql
CREATE TABLE IF NOT EXISTS processed_sequences (
    source_eid TEXT NOT NULL,
    sequence_id INTEGER NOT NULL,
    processed_at REAL NOT NULL,
    PRIMARY KEY(source_eid, sequence_id)
);
```
- When a bundle arrives at GSB, its sequence ID is checked against `processed_sequences`.
- If already present, the bundle is immediately rejected as a replayed message (`ReplayDetectedError`), generating a security audit telemetry event without triggering cryptographic decapsulation.
- Out-of-order bundles with valid unrecorded sequence IDs within the lifetime window ($t < t_{\text{expiry}}$) are accepted, processed, and acknowledged.
