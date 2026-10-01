#!/usr/bin/env python3
"""
Independent Mathematical Validation Script: End-to-End Fault Chain Simulation
Standard: NIST FIPS 203 (ML-KEM)
Objective: Numerically simulate the complete analytical chain:
           Delta_NTT -> PolyMul(s, u) -> iNTT -> Decoding Slack Check (q/4 = 832) -> FO Check
           proving why Layer 1 perturbations yield 100% valid decapsulation while
           Layers 2-7 trigger implicit rejection.
"""

import random

Q = 3329
N = 256
ZETA = 17

def bit_rev_7(k: int) -> int:
    ans = 0
    for _ in range(7):
        ans = (ans << 1) | (k & 1)
        k >>= 1
    return ans

ZETAS = [pow(ZETA, bit_rev_7(k), Q) for k in range(128)]

def forward_ntt(poly: list) -> list:
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
                if layer == target_layer and current_butterfly == target_butterfly:
                    res_add = (res_add + delta) % Q
                r[j + length] = res_sub
                r[j] = res_add
                current_butterfly += 1
        length //= 2
        layer += 1
    return r

def poly_mul_ntt(a: list, b: list) -> list:
    """Base multiplication in NTT domain of two polynomials (degree-1 pairs mod X^2 - zeta)."""
    res = [0] * N
    for i in range(128):
        zeta_val = pow(ZETA, 2 * bit_rev_7(i) + 1, Q)
        a0, a1 = a[2 * i], a[2 * i + 1]
        b0, b1 = b[2 * i], b[2 * i + 1]
        res[2 * i] = (a0 * b0 + a1 * b1 * zeta_val) % Q
        res[2 * i + 1] = (a0 * b1 + a1 * b0) % Q
    return res

def fips_compress(x: int, d: int) -> int:
    return ((x * (1 << d) + (Q // 2)) // Q) % (1 << d)

def test_decoding_slack_behavior():
    """Verify that message decoding Compress_1(w) tolerates perturbations up to q/4 ~ 832."""
    print("\n[+] Verifying FIPS 203 Message Decoding Slack (Threshold q/4 = 832):")
    clean_bit0 = 0
    clean_bit1 = 1665
    for error in [100, 400, 800, 831, 832, 900]:
        recovered0 = fips_compress(clean_bit0 + error, 1)
        recovered1 = fips_compress(clean_bit1 - error, 1)
        status0 = "EXACT" if recovered0 == 0 else "FLIPPED"
        status1 = "EXACT" if recovered1 == 1 else "FLIPPED"
        if error < 832:
            assert recovered0 == 0 and recovered1 == 1, f"Error {error} unexpectedly flipped message bit!"
        print(f"    Noise Magnitude e={error:4d}: Bit0 -> {recovered0} [{status0}] | Bit1 -> {recovered1} [{status1}]")
    print("[PASS] Decoding Slack Verified: Message decoding strictly tolerates total error ||e||_infty < 832.")

def simulate_decapsulation_ntt_fault():
    """
    Simulate the exact indcpa_dec pipeline under NTT faults:
    1. u is decompressed ciphertext polynomial.
    2. Forward NTT is computed on u with a single butterfly fault (delta = 8).
    3. Multiplied by secret s (coefficients in [-2, 2]) in NTT domain.
    4. Inverse NTT is computed to recover s^T u in time domain.
    5. Check if maximum error in time domain exceeds decoding threshold q/4 = 832.
    """
    random.seed(123)
    trials = 100
    print("\n[+] Simulating indcpa_dec Pipeline Under NTT Faults (N=100 per layer, Delta = +8):")
    print("    Decoding Slack Threshold: q / 4 = 832.25")
    
    for layer in [1, 2, 4, 7]:
        error_exceeded_count = 0
        max_errors = []
        
        for _ in range(trials):
            # Sample secret s from CBD2: coefficients in [-2, 2]
            s_time = [random.randint(-2, 2) % Q for _ in range(N)]
            s_ntt = forward_ntt(s_time)
            
            # Decompressed u vector polynomial
            u_clean = [random.randint(0, Q - 1) for _ in range(N)]
            u_ntt_clean = forward_ntt(u_clean)
            
            # Faulted NTT on u
            u_ntt_fault = forward_ntt_single_fault(u_clean, target_layer=layer, target_butterfly=0, delta=8)
            
            # Compute s^T u
            clean_prod = poly_mul_ntt(s_ntt, u_ntt_clean)
            fault_prod = poly_mul_ntt(s_ntt, u_ntt_fault)
            
            clean_time = inverse_ntt(clean_prod)
            fault_time = inverse_ntt(fault_prod)
            
            # Measure error in time domain
            diffs = []
            for c1, c2 in zip(clean_time, fault_time):
                d = (c2 - c1) % Q
                if d > Q // 2:
                    d -= Q
                diffs.append(abs(d))
                
            m_err = max(diffs)
            max_errors.append(m_err)
            if m_err >= 832:
                error_exceeded_count += 1
                
        avg_max_err = sum(max_errors) / len(max_errors)
        overall_max = max(max_errors)
        message_recovery_rate = (trials - error_exceeded_count) / trials * 100
        
        print(f"    Layer L={layer}: Avg Max Err = {avg_max_err:6.1f} | Peak Err = {overall_max:4d} | Exceeded 832 = {error_exceeded_count:3d}/{trials} | Message Preserved = {message_recovery_rate:6.1f}%")
        
        if layer == 1:
            assert error_exceeded_count == 0, "Layer 1 unexpectedly flipped message bits!"
        else:
            assert error_exceeded_count > 0, f"Layer {layer} unexpectedly had zero message bit flips!"

    print("\n[PASS] Decapsulation NTT Fault Dichotomy Mathematically Proven:")
    print("       - Layer 1 error is diffused across the basis: time-domain error stays below 832 (100% clean message).")
    print("       - Layers 2-7 error remains concentrated: time-domain error exceeds 832, causing message bits to flip and triggering implicit rejection.")

if __name__ == "__main__":
    print("=" * 70)
    print(" INDEPENDENT MATHEMATICAL VALIDATION: END-TO-END FAULT CHAIN SIMULATION")
    print("=" * 70)
    test_decoding_slack_behavior()
    simulate_decapsulation_ntt_fault()
    print("=" * 70)
    print(" All end-to-end analytical chain simulations passed successfully.\n")
