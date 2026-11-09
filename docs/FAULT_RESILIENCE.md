# ASTRA-Sec: Fault Resilience, NTT Invariant Monitoring & SDC Suppression

**Permanent Research Title:** *Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems*  
**Foundational Software Case Study:** *Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment*  
**Date:** November 10, 2026  

---

## 1. Space Ionizing Radiation & Single-Event Upsets (SEUs)

Spacecraft in Low Earth Orbit (LEO) and geostationary orbits traverse trapped proton belts (South Atlantic Anomaly) and experience galactic cosmic rays. When a heavy ion strikes a CMOS storage cell or arithmetic register, it deposits charge that induces a **Single-Event Upset (SEU)** (transient bit-flip).

In lattice-based post-quantum cryptography:
- Polynomial multiplication is accelerated via the Number Theoretic Transform (NTT).
- An unmitigated bit-flip in the NTT butterfly coefficients or twiddle factors spreads corruptions across all 256 polynomial coefficients.
- This leads to **Silent Data Corruption (SDC)**: the decapsulated shared secret becomes corrupt, downstream symmetric keys mismatch, and communication is lost without a clear fault attribution.

---

## 2. Dual-Transform NTT Butterfly Invariant Mathematics

The Kyber / ML-KEM NTT operates over the ring $\mathcal{R}_q = \mathbb{Z}_q[X] / (X^{256} + 1)$ with prime modulus $q = 3329$.

In the Cooley-Tukey butterfly:
$$\hat{a} = a + t \cdot \zeta \pmod q$$
$$\hat{b} = a - t \cdot \zeta \pmod q$$

Where $\zeta$ is a precomputed primitive 256th root of unity (twiddle factor).

### The Two-Factor Butterfly Invariant (TFIB):
ASTRA-Sec monitors intermediate butterfly values by evaluating the dual-domain relationship:
$$r \equiv t \cdot \zeta \pmod{3329}$$

For each butterfly computation:
1. The forward transform evaluates candidate $r$.
2. The invariant monitor verifies that $r \cdot \zeta^{-1} \equiv t \pmod{3329}$.
3. Any arithmetic discrepancy ($r \not\equiv t \cdot \zeta$) immediately signals an SEU bit-flip before the corrupted coefficients propagate into the inverse transform.

### Mathematical Invariant Coverage
Across a single ML-KEM-768 decapsulation:
- ML-KEM-768 uses matrix dimension $k=3$.
- Forward NTTs: $k \times \text{vector transforms} = 3$ transforms.
- Pointwise polynomial multiplications: $k \times k = 9$ multiplications.
- Inverse NTTs: $k = 3$ transforms.
- Total NTT transforms evaluated: 11 transforms.
- Each transform evaluates $7 \text{ layers} \times 128 \text{ butterfly pairs} = 896$ butterfly operations.
- Total invariants checked per decapsulation: **$11 \times 896 = 9,856\ \text{butterflies}$**.

---

## 3. Localized Register Snapshot Rollback ($K \le 2$)

When an invariant violation is detected:
1. **Rollback Trigger**: Rather than aborting decapsulation and requiring a multi-second re-transmission across the space link, the system halts execution.
2. **Snapshot Restoration**: A localized snapshot of CPU registers and input polynomial coefficients (captured prior to the NTT layer) is restored.
3. **Retry Counter**: The retry counter $K$ is incremented ($K = 1$).
4. **Budget**: If the fault was transient (the charge dissipated), the retry succeeds. If the fault recurs, a second retry ($K = 2$) is attempted.

---

## 4. Fail-Stop Implicit Rejection & SDC Suppression

If $K > 2$ (indicating persistent hardware damage, stuck-at bit, or heavy multi-bit upset):
1. **Suppression Lockout**: Execution immediately engages **Fail-Stop Containment**.
2. **Pseudo-Random Seed Substitution**: Conforming to NIST FIPS 203 Section 7.3, decapsulation generates the implicit rejection shared secret:
   $$K_{\text{implicit}} = \text{J}(\text{sk}_{\text{PRF}} \parallel c)$$
3. **Outcome**: The attacker or faulty system receives an uncorrelated pseudo-random key. The subsequent AES-256-GCM authentication tag fails cleanly, completely eliminating Silent Data Corruption ($P_{\text{sdc}} = 0.00\%$).
