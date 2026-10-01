# Post-Quantum Cryptography Research & Development Protocol

**Project Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Document Version:** 1.0.0-PROTOCOL  
**Date:** October 1, 2026  
**Status:** MANDATORY OPERATIONAL SPECIFICATION  

---

## 1. Core Engineering Principles

1. **Academic Discipline & Skepticism:**
   - Every claim must be tagged with explicit evidence levels: `VERIFIED FACT`, `FORMAL RESULT`, `EMPIRICAL RESULT`, `IMPLEMENTATION-SPECIFIC RESULT`, `SIMULATION-SPECIFIC RESULT`, `LITERATURE CLAIM`, `HYPOTHESIS`, or `FUTURE WORK`.
   - Never upgrade a hypothesis into a demonstrated result without empirical and mathematical proof.
   - Do NOT equate software-level bit flips with real physical ionizing radiation or Single Event Upsets (SEUs) without qualification.
2. **Implementation Integrity:**
   - Maintain strict separation between Path A (unmodified external oracle `liboqs`) and Path B (standalone C90 research implementations `mlkem-native` and `mldsa-native`).
   - All cryptographic source code must compile with zero warnings under `-Wall -Wextra -O3 -std=c99` (or `-std=c11`).
   - Every phase must maintain 100% bit-level reproducibility against the NIST Known Answer Tests (KAT) for all 6 parameter sets in `tests/test_fips_kats.c`.
3. **Traceability & Provenance:**
   - Source code commits must remain pinned in `docs/implementation-provenance.md`.
   - Every fault experiment must record deterministic PRNG seeds, iteration counts, and Wilson 95% confidence intervals in machine-readable JSON.

---

## 2. Research Git Protocol

Every future Antigravity research prompt in this project **MUST** adhere to the following workflow:

```
  [ START ]
      │
      ▼
  [ 1. Inspect Current Git State ]
      │  Run: git status, git branch --show-current, git log --oneline -10, git remote -v
      │  Verify repository is https://github.com/dhairyahuh/pqc-research
      │  Identify existing uncommitted changes; DO NOT overwrite unrelated user work
      ▼
  [ 2. Perform Requested Research/Engineering Work ]
      │  Implement only the approved phase scope; observe freezes where active
      ▼
  [ 3. Run Relevant Tests ]
      │  Execute baseline tests: make test, Python correctness suites, simulation harnesses
      │  Verify zero regressions and bit-level KAT reproducibility
      ▼
  [ 4. Audit Changed Files ]
      │  Inspect git diff, git diff --stat, git status --short
      │  Confirm no accidental or unauthorized source code modifications occurred
      ▼
  [ 5. Update Documentation / Results ]
      │  Update changelogs, research roadmaps, JSON experiment logs, and markdown reports
      ▼
  [ 6. Git Diff Review ]
      │  Review exact diffs to verify precision and quality
      ▼
  [ 7. Create a Focused Commit ]
      │  Stage ONLY files relevant to the completed phase: git add <specific files>
      │  Do NOT use indiscriminate 'git add .'
      │  Apply strict commit naming conventions
      ▼
  [ 8. Push to GitHub ]
      │  Push to remote tracking branch: git push origin <current-branch>
      ▼
  [ 9. Verify Remote Contains the Commit ]
      │  Run: git status, git log -1 --oneline, git show --stat --oneline HEAD, git ls-remote origin <current-branch>
      ▼
  [ 10. Report Commit Hash + Summary ]
      │  Report: commit hash, commit message, files changed, tests run, test results,
      │  known limitations, and next recommended phase
      ▼
  [ STOP ]
```

### Commit Naming Convention
Every commit must use structured conventional commits with the `research(phase-X)` prefix:

```
research(phase-X): <short description>
```

#### Approved Standard Examples:
- `research(phase-0): complete state-of-art audit`
- `research(phase-1): formalize ML-KEM fault propagation model`
- `research(phase-2): implement systematic ML-KEM fault campaign`
- `research(phase-3): add ML-DSA mid-operation fault instrumentation`
- `research(phase-4): correlate analytical and empirical fault propagation`
- `research(phase-5): add cross-implementation fault comparison`
- `research(phase-6): add formal fault contracts`
- `research(phase-7): implement selective resilience mechanisms`
- `research(phase-8): extend spacecraft protocol model`
- `research(phase-9): add comparative resilience evaluation`
- `research(phase-10): validate final research contributions`

#### Strictly Forbidden Commit Messages:
Do NOT use vague, uninformative commit messages such as:
- `update`
- `changes`
- `stuff`
- `final`
- `fix`
- `work`

### Safety & History Integrity Rules
- Do NOT rewrite Git history.
- Do NOT use destructive commands such as:
  - `git reset --hard`
  - `git push --force` (or `git push -f`)
  - Deleting active branches
  - Rebasing or amending published commits
  unless explicitly authorized by the project lead.
- Do NOT bundle unrelated future work into the current phase commit.
- If unrelated user work is present in the working tree, **preserve it, do not overwrite it, and report it clearly**.

---
*Protocol active and enforceable across all subsequent project phases.*
