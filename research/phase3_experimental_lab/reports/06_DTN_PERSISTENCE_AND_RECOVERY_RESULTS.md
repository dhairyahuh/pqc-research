# ASTRA-Sec Phase 3: DTN Persistence and Disruption Recovery Results

## 1. Storage & Persistence Architecture

The DTN layer (Layer 5/6) of ASTRA-Sec enforces persistent storage-backed disruption tolerance. Intermediate satellite relays (`SAT1` and `SAT2`) do not decrypt application payloads; instead, they inspect the RFC 9171 BPv7 routing metadata, verify relay authentication, and spool bundles into persistent SQLite databases configured with Write-Ahead Logging (WAL) and `PRAGMA synchronous = FULL`.

This section reports the empirical persistence, storage overhead, and recovery measurements obtained during laboratory execution.

---

## 2. Spool Storage & Growth Under Load

During message transmission, the laboratory monitors real-time disk growth in the persistent spool directory.

| Scenario | Messages Dispatched | Payload / Msg | Total Ingested | Spool Initial Disk | Spool Final Disk | Spool Growth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EXP-PILOT-01` | 5 | 512 B | 25,595 B wire | 65,536 B | 147,456 B | +81,920 B |
| `EXP-A01-CONVENTIONAL` | 10 | 512 B | 51,190 B wire | 65,536 B | 212,992 B | +147,456 B |
| `EXP-B01-UNMONITORED` | 10 | 512 B | 51,190 B wire | 65,536 B | 212,992 B | +147,456 B |
| `EXP-D01-FULL-ASTRA` | 10 | 512 B | 51,190 B wire | 65,536 B | 212,992 B | +147,456 B |
| `EXP-E01-PAYLOAD-4KB` | 10 | 4,096 B | 87,030 B wire | 65,536 B | 249,856 B | +184,320 B |

### Storage Characteristics
- **WAL Page Allocation**: SQLite WAL pages are allocated in standard 4 KB OS blocks. Storage growth occurs monotonically as bundles are spooled and transitions are logged.
- **Transactional Atomicity**: Every bundle spool operation executes inside an explicit database transaction with checkpointing.
- **Wire-to-Storage Ratio**: For a 512 B application payload, the wire bundle size is 5,119 B (due to post-quantum key encapsulation material and signature overhead), resulting in ~14.7 KB of SQLite page allocation per message (inclusive of index B-trees, WAL headers, and uncompacted rollback journals).

---

## 3. Disruption Recovery Under Link Occultation

In addition to steady-state spooling, the Phase 2 and Phase 3 verification suites tested link occultation scenarios where the link between `SAT1` and `SAT2` was marked `LinkState.DOWN`.
1. **In-Flight Hold**: When the inter-satellite link dropped, `SAT1` safely held bundles in its persistent spool table without dropping them or rejecting the sender.
2. **Contact Schedule Resumption**: Upon transition back to `LinkState.UP`, calling `process_spool()` drained the pending queue in strict FIFO sequence order, delivering all spooled bundles to `SAT2` and subsequently `GSB`.
3. **No Duplicate Ingestion**: Anti-replay tracking across restarts verified that already-delivered bundle IDs are recognized and ignored upon re-connection.
