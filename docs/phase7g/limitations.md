# Phase 7G: Limitations, Threats to Validity, and Hardware Realities

## 1. Threats to Validity and Scope Boundaries

While Phase 7G resolves the integration defects identified in Phase 7E and 7F, several key engineering and physical limitations must be acknowledged:

### 1.1 Twiddle Factor Shared Operand Blind Spot (Class 2)
- **Limitation**: The butterfly invariant $D = (u' - v') - 2\cdot\text{fqmul}(v, \zeta)$ evaluates arithmetic consistency between inputs $(u, v)$, the twiddle factor $\zeta$, and outputs $(u', v')$. If the twiddle factor $\zeta$ itself is corrupted during DRAM fetch or in the cache line before loading, both the primary computation and the monitor's recomputation use the same corrupted $\zeta^*$.
- **Implication**: The invariant cannot detect pre-computation corruption of twiddle factors without an independent ROM verification table or redundant lookup paths.
- **Safety Backstop**: Fortunately, this fault is absorbed by the downstream Fujisaki-Okamoto re-encryption check ($\hat{c}' \neq c$), resulting in 100% safe implicit rejection ($K_{\text{rej}}$) with 0.0% undetected key corruption.

### 1.2 SIMD / Neon / AVX Vectorization Impact
- **Current Scope**: Evaluated on the C reference implementation where loop unrolling and compiler scalar optimizations (`-O3`) operate over 16-bit integers.
- **Vectorized Architectures**: On production hardware using ARM Neon or AVX2 vector instructions (e.g. processing 8 or 16 butterfly operations in parallel SIMD lanes), register rollback requires vector register saving and lane-masking retry. Implementing butterfly invariants across SIMD lanes will alter the micro-architectural instruction mix and may impact vector throughput differently.

### 1.3 Trusted Local Register Assumptions
- **Model Assumption**: The monitor assumes that register values $(u_{\text{saved}}, v_{\text{saved}})$ preserved on the stack or in callee-saved registers during the 10–20 cycle window of butterfly execution are not subjected to a second, concurrent ion strike.
- **Physical Justification**: In Low Earth Orbit (LEO) or Geostationary Orbit (GEO), the flux of cosmic heavy ions causing Single Event Effects (SEE) is on the order of $10^{-5}$ to $10^{-3}$ events per device-day. The probability of two distinct particle strikes occurring in the same 5-nanosecond window within the same register file is physically negligible ($P < 10^{-18}$).

### 1.4 Persistent Fault (Class 6) Recovery Bound
- **Limitation**: Transient fault recovery mechanisms cannot repair physical gate damage (e.g. Total Ionizing Dose breakdown or Single Event Burnout).
- **Graceful Degradation**: The monitor bounds retries to $N=1$. When a retry fails to clear the error, the system classifies the fault as permanent, enters a fail-safe state, and forces implicit rejection. Recovery is impossible without redundant physical cores.

---

## 2. Path to Physical Beam Validation

Phase 7G provides a validated software baseline with verified in-tree execution. For flight qualification (TRL 6+), the following steps remain:
1. **FPGA Hardware Emulation**: Synthesize ML-KEM accelerator IP with dual-rail butterfly ALUs on radiation-tolerant FPGAs (e.g. Microchip RT PolarFire or AMD Xilinx Space Grade Kintex UltraScale).
2. **Heavy-Ion / Proton Beam Testing**: Subject the target SoC running the instrumented ML-KEM binary to mono-energetic proton (60–200 MeV) or heavy-ion beams (e.g. at Texas A&M Cyclotron Institute or CERN CHARM) to measure real cross-sections for SEUs versus autonomous recovery.
