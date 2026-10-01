# Phase 7K: Independent Fault Injection Audit

## 1. Audit Framework & Code Inspection Protocol

Every fault class evaluated in the Phase 7J campaign was inspected against the compiled C source code in `algorithms/source_ref/` and `experiments/phase7j/phase7j_independent_validator.c`.

We audit:
1. **Target Locus & Variable**: The specific register or pointer mutated.
2. **Execution Reality**: Whether the modification genuinely perturbs in-flight production arithmetic or merely toggles a harness simulation flag.
3. **Checker Independence**: What parameters, constants, and registers are shared between the operational arithmetic and the monitoring check.
4. **Retry Mechanics**: Whether recovery re-executes authentic butterfly instructions.

---

## 2. Threat Class Inspection Table (J01 to J16)

| Class | Source Function & Location | Mutated State | Native Path? | Shared Dependencies | Recovery / Rejection Mechanism |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **J01** | `hook_mid_ntt_post_mul` (`mlkem_fault_hooks.c:250`) | In-flight intermediate `*t_ptr` | **YES** | Input $v$, twiddle $\zeta$ | Recomputes $t_{\text{check}}$, rolls back $r[j], r[j+\text{len}]$, retries butterfly $\to$ **Recovered**. |
| **J02** | `hook_mid_invntt_post_diff` (`mlkem_fault_hooks.c:744`)| In-flight difference `*diff_ptr` | **YES** | Inputs $u, v$, twiddle $\zeta$ | Recomputes $v'_{\text{expected}}$, rolls back shadow $(u, v)$, retries butterfly $\to$ **Recovered**. |
| **J03** | `hook_mid_ntt_butterfly` (`mlkem_fault_hooks.c:281`) | Output register `*r_j` (2-bit flip) | **YES** | Inputs $u, v$, twiddle $\zeta$ | Difference invariant detects multi-bit flip, rolls back $\to$ **Recovered**. |
| **J04** | `hook_mid_invntt_butterfly` (`mlkem_fault_hooks.c:765`)| Output register `*r_j_len` (2-bit flip) | **YES** | Inputs $u, v$, twiddle $\zeta$ | Multiplier invariant detects multi-bit flip, rolls back $\to$ **Recovered**. |
| **J05** | `hook_mid_invntt_butterfly` (`mlkem_fault_hooks.c:765`)| Persistent fault on $u$ register | **YES** | Shadow register $u_{\text{saved}}$ | Re-check on retry fails ($N_{\text{retry}}=1$), zeroizes registers $\to$ **Safe Reject**. |
| **J06** | `hook_mid_invntt_butterfly` (`mlkem_fault_hooks.c:765`)| Output register transient flip | **YES** | Inputs $u, v$, twiddle $\zeta$ | Evaluates false-alarm handling: rolls back, clean retry passes $\to$ **Recovered**. |
| **J07** | `hook_mid_invntt_pre_butterfly` (`mlkem_fault_hooks.c:710`)| Twiddle factor `*zeta_ptr` | **YES** | Shared $\zeta$ table entry | Local invariant evaluates to 0 (blind spot); FO re-encryption rejects $\to$ **Safe Reject**. |
| **J08** | `hook_mid_invntt_butterfly` (`mlkem_fault_hooks.c:765`)| Additive overflow $u' > 3329$ | **YES** | Modulus $q=3329$ | Barrett reduction check catches non-modular values $\to$ **Recovered**. |
| **J09** | `native_invntt_monitor_butterfly` (`mlkem_fault_hooks.c:850`)| Persistent bit active on retry | **YES** | Retry execution engine | Exceeds retry bound ($N_{\text{retry}}=1$), sets persistent flag $\to$ **Safe Reject**. |
| **J10** | `hook_mid_invntt_butterfly` (`mlkem_fault_hooks.c:790`)| Symmetric offset $(u'+\Delta, v'+\Delta)$ | **YES** | Dual rail comparator | Sum check $S = u' - (u+v)$ catches symmetric offset $\to$ **Recovered**. |
| **J11** | Forward & Inverse NTT hooks invoked concurrently | Simultaneous bit-flips in Fwd & Inv | **YES** | Separate forward/inverse state | Both monitors detect, rollback, and recompute $\to$ **Recovered**. |
| **J12** | Forward NTT Layer 1 output register | Permanent stuck bit | **YES** | Register hardware cell | Quenches butterfly to zero, sets persistent flag $\to$ **Safe Reject**. |
| **J13** | Inverse NTT Layer 7 output register | Permanent stuck bit | **YES** | Register hardware cell | Quenches butterfly to zero, sets persistent flag $\to$ **Safe Reject**. |
| **J14** | `mlkem768_dec(NULL)` public API call | Persistent stuck bit | **YES** | Global persistent counters | Hardened `kem.c` forces `fail = 0xFF`, emits $K_{\text{rej}}$ $\to$ **Safe Reject**. |
| **J15** | Direct input array modification | 1-byte flip in ciphertext input $c$ | **YES** | Ciphertext buffer | Fujisaki–Okamoto re-encryption mismatch $\to$ **Safe Reject**. |
| **J16** | Unmodified execution path | None (Clean baseline) | **YES** | Standard reference keypair | 0 false alarms, outputs authentic key $\to$ **Benign (Authentic Key)**. |

---

## 3. Critical Findings on Shared Operands & Common Modes

1. **Genuinely Native Execution**:
   Unlike early prototypes in Phase 7E where null callbacks were passed, every fault in the Phase 7J campaign directly perturbs live memory locations inside the active loop of `mlk_ntt_layer` and `mlk_invntt_layer`.
2. **The Twiddle Factor Common Mode (J07)**:
   The audit confirms that the native monitor cannot detect corruption in the twiddle factor $\zeta$ when $\zeta$ is modified in memory before butterfly entry. Because the checker recomputes $v'_{\text{expected}} = \text{fqmul}(d, \zeta)$, both the butterfly and the checker scale by the same corrupted constant, evaluating to zero difference. Resilience against twiddle table degradation is achieved downstream by the Fujisaki–Okamoto transform, which detects ciphertext re-encryption failure.
3. **Retry Boundedness (J09)**:
   The monitor strictly bounds retry attempts to $N_{\text{max\_retries}} = 1$. When a second fault occurs during the retry cycle, the implementation does not loop; it marks `persistent_count++`, zeroizes registers, and allows decapsulation to terminate safely via implicit rejection.
