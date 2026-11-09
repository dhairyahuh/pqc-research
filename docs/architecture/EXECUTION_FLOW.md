# Cryptographic Execution Flow

This document details the exact execution pipeline for NIST FIPS 203 ML-KEM-768 decapsulation augmented with TFIB (Twiddle Factor Integrity Binding).

## 1. Sequence Diagram: Decapsulation with TFIB Pre-Assertion

```mermaid
sequenceDiagram
    autonumber
    actor Ground as Ground Station / Sender
    participant Flight as Satellite Flight Software
    participant TFIB as TFIB Integrity Monitor
    participant Decaps as ML-KEM Decapsulation Engine
    participant NTT as NTT / InvNTT Engine
    participant FO as Fujisaki-Okamoto Re-encryption

    Ground->>Flight: Transmit Ciphertext (c)
    Flight->>TFIB: tfib_assert_integrity(&zetas)
    
    alt Table Clean
        TFIB-->>Flight: TFIB_SUCCESS (0)
    else SEU Bit-Flip Detected in zetas
        TFIB->>TFIB: tfib_restore_from_gold(&zetas)
        TFIB->>Flight: TFIB_HEALED_SEU_DETECTED (Log Telemetry)
    end
    
    Flight->>Decaps: crypto_kem_dec(ss, c, sk)
    Decaps->>NTT: Forward / Inverse Polynomial Mult
    NTT-->>Decaps: Decrypted Message m'
    Decaps->>FO: Re-encrypt c' = Encrypt(pk, m')
    
    alt c' == c (Ciphertext Valid)
        FO-->>Flight: Derived Shared Secret K = H(m', c)
    else c' != c (Ciphertext Invalid or SEU in arithmetic)
        FO-->>Flight: Implicit Rejection Secret K = H(z, c)
    end
    
    Flight-->>Ground: Complete Session Handshake
```

## 2. Stage Breakdown

### Stage 1: Pre-Assertion Gate
Before initiating any polynomial transformations, `tfib_assert_integrity` computes a fast bounded hash/checksum of the 128 active 16-bit twiddle factor coefficients in SRAM. The result is compared against the immutable reference value. If an SEU bit-flip is detected, the self-healing subroutine copies the gold table from write-protected storage and logs an SEU telemetry event.

### Stage 2: In-Place Butterfly Operations
The Decapsulation routine executes NTT and inverse-NTT passes over 256-element polynomials in $\mathbb{Z}_q[X]/(X^{256}+1)$ with $q=3329$. Montgomery reduction ensures intermediate 16-bit multiplications remain strictly bounded within $[0, 2q)$.

### Stage 3: Fujisaki-Okamoto Transform (Implicit Rejection)
In ML-KEM decapsulation, after recovering candidate message $m'$, the engine re-encrypts $m'$ using the public key $pk$ to produce $c'$. It performs a constant-time comparison `verify(c, c')`. If the comparison fails (due to invalid input or transient arithmetic faults), it returns $K = \text{SHAKE256}(z \| c)$, deterministically rejecting the input without disclosing whether rejection stemmed from authentication failure or bit errors.

