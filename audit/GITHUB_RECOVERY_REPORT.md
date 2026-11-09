# ASTRA-Sec: Git Repository, Provenance & Reproducibility Audit Report

**Auditor:** Independent Configuration Management & Git Auditor  
**Date:** November 9, 2026  
**Repository Branch:** `astra-sec`  
**Current Head Commit:** `4f2ed009ae4ed2c1e08fa86bb7097212c2fab781`

---

## 1. Commit History & Milestone Provenance

Every major phase and milestone of ASTRA-Sec has a distinct, conventional commit preserving complete provenance:

| Commit Hash | Author | Date | Subject / Milestone |
| :--- | :--- | :--- | :--- |
| `4f2ed00` | Dhairya Jain | 2026-11-09 18:28 | `feat(dashboard): add ASTRA-Sec research monitoring dashboard` |
| `d46d5d0` | Dhairya Jain | 2026-11-09 18:15 | `paper(research): add ASTRA-Sec manuscript and reproducibility package` |
| `93d7901` | Dhairya Jain | 2026-11-09 18:03 | `experiment(benchmarks): add comparative performance evaluation` |
| `bf174de` | Dhairya Jain | 2026-11-09 17:49 | `experiment(security): add reproducible cross-layer fault campaigns` |
| `2cac90f` | Dhairya Jain | 2026-11-09 17:34 | `feat(security): implement authorization and replay-safe delivery` |
| `fc44101` | Dhairya Jain | 2026-11-09 17:24 | `feat(dtn): integrate BPv7, BPSec and disruption store-and-forward` |
| `7bf83ad` | Dhairya Jain | 2026-11-09 17:15 | `feat(network): implement 4-node satellite store-and-forward topology` |
| `8be558c` | Dhairya Jain | 2026-11-09 16:45 | `feat(crypto): integrate native fault-monitored ML-KEM-768 with TFIB-Ref` |
| `85799a4` | Dhairya Jain | 2026-11-09 16:41 | `feat(crypto): implement post-quantum end-to-end messaging pipeline` |
| `9dc872d` | Dhairya Jain | 2026-11-09 16:29 | `feat(scaffold): initialize ASTRA-Sec 7-layer architecture foundation` |
| `8b2382d` | Dhairya Jain | 2026-11-09 16:04 | `checkpoint: preserve PQC NTT fault resilience research` |

---

## 2. Branch Topology & Preservation

The repository maintains explicit branch isolation to ensure original research is never overwritten:
1. `archive/pqc-ntt-fault-resilience` (at `8b2382d`): Permanent read-only archive of the pre-ASTRA-Sec research state.
2. `space-resilience-framework` (at `b39a18a`): Historical integration branch preserving pre-existing experimental improvements.
3. `main` (at `8b2382d`): Upstream base repository.
4. `astra-sec` (HEAD): Active development branch housing the complete 7-layer ASTRA-Sec architecture.

---

## 3. Remote Tracking & Hygiene

- **Configured Remote:**
  ```
  origin https://github.com/dhairyahuh/pqc-research.git (fetch)
  origin https://github.com/dhairyahuh/pqc-research.git (push)
  ```
- **Untracked Files Inspection:**
  Untracked items in the workspace (`CONTRIBUTING.md`, `PROJECT_OVERVIEW.md`, `docs/`, `paper/`, `presentation/`, etc.) consist solely of documentation, presentation handbooks, and directory manifests created during roadmap planning. No sensitive, broken, or rogue files exist.
- **Accidental Binaries Check:**
  All pre-compiled binaries and object files reside strictly within `.gitignore` directories (`bin/`, `bin/obj/`, `*.dylib`, `*.so`, `*.o`, `*.a`). No binary blobs have been committed to git tracking in `astra-sec`.
- **Secret Audit:**
  Zero private keys (`BEGIN PRIVATE KEY`), credentials, operational tokens, or API secrets exist in the git history or working tree.

---

## 4. Recovery & Demonstration Guidelines

1. **Clean Workspace Clone**:
   ```bash
   git clone -b astra-sec https://github.com/dhairyahuh/pqc-research.git
   cd pqc-research
   make setup-dev
   make all
   make test
   ```
2. **Branch Reset Protection**:
   Under no circumstances should `git rebase`, `git reset --hard`, or force-push (`git push -f`) be executed on `astra-sec` or `archive/pqc-ntt-fault-resilience`.
