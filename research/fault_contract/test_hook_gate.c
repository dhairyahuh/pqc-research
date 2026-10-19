/* test_hook_gate.c — CRITERION 6 regression guard.
 * Clean/production builds must NOT define the research fault-hook macros. This TU
 * fails to COMPILE if they are defined, so a production build that accidentally
 * enables hooks turns into a hard build error instead of silent instrumentation.
 */
#if defined(MLKEM_RESEARCH_FAULT_HOOKS)
#error "MLKEM_RESEARCH_FAULT_HOOKS must not be enabled in clean/production builds"
#endif
#if defined(MLDSA_RESEARCH_FAULT_HOOKS)
#error "MLDSA_RESEARCH_FAULT_HOOKS must not be enabled in clean/production builds"
#endif
#include <stdio.h>
int main(void) {
    printf("hook-gate OK: research fault hooks are OFF in this build configuration\n");
    return 0;
}
