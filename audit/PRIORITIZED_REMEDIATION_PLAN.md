# ASTRA-Sec: Prioritized Remediation Plan

This remediation plan categorizes all technical findings, structural gaps, and potential improvements identified during the independent technical audit.

**Policy Note:** In accordance with audit instructions, no P0 or P1 architectural modifications have been applied during this read-only audit. All items are cataloged below for project owner review and prioritization.

---

## 1. Prioritization Framework
- **P0 (Critical):** Security vulnerability, silent data corruption, false success reporting, or broken core workflow.
- **P1 (High):** Major architectural limitation, external daemon integration gap, or missing protocol layer.
- **P2 (Medium):** Reproducibility enhancements, extended stress testing, or documentation gaps.
- **P3 (Low):** UI polish, non-critical telemetry metrics, or cosmetic enhancements.

---

## 2. Issues & Remediation Catalog

### Priority P0: Critical Vulnerabilities & Core Failures
> **Status:** **NONE DETECTED.**  
> The core 4-node communication flow, cryptographic decapsulation, AEAD encryption, FDIR fault containment, and adversarial protections are 100% functional and pass all automated tests.

---

### Priority P1: High-Priority Architectural Enhancements

#### Issue P1-01: Native NASA/JPL ION-DTN C Daemon Runtime Integration
- **Description:** ASTRA-Sec currently relies on a native pure-Python RFC 9171 / RFC 9172 BPv7 engine. While it generates official ION configuration files (`.ionconfig`, `.ionrc`, `.bprc`, `.ionsecrc`), it does not execute against live `ionadmin`/`bpadmin` POSIX shared-memory daemons on macOS.
- **Evidence:** `which ionadmin` returns non-zero. System runs via `astra_sec/dtn/adapter.py`.
- **Impact:** Demonstrations on macOS showcase the pure-Python BPv7 engine rather than NASA's C reference implementation.
- **Files Affected:** `astra_sec/dtn/adapter.py`, `astra_sec/dtn/ion_config.py`.
- **Proposed Fix:** Provide a standardized Docker Compose configuration deploying official NASA/JPL ION-DTN 4.1.2 Linux containers, with a POSIX socket bridge connecting ASTRA-Sec L2 to ION's `bpsendfile` / `bprecvfile` utilities.
- **Tests Needed:** Cross-container bundle ingestion and extraction integration tests.
- **Estimated Effort:** 8–12 engineering hours.
- **Dependencies:** Docker Desktop / Linux container runtime.

#### Issue P1-02: Complete Per-Message Asymmetric Double Ratchet
- **Description:** ASTRA-Sec implements security continuity and forward/backward secrecy via periodic epoch keypair rotation (`GroundStationNode.rotate_node_keys()`). A full per-message Diffie-Hellman / KEM ratchet (Signal Double Ratchet protocol equivalent for PQC) is only partially integrated.
- **Evidence:** `tests/integration/test_security_continuity.py:test_06_key_rotation` tests epoch updates rather than per-bundle ephemeral public key exchanges.
- **Impact:** Fine-grained compromise recovery is bound to epoch synchronization windows rather than individual message receipts.
- **Files Affected:** `astra_sec/security/lifecycle.py`, `astra_sec/service/ground_station.py`.
- **Proposed Fix:** Incorporate an ephemeral KEM encapsulation header in every outbound bundle, ratcheting the root key upon valid reception and acknowledgment.
- **Tests Needed:** Out-of-order ratcheting tests and forward secrecy falsification tests.
- **Estimated Effort:** 10–14 engineering hours.
- **Dependencies:** None.

---

### Priority P2: Medium-Priority Reproducibility & Engineering Improvements

#### Issue P2-01: Automated CI LaTeX Manuscript PDF Compilation
- **Description:** `pdflatex` is not installed on standard macOS developer workstations, preventing headless compilation of `manuscript/main.tex` in local CI workflows.
- **Evidence:** `which pdflatex` returns not found. Manuscript validated via `validate_manuscript.py`.
- **Impact:** Evaluators must upload the manuscript folder to Overleaf or use Docker to view the compiled PDF.
- **Files Affected:** `.github/workflows/ci.yml`, `manuscript/Makefile`.
- **Proposed Fix:** Add a GitHub Actions job using `dante-ev/latex-action` or a lightweight TeX Live Docker container to compile `main.tex` to `ASTRA_Sec_Research_Manuscript.pdf` on every commit.
- **Tests Needed:** PDF artifact generation check in CI.
- **Estimated Effort:** 2–3 engineering hours.
- **Dependencies:** GitHub Actions runner.

#### Issue P2-02: Extended Soak & Stress Testing under Orbital Contact Plan
- **Description:** Current disruption tests evaluate scheduled contacts up to 300 seconds. Extended soak tests simulating multi-day interplanetary occultations (e.g., Mars conjunction) with millions of spooled bundles have not been evaluated.
- **Evidence:** Spool scalability tested up to $N=1000$ bundles.
- **Impact:** Long-term SQLite WAL performance under multi-gigabyte bundle spools remains uncharacterized.
- **Files Affected:** `tests/integration/test_dtn_disruption.py`, `astra_sec/network/spool.py`.
- **Proposed Fix:** Implement a parametric soak-testing script generating 50,000 spooled bundles and measuring retrieval latencies across database vacuum cycles.
- **Tests Needed:** Spool vacuum and WAL checkpoint stress tests.
- **Estimated Effort:** 4–6 engineering hours.
- **Dependencies:** Disk space (~5 GB).

---

### Priority P3: Low-Priority UI & Documentation Polish

#### Issue P3-01: Dashboard Telemetry Export & Log Filter Controls
- **Description:** The dashboard live audit stream displays the last 200 events but lacks a client-side button to export the audit ledger to CSV/JSON.
- **Evidence:** Inspection of `astra_sec/dashboard/static/index.html`.
- **Impact:** Users must manually copy logs from the browser console or query the REST endpoint directly.
- **Files Affected:** `astra_sec/dashboard/static/index.html`.
- **Proposed Fix:** Add an "Export Audit Log (JSON)" button in the audit stream card.
- **Tests Needed:** Frontend DOM click validation.
- **Estimated Effort:** 1 engineering hour.
- **Dependencies:** None.

#### Issue P3-02: Dark/Light Mode Theme Toggle
- **Description:** Dashboard is currently locked to space-mission dark mode (`#0b0f19`).
- **Evidence:** Hardcoded dark CSS classes in `index.html`.
- **Impact:** Visual preference only.
- **Files Affected:** `astra_sec/dashboard/static/index.html`.
- **Proposed Fix:** Add CSS variable theme toggling supporting high-contrast light mode for presentation projectors.
- **Tests Needed:** UI regression check.
- **Estimated Effort:** 1 engineering hour.
- **Dependencies:** None.
