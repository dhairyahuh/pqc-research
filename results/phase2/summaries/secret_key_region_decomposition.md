# Secret Key Memory Region Decomposition (ML-KEM-512, 768, 1024)

| Parameter Set | Memory Region | Dominant Observed Outcome | Rate (95% CI) | Security Consequence |
|:---|:---|:---|:---|:---|
| ML-KEM-512 | `REGION_SECRET_VECTOR_S` (Private vector s) | `IMPLICIT_REJECTION` | 100.00% [99.62, 100.00] | Key desynchronization; constant-time FO implicit rejection protects key. |
| ML-KEM-512 | `REGION_EMBEDDED_PK` (Public key pk) | `EXPLICIT_ERROR` | 100.00% [99.62, 100.00] | Pre-decapsulation trap; explicit failure prevents computation. |
| ML-KEM-512 | `REGION_HASH_HPK` (Hash H(pk)) | `EXPLICIT_ERROR` | 100.00% [99.62, 100.00] | Cryptographic binding mismatch; immediate explicit failure. |
| ML-KEM-512 | `REGION_REJECTION_SEED_Z` (Seed z) | `CORRECT` | 100.00% [99.62, 100.00] | Benign on valid ciphertexts; alters fallback key only on corrupted inputs. |
| ML-KEM-768 | `REGION_SECRET_VECTOR_S` (Private vector s) | `IMPLICIT_REJECTION` | 100.00% [99.62, 100.00] | Key desynchronization; constant-time FO implicit rejection protects key. |
| ML-KEM-768 | `REGION_EMBEDDED_PK` (Public key pk) | `EXPLICIT_ERROR` | 100.00% [99.62, 100.00] | Pre-decapsulation trap; explicit failure prevents computation. |
| ML-KEM-768 | `REGION_HASH_HPK` (Hash H(pk)) | `EXPLICIT_ERROR` | 100.00% [99.62, 100.00] | Cryptographic binding mismatch; immediate explicit failure. |
| ML-KEM-768 | `REGION_REJECTION_SEED_Z` (Seed z) | `CORRECT` | 100.00% [99.62, 100.00] | Benign on valid ciphertexts; alters fallback key only on corrupted inputs. |
| ML-KEM-1024 | `REGION_SECRET_VECTOR_S` (Private vector s) | `IMPLICIT_REJECTION` | 100.00% [99.62, 100.00] | Key desynchronization; constant-time FO implicit rejection protects key. |
| ML-KEM-1024 | `REGION_EMBEDDED_PK` (Public key pk) | `EXPLICIT_ERROR` | 100.00% [99.62, 100.00] | Pre-decapsulation trap; explicit failure prevents computation. |
| ML-KEM-1024 | `REGION_HASH_HPK` (Hash H(pk)) | `EXPLICIT_ERROR` | 100.00% [99.62, 100.00] | Cryptographic binding mismatch; immediate explicit failure. |
| ML-KEM-1024 | `REGION_REJECTION_SEED_Z` (Seed z) | `CORRECT` | 100.00% [99.62, 100.00] | Benign on valid ciphertexts; alters fallback key only on corrupted inputs. |
