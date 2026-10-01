#!/usr/bin/env python3
"""
Independent Mathematical Validation Script: NTT Butterfly Error Diffusion Tree
Standard: NIST FIPS 203 (ML-KEM, Algorithms 8 and 9)
Objective: Mathematically prove and verify the Claim 1 diffusion formulas:
           1. Shared intermediate / twiddle fault: N_diffused(L) = 2^(8 - L)
           2. Single output register fault:        N_diffused(L) = 2^(7 - L)
           independently from the C implementation.
"""

# ML-KEM Field Constants
Q = 3329
N = 256
ZETA = 17  # Primitive 256th root of unity mod 3329 (17^128 = -1 mod 3329)

def bit_rev_7(k: int) -> int:
    """Bit-reverse a 7-bit integer."""
    ans = 0
    for _ in range(7):
        ans = (ans << 1) | (k & 1)
        k >>= 1
    return ans

# Precompute 128 twiddle factors in bit-reversed order (FIPS 203 Section 2.3)
ZETAS = [pow(ZETA, bit_rev_7(k), Q) for k in range(128)]

def forward_ntt(poly: list) -> list:
    """
    Independent Pure Python Forward 7-Layer Cooley-Tukey NTT.
    Implements FIPS 203 Algorithm 8.
    """
    r = list(poly)
    k = 1
    length = 128
    while length >= 2:
        for start in range(0, N, 2 * length):
            zeta = ZETAS[k]
            k += 1
            for j in range(start, start + length):
                t = (zeta * r[j + length]) % Q
                r[j + length] = (r[j] - t) % Q
                r[j] = (r[j] + t) % Q
        length //= 2
    return r

def inverse_ntt(poly: list) -> list:
    """
    Independent Pure Python Inverse 7-Layer Gentleman-Sande NTT.
    Implements FIPS 203 Algorithm 9.
    """
    r = list(poly)
    k = 127
    length = 2
    while length <= 128:
        for start in range(0, N, 2 * length):
            zeta = ZETAS[k]
            k -= 1
            for j in range(start, start + length):
                t = r[j]
                r[j] = (t + r[j + length]) % Q
                r[j + length] = (zeta * (r[j + length] - t)) % Q
        length *= 2
    f = pow(128, -1, Q)
    return [(c * f) % Q for c in r]

def forward_ntt_single_fault(poly: list, target_layer: int, target_butterfly: int, delta: int) -> list:
    """
    Forward NTT with an additive perturbation Delta injected into a single output register r[j].
    Diffusion width should be exactly 2^(7 - L).
    """
    r = list(poly)
    k = 1
    length = 128
    layer = 1
    while length >= 2:
        current_butterfly = 0
        for start in range(0, N, 2 * length):
            zeta = ZETAS[k]
            k += 1
            for j in range(start, start + length):
                t = (zeta * r[j + length]) % Q
                res_sub = (r[j] - t) % Q
                res_add = (r[j] + t) % Q
                
                # Fault single output register r[j]
                if layer == target_layer and current_butterfly == target_butterfly:
                    res_add = (res_add + delta) % Q
                    
                r[j + length] = res_sub
                r[j] = res_add
                current_butterfly += 1
        length //= 2
        layer += 1
    return r

def forward_ntt_shared_fault(poly: list, target_layer: int, target_butterfly: int, delta: int) -> list:
    """
    Forward NTT with an additive perturbation Delta injected into the shared intermediate t.
    Both outputs r[j] and r[j+len] are perturbed.
    Diffusion width should be exactly 2^(8 - L).
    """
    r = list(poly)
    k = 1
    length = 128
    layer = 1
    while length >= 2:
        current_butterfly = 0
        for start in range(0, N, 2 * length):
            zeta = ZETAS[k]
            k += 1
            for j in range(start, start + length):
                t = (zeta * r[j + length]) % Q
                
                # Fault shared intermediate t
                if layer == target_layer and current_butterfly == target_butterfly:
                    t = (t + delta) % Q
                    
                r[j + length] = (r[j] - t) % Q
                r[j] = (r[j] + t) % Q
                current_butterfly += 1
        length //= 2
        layer += 1
    return r

def test_ntt_invertibility():
    """Verify clean NTT is perfectly invertible."""
    clean_poly = [(i * 13 + 7) % Q for i in range(N)]
    ntt_poly = forward_ntt(clean_poly)
    recovered = inverse_ntt(ntt_poly)
    assert recovered == clean_poly, "FAIL: Inverse NTT does not recover clean polynomial!"
    print("[PASS] NTT Invertibility: Forward and Inverse NTT are exact inverses.")

def test_diffusion_formulas():
    """
    Mathematically prove both diffusion formulas across all 7 layers:
    1. Shared intermediate t: N_diffused(L) = 2^(8 - L)
    2. Single output register: N_diffused(L) = 2^(7 - L)
    """
    clean_poly = [(i * 13 + 7) % Q for i in range(N)]
    clean_ntt = forward_ntt(clean_poly)
    delta = 15  # Non-zero perturbation
    
    print("\n[+] Testing NTT Error Diffusion Tree Across Layers 1 to 7:")
    print("  --- CASE 1: Shared Intermediate / Twiddle Fault (Formula: 2^(8 - L)) ---")
    for layer in range(1, 8):
        expected_shared = 1 << (8 - layer)  # 2^(8-L)
        faulted_shared = forward_ntt_shared_fault(clean_poly, target_layer=layer, target_butterfly=0, delta=delta)
        diff_count = sum(1 for c1, c2 in zip(clean_ntt, faulted_shared) if c1 != c2)
        print(f"    Layer L={layer}: Expected={expected_shared:3d} | Observed={diff_count:3d} | Match: {diff_count == expected_shared}")
        assert diff_count == expected_shared, f"Shared fault layer {layer} did not match expected {expected_shared}!"
        
    print("\n  --- CASE 2: Single Output Register Fault (Formula: 2^(7 - L)) ---")
    for layer in range(1, 8):
        expected_single = 1 << (7 - layer)  # 2^(7-L)
        faulted_single = forward_ntt_single_fault(clean_poly, target_layer=layer, target_butterfly=0, delta=delta)
        diff_count = sum(1 for c1, c2 in zip(clean_ntt, faulted_single) if c1 != c2)
        print(f"    Layer L={layer}: Expected={expected_single:3d} | Observed={diff_count:3d} | Match: {diff_count == expected_single}")
        assert diff_count == expected_single, f"Single fault layer {layer} did not match expected {expected_single}!"

    print("\n[PASS] Claim 1 Mathematically Proven:")
    print("       - Shared intermediate fault diffuses across 2^(8 - L) coefficients (128 down to 2).")
    print("       - Single output register fault diffuses across 2^(7 - L) coefficients (64 down to 1).")

if __name__ == "__main__":
    print("=" * 70)
    print(" INDEPENDENT MATHEMATICAL VALIDATION: NTT BUTTERFLY DIFFUSION TREE")
    print("=" * 70)
    test_ntt_invertibility()
    test_diffusion_formulas()
    print("=" * 70)
    print(" All mathematical NTT diffusion checks passed successfully.\n")
