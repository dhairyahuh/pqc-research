# Phase 14 — Persistent-Storage Fault Arm: Claim Boundaries

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Target:** Scientific Scope, Admissible Claims, and Inadmissible Claims for Future Phases  
**Standard:** Strict Epistemological Demarcation Between Software Fault Injection and Physical Radiation Physics

---

## 1. Executive Demarcation Principle

The persistent-storage fault arm evaluates how a specific post-quantum cryptographic software implementation (`mlkem-native` C reference on macOS arm64) responds when bytes in its operational mathematical constants table (`mlk_zetas`) are corrupted in memory across the decapsulation lifecycle.

**Under no circumstances does software memory mutation constitute or simulate physical radiation exposure.**

---

## 2. Definitive Claim Demarcation Matrix

| Research Dimension | Admissible Scientific Claims (What Future Data COULD Support) | Inadmissible Scientific Claims (What Future Data CANNOT Support) |
|:---|:---|:---|
| **Fault Nature** | • Software-level bit-flip injection into persistent virtual memory backing storage.<br>• Deterministic corruption of operational twiddle-factor constants. | • **NOT** physical Single-Event Upsets (SEU).<br>• **NOT** multi-cell upsets (MCU) in silicon storage cells.<br>• **NOT** cosmic ray, heavy ion, or proton strikes. |
| **Algorithmic Behavior** | • Sensitivity of ML-KEM-768 NTT butterfly operations to persistent parameter errors.<br>• Efficacy of the Fujisaki-Okamoto (FO) transform in rejecting ciphertexts when operational constants are corrupted across multiple stages.<br>• Empirical distinction between single-butterfly transient faults (TFIB) and persistent multi-stage table faults. | • **NOT** proof of cryptographic security against arbitrary fault attacks.<br>• **NOT** a general mathematical theorem covering all lattice-based schemes. |
| **System Scope** | • Behavioral characterization of the **modified research build** (`MLKEM_RESEARCH_RELOCATE_ZETAS`) executing on Apple Silicon under Darwin Mach-O virtual memory. | • **NOT** characterization of the unmodified upstream production binary (which resides immutably in `__TEXT`).<br>• **NOT** valid for other compilers, optimization levels, or CPU architectures without separate binary verification. |
| **Environmental Scope** | • Empirical software fault analysis in a desktop laboratory environment. | • **NOT** radiation resilience, radiation tolerance, or radiation hardening.<br>• **NOT** space qualification or flight readiness.<br>• **NOT** predictive of Low Earth Orbit (LEO) or Deep Space upset rates. |
| **Hardware Scope** | • Observable effects on macOS Mach-O virtual memory pages. | • **NOT** SRAM, DRAM, Flash, or EEPROM physical cell behavior.<br>• **NOT** representative of spaceborne microprocessors (e.g. BAE RAD750, Cobham GR740, Vorago VA416x0). |

---

## 3. Explicit Comparison: Operational Table Arm vs Transient Logical Arm (TFIB)

A critical scientific goal of the persistent-storage arm is to resolve the gap left by previous transient fault injection (TFIB):

```
+-----------------------------------------------------------------------------+
| Transient Logical-Value Arm (TFIB - Phases 1 to 10)                        |
| • Hook intercepts a stack-local variable (zeta_val) inside a single loop.  |
| • Affects exactly ONE butterfly operation in layer L.                      |
| • Table in memory remains completely pristine.                              |
| • Subsequent butterflies and re-encryption use uncorrupted constants.      |
| • Models transient computational ALU/register glitch.                       |
+-----------------------------------------------------------------------------+
                                      VS
+-----------------------------------------------------------------------------+
| Persistent Operational-Table Arm (Proposed Pilot & Phase 15)                |
| • Mutates the actual backing memory storage of mlk_zetas.                  |
| • Affects EVERY butterfly operation in every layer that references index i. |
| • Affects decapsulation inverse NTT AND re-encryption forward NTT/basemul.  |
| • Persists across the entire cryptographic transaction until repaired.      |
| • Models persistent storage-cell corruption in memory-mapped tables.       |
+-----------------------------------------------------------------------------+
```

### Key Confounders to Disclose in All Future Publications:
1. **Binary Layout Confounder:** Moving `mlk_zetas` from `__TEXT,__const` to `__DATA_CONST,__const` changes symbol relocation, PC-relative addressing offsets, and potential memory alignment.
2. **Optimization Confounder:** While disassembly confirms memory loads in the current research build, compilers may alter vector loop unrolling or register reuse across translation units.
3. **Platform Virtualization Confounder:** Darwin Mach VM operates through translation lookaside buffers (TLBs), page tables, and cache lines; hardware DRAM bit-flips in space bypass OS virtual memory entirely.

---

## 4. Mandatory Manuscript Guardrails

If the persistent-storage pilot is approved and executed, the following framing rules are mandatory for Manuscript v2 and all future publications:

1. **Title and Abstract:** Must refer exclusively to "software-level persistent storage fault injection" or "persistent table fault analysis". Terms such as "radiation resilience", "radiation testing", or "space qualification" are strictly prohibited.
2. **Methodology Section:** Must explicitly state that `mlk_zetas` was relocated from `__TEXT` to `__DATA_CONST` via compile-time research instrumentation, and that the upstream unmodified code is protected by Mach-O W^X enforcement.
3. **Threat Model:** Must specify that the threat model evaluates software tolerance to persistent parameter corruption, independent of the physical mechanism that induced the corruption.
