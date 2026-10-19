/* test_fault_contract.c — Phase 1 negative/positive tests for the fault contract.
 * Exit 0 iff every invariant holds. Build with -Wall -Wextra -Werror -Wconversion
 * and -fsanitize=address,undefined (see run_phase1_tests.sh).
 */
#include "fault_contract.h"
#include <stdio.h>

static int g_fail = 0;
#define CHECK(cond, msg) do { \
    if (!(cond)) { printf("  FAIL: %s\n", (msg)); g_fail++; } \
    else         { printf("  ok  : %s\n", (msg)); } \
} while (0)

/* Build an armed, fully-activated fault event. */
static fc_event_t armed_activated(void) {
    fc_event_t e; memset(&e, 0, sizeof(e));
    e.schema_version = FC_SCHEMA_VERSION;
    strcpy(e.model_id, "mem.bitflip");
    e.model_version = 1;
    e.target_component = FC_TGT_OP_TWIDDLE;
    e.fault_class = FC_CLASS_LOGICAL_VALUE;
    e.duration = FC_DUR_TRANSIENT;
    e.combo_group = -1;
    e.armed = true;
    e.target_accessible = true;
    e.mutation_applied = true;
    e.target_actually_affected = true;
    return e;
}

static fc_trial_t trial_of(fc_event_t e, fc_oracle_verdict_t ov,
                           bool detected, bool claimed_recovery) {
    fc_trial_t t; memset(&t, 0, sizeof(t));
    t.event = e; t.oracle = ov;
    t.monitor.detected = detected;
    t.monitor.claimed_recovery = claimed_recovery;
    return t;
}

int main(void) {
    printf("== Phase 1 fault-contract invariants ==\n");

    /* CRITERION 3: recovery requires an independent VALID verdict. A monitor that
     * loudly claims recovery cannot force RECOVERED when the oracle disagrees. */
    {
        fc_trial_t t = trial_of(armed_activated(), FC_ORACLE_REJECT, true, true);
        CHECK(fc_classify(&t) != FC_OUT_RECOVERED,
              "monitor 'recovery' with oracle=REJECT is NOT recovered");
        CHECK(fc_classify(&t) == FC_OUT_SAFE_FAIL_DETECTED,
              "oracle=REJECT + detected -> SAFE_FAIL_DETECTED");

        t = trial_of(armed_activated(), FC_ORACLE_REJECT, false, false);
        CHECK(fc_classify(&t) == FC_OUT_SAFE_FAIL_FO_CONTAINED,
              "oracle=REJECT + undetected -> SAFE_FAIL_FO_CONTAINED (not conflated)");

        t = trial_of(armed_activated(), FC_ORACLE_NEITHER, true, true);
        CHECK(fc_classify(&t) == FC_OUT_SDC, "oracle=NEITHER -> SDC (monitor claim ignored)");

        t = trial_of(armed_activated(), FC_ORACLE_UNAVAILABLE, true, true);
        CHECK(fc_classify(&t) == FC_OUT_INCONCLUSIVE,
              "no oracle verdict -> INCONCLUSIVE, never RECOVERED");

        t = trial_of(armed_activated(), FC_ORACLE_VALID, true, false);
        CHECK(fc_classify(&t) == FC_OUT_RECOVERED,
              "activated+detected+oracle=VALID -> RECOVERED (the only path)");

        t = trial_of(armed_activated(), FC_ORACLE_VALID, false, false);
        CHECK(fc_classify(&t) == FC_OUT_INEFFECTIVE,
              "activated+undetected+oracle=VALID -> INEFFECTIVE (not recovered)");
    }

    /* CRITERION 2: ineligible / failed injections cannot be counted as activated. */
    {
        fc_event_t e = armed_activated(); e.target_accessible = false;
        fc_trial_t t = trial_of(e, FC_ORACLE_VALID, true, true);
        CHECK(fc_injection_status(&e) == FC_INJ_INELIGIBLE, "inaccessible target -> INELIGIBLE");
        CHECK(fc_classify(&t) == FC_OUT_INELIGIBLE,
              "ineligible stays INELIGIBLE despite monitor detect/recovery claims");

        e = armed_activated(); e.target_actually_affected = false; /* applied, no effect */
        t = trial_of(e, FC_ORACLE_VALID, false, false);
        CHECK(fc_injection_status(&e) == FC_INJ_FAILED, "no read-back change -> INJECTION_FAILED");
        CHECK(fc_classify(&t) == FC_OUT_INJECTION_FAILED,
              "failed injection != INEFFECTIVE and != activated");
    }

    /* CRITERION 2: a clean-control false alarm is NOT a recovery. */
    {
        fc_event_t e; memset(&e, 0, sizeof(e));
        e.schema_version = FC_SCHEMA_VERSION; e.armed = false; e.combo_group = -1;
        fc_trial_t t = trial_of(e, FC_ORACLE_VALID, true /*false alarm*/, true);
        CHECK(fc_classify(&t) == FC_OUT_CLEAN_COMPLETED,
              "unarmed trial with monitor false-alarm -> CLEAN_COMPLETED, not RECOVERED");
    }

    /* no-conflation guard: a known SDC trial must classify as SDC (catches a
     * vacuous classifier that returns CLEAN/COMPLETED for everything). */
    {
        fc_trial_t t = trial_of(armed_activated(), FC_ORACLE_NEITHER, false, false);
        CHECK(fc_classify(&t) == FC_OUT_SDC, "known-bad output surfaces as SDC");
    }

    /* excluded trials require a reason. */
    {
        fc_trial_t t = trial_of(armed_activated(), FC_ORACLE_VALID, true, false);
        t.excluded = true;
        CHECK(fc_classify(&t) == FC_OUT_INCONCLUSIVE, "excluded w/o reason -> INCONCLUSIVE");
        strcpy(t.exclude_reason, "injector OS trap");
        CHECK(fc_classify(&t) == FC_OUT_EXCLUDED, "excluded w/ reason -> EXCLUDED");
    }

    /* CRITERION 5: trial accounting must detect a dropped record. */
    {
        fc_ledger_t l; fc_ledger_init(&l);
        for (int i = 0; i < 5; i++) fc_ledger_begin(&l);
        for (int i = 0; i < 4; i++) fc_ledger_record(&l, FC_OUT_RECOVERED); /* drop one */
        CHECK(fc_ledger_check(&l) != 0, "ledger detects a missing/dropped trial record");
        fc_ledger_record(&l, FC_OUT_SAFE_FAIL_DETECTED);
        CHECK(fc_ledger_check(&l) == 0, "ledger balances once all trials finalized");
    }

    /* CRITERION: malformed / internally inconsistent records fail validation. */
    {
        fc_trial_t t = trial_of(armed_activated(), FC_ORACLE_VALID, true, false);
        CHECK(fc_trial_consistent(&t), "well-formed activated record is consistent");

        fc_trial_t bad = t; bad.event.schema_version = 999;
        CHECK(!fc_trial_consistent(&bad), "wrong schema_version fails validation");

        bad = t; bad.event.target_component = (fc_target_t)255;
        CHECK(!fc_trial_consistent(&bad), "out-of-range target fails validation");

        bad = t; bad.event.armed = 0; /* unarmed but still carries activation evidence */
        CHECK(!fc_trial_consistent(&bad), "unarmed record with activation evidence is inconsistent");

        bad = t; bad.event.mutation_applied = 0; /* affected without applied */
        CHECK(!fc_trial_consistent(&bad), "affected-without-applied is inconsistent");
    }

    printf("== %s (%d failures) ==\n", g_fail ? "FAILED" : "PASSED", g_fail);
    return g_fail ? 1 : 0;
}
