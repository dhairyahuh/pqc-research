# ASTRA-Sec: DTN & Space Network Transport Audit Report

**Auditor:** Independent Space Communications & Network Protocol Reviewer  
**Standards Under Review:** RFC 9171 (Bundle Protocol v7), RFC 9172 (BPSec), RFC 8949 (CBOR)  
**Evaluated Implementations:** NASA/JPL ION-DTN v4.1.2 configuration vs. ASTRA-Sec Python BPv7 Engine

---

## 1. NASA/JPL ION-DTN Integration Status (Critical Audit Finding)

A central objective of this audit was to determine whether ASTRA-Sec executes against a running NASA/JPL ION-DTN C daemon on the host or uses an internal protocol engine.

### Verification of System Binaries:
```bash
which ionadmin  # Output: ionadmin not found
which bpadmin   # Output: bpadmin not found
```

### Technical Distinction:
1. **ION Configuration Exporter (`astra_sec/dtn/ion_config.py`, `contact_plan.py`)**:
   - The codebase includes automated configuration generators for official NASA/JPL ION-DTN deployments.
   - It outputs valid `.ionconfig`, `.ionrc`, `.bprc`, and `.ionsecrc` files conforming to the 4-node topology (`ipn:1.1`, `ipn:2.1`, `ipn:3.1`, `ipn:4.1`).
   - It exports standardized ION contact plans (`IonContactPlan.to_ion_contact_plan()`) specifying scheduled contact windows and transmission data rates (e.g., 100,000 bytes/sec).
2. **Operational Transport Engine (`astra_sec/dtn/bpv7.py`, `bpsec.py`, `adapter.py`)**:
   - Because native ION C daemons require Linux POSIX shared-memory IPC (`/dev/shm`) and are not pre-installed on the evaluation host, ASTRA-Sec provides a **native pure-Python RFC 9171 (BPv7) implementation**.
   - All multi-hop DTN experiments, store-carry-forward simulations, and adversarial network disruption trials run through this pure-Python BPv7 engine backed by SQLite WAL persistent spools.

> [!IMPORTANT]
> ASTRA-Sec is not currently communicating via UNIX IPC with a running `ionadmin` process. All DTN functionality is executed through ASTRA-Sec's internal RFC 9171/RFC 9172 implementation. Research reports and manuscripts must strictly state this distinction.

---

## 2. RFC 9171 Bundle Protocol v7 (BPv7) Implementation

The internal BPv7 implementation in `astra_sec/dtn/bpv7.py` was inspected against RFC 9171 specifications:

| BPv7 Component | Specification | ASTRA-Sec Implementation | Status |
| :--- | :--- | :--- | :--- |
| **Primary Block** | Version 7, Bundle Processing Control Flags, CRC type | Canonical CBOR array encoding primary fields. | **VERIFIED** |
| **Endpoint IDs (EID)** | RFC 9171 DTN URI scheme (`dtn://...`) or IPN scheme (`ipn:...`) | Fully supported and validated via `validate_dtn_eid()`. | **VERIFIED** |
| **Creation Timestamp** | DTN epoch (milliseconds since 2000-01-01 00:00:00 UTC) | `unix_to_dtn_epoch()` and `dtn_epoch_to_unix()` conversion. | **VERIFIED** |
| **Lifetime** | Milliseconds from creation timestamp | Monotonically enforced; expired bundles pruned. | **VERIFIED** |
| **Payload Block** | Block Type 1, Block Number 1, raw payload | Holds opaque binary L2 envelope (`PqcMessageEnvelope.to_binary()`). | **VERIFIED** |
| **Wire Encoding** | RFC 8949 Concise Binary Object Representation (CBOR) | Canonical indefinite/definite wire framing via `cbor2`. | **VERIFIED** |

---

## 3. RFC 9172 BPSec Integration (Block Integrity Block)

BPSec support is implemented in `astra_sec/dtn/bpsec.py`:
- **Security Context ID:** RFC 9172 Context 1 (BIB-HMAC-SHA256).
- **Protected Target:** Canonical Block Number 1 (the Payload Block).
- **Tamper Resistance:** Modifying a single byte of the payload block causes `BpSecSecurityContext.verify_bib()` to reject the bundle before forwarding or delivery (`test_bpv7_cbor.py:test_bpsec_bib_integrity_and_tampering`).

### Preservation of Application End-to-End Encryption
The audit confirmed strict isolation between L5 BPSec and L2 application encryption:
1. BPSec BIB integrity operates hop-by-hop or relay-to-relay at L5 to prevent network injection.
2. Even if BPSec is stripped or bypassed, the payload inside Block 1 remains fully encrypted under AES-256-GCM and signed under ML-DSA-65. Relays can neither inspect nor forge the inner message.

---

## 4. Disruption & Persistence Management (L6)

1. **Persistent Message Spool (`astra_sec/network/spool.py`)**:
   - Implemented using SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL`).
   - Survives unexpected process crash or restart (`test_multinode_satellite.py:test_02_relay_restart_with_persistent_spool`).
2. **Contact Scheduling & Manual Overrides**:
   - `ContactSchedule` dynamically computes link availability based on simulated orbital time windows.
   - Supports manual link overrides (`LinkState.UP`, `LinkState.DOWN`, `LinkState.OCCULTED`) for testing link blackouts.
   - Bundles arriving during link occultation are marked `WAITING_CONTACT` and flushed in FIFO order upon reconnection.
