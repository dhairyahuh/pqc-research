/* mem_campaign.c — Phase 2 logical-value memory-fault campaign.
 *
 * Reuses the EXACT same deterministic inputs, real decapsulation path, and
 * independent oracle as tfib_experiment_runner.c, but emits v1 fault-contract
 * records (research/fault_contract/fault_contract.h) and classifies terminal
 * outcomes with fc_classify(). The historical runner/CSV are left untouched;
 * this is an additive, parallel path for a matched comparison.
 *
 * SCOPE: every fault here mutates a TEMPORARY LOGICAL VALUE (a local copy of a
 * twiddle/tag/checker word), NOT persistent backing storage (the const tables are
 * never written). This is NOT physical radiation simulation and NOT persistent-
 * memory recovery. See research/FAULT_MODEL_SPECIFICATION.md and the persistent-
 * storage blocker note.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "tfib_common.h"
#include "tfib_core.h"
#include "independent_oracle.h"
#include "fips202_ref.h"
#include "campaign_prf.h"
#include "fault_contract.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);
int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(i ^ 0xAA);
    return 0;
}

static fc_target_t locus_target(tfib_fault_locus_t l) {
    switch (l) {
        case TFIB_FAULT_OP_TWIDDLE:   return FC_TGT_OP_TWIDDLE;
        case TFIB_FAULT_REF_TWIDDLE:  return FC_TGT_REF_TABLE;
        case TFIB_FAULT_META_TAG:     return FC_TGT_META_TAG;
        case TFIB_FAULT_CHECKER_LOGIC:return FC_TGT_CHECKER_LOGIC;
        case TFIB_FAULT_SIMULTANEOUS: return FC_TGT_OP_TWIDDLE; /* op+ref coordinated */
        default:                      return FC_TGT_NONE;
    }
}
static const char *locus_model(tfib_fault_locus_t l) {
    switch (l) {
        case TFIB_FAULT_OP_TWIDDLE:   return "mem.logical.op_twiddle";
        case TFIB_FAULT_REF_TWIDDLE:  return "mem.logical.ref_twiddle";
        case TFIB_FAULT_META_TAG:     return "mem.logical.meta_tag";
        case TFIB_FAULT_CHECKER_LOGIC:return "mem.logical.checker_logic";
        case TFIB_FAULT_SIMULTANEOUS: return "mem.logical.simultaneous_pair";
        default:                      return "none";
    }
}

/* <!-- MC-APPEND --> */
static const char *inj_name(fc_injection_status_t s) {
    switch (s) { case FC_INJ_NOT_ARMED: return "NOT_ARMED";
        case FC_INJ_INELIGIBLE: return "INELIGIBLE"; case FC_INJ_FAILED: return "FAILED";
        case FC_INJ_ACTIVATED: return "ACTIVATED"; default: return "?"; }
}
static const char *oracle_name(fc_oracle_verdict_t v) {
    switch (v) { case FC_ORACLE_VALID: return "VALID"; case FC_ORACLE_REJECT: return "REJECT";
        case FC_ORACLE_NEITHER: return "NEITHER"; default: return "UNAVAILABLE"; }
}
static const char *tgt_name(fc_target_t t) {
    switch (t) { case FC_TGT_OP_TWIDDLE: return "OP_TWIDDLE"; case FC_TGT_REF_TABLE: return "REF_TABLE";
        case FC_TGT_META_TAG: return "META_TAG"; case FC_TGT_CHECKER_LOGIC: return "CHECKER_LOGIC";
        default: return "NONE"; }
}

static int g_inconsistent = 0;

static void run_suite_v1(FILE *fp, int *trial_id, tfib_mode_t mode, const char *mode_name,
                         const char *suite_name, tfib_fault_locus_t locus, bool persistent,
                         int num_trials, fc_ledger_t *led) {
    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
    uint8_t ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej_expected[SS_BYTES];
    tfib_set_mode(mode);

    for (int t = 0; t < num_trials; t++) {
        tfib_fault_reset();
        tfib_reset_all_stats();

        uint8_t prf_output[64 + 32];
        campaign_prf(prf_output, sizeof(prf_output), t, mode, locus, persistent);
        if (independent_oracle_keypair_derand(pk, sk, prf_output) != 0 ||
            independent_oracle_encaps_derand(ct, ss_expected, pk, prf_output + 64) != 0 ||
            independent_oracle_compute_rejection(ss_rej_expected, sk, ct) != 0) {
            fprintf(stderr, "FATAL: oracle input generation failed (trial %d)\n", t); exit(2);
        }

        unsigned stage = (unsigned)((t % 7) + 1);
        unsigned b_idx = (unsigned)((t * 17) % 128);
        uint8_t bit = (uint8_t)((t % 15) + 1);
        if (locus != TFIB_FAULT_NONE) tfib_fault_arm(locus, stage, b_idx, bit, persistent);

        uint32_t status = 0;
        (void)mlkem768_dec_monitored(ss_out, ct, sk, &status);

        /* ---- build the v1 record; dimensions kept strictly separate ---- */
        fc_trial_t tr; memset(&tr, 0, sizeof(tr));
        fc_event_t *e = &tr.event;
        e->schema_version = FC_SCHEMA_VERSION;
        strncpy(e->model_id, locus_model(locus), sizeof(e->model_id) - 1);
        e->model_version = 1;
        e->target_component = locus_target(locus);
        e->target_id = b_idx;
        e->phase = stage;
        e->seed = (uint64_t)CAMPAIGN_SEED_BASE_MAGIC + (uint64_t)t * 31u;
        e->event_index = (uint64_t)(*trial_id);
        e->op_index = b_idx;
        e->location_kind = FC_LOC_BIT;
        e->location = (uint32_t)(bit % 16);
        e->mask = (uint64_t)(1u << (bit % 16));
        e->fault_class = FC_CLASS_LOGICAL_VALUE;          /* temporary local value only */
        e->duration = persistent ? FC_DUR_PERSISTENT : FC_DUR_TRANSIENT;
        e->combo_group = (locus == TFIB_FAULT_SIMULTANEOUS) ? 1 : -1;
        e->armed = (locus != TFIB_FAULT_NONE) ? 1u : 0u;
        e->target_accessible = e->armed;                   /* local copies always reachable */
        e->mutation_applied  = e->armed;                   /* injector attempted at the site */
        e->target_actually_affected = (g_tfib_fault.trigger_count > 0) ? 1u : 0u;

        tr.monitor.detected = (tfib_get_total_mismatches() > 0) ? 1u : 0u;
        tr.monitor.claimed_recovery = (tfib_get_total_recoveries() > 0) ? 1u : 0u;
        tr.monitor.claimed_fail_stop = (uint8_t)(tr.monitor.detected && !tr.monitor.claimed_recovery);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);
        tr.oracle = ss_match ? FC_ORACLE_VALID : (rej_match ? FC_ORACLE_REJECT : FC_ORACLE_NEITHER);

        fc_ledger_begin(led);
        bool consistent = fc_trial_consistent(&tr);
        fc_outcome_t outcome;
        if (!consistent) { g_inconsistent++; outcome = FC_OUT_INCONCLUSIVE; }
        else outcome = fc_classify(&tr);
        fc_ledger_record(led, outcome);

        fc_injection_status_t inj = fc_injection_status(e);
        fprintf(fp,
            "{\"trial_id\":%d,\"config\":\"%s\",\"suite\":\"%s\",\"t\":%d,"
            "\"stage\":%u,\"butterfly\":%u,\"bit\":%u,\"persistent\":%d,"
            "\"model_id\":\"%s\",\"target\":\"%s\",\"fault_class\":\"LOGICAL_VALUE\","
            "\"duration\":\"%s\",\"combo_group\":%d,"
            "\"armed\":%u,\"accessible\":%u,\"applied\":%u,\"affected\":%u,"
            "\"injection_status\":\"%s\",\"monitor_detected\":%u,\"monitor_claimed_recovery\":%u,"
            "\"oracle_verdict\":\"%s\",\"terminal_outcome\":\"%s\",\"consistent\":%d,"
            "\"status\":\"0x%08X\",\"ss_match\":%d,\"rej_match\":%d}\n",
            (*trial_id)++, mode_name, suite_name, t, stage, b_idx, bit, persistent ? 1 : 0,
            locus_model(locus), tgt_name(locus_target(locus)),
            persistent ? "PERSISTENT" : "TRANSIENT", e->combo_group,
            e->armed, e->target_accessible, e->mutation_applied, e->target_actually_affected,
            inj_name(inj), tr.monitor.detected, tr.monitor.claimed_recovery,
            oracle_name(tr.oracle), fc_outcome_name(outcome), consistent ? 1 : 0,
            status, ss_match ? 1 : 0, rej_match ? 1 : 0);
    }
}

int main(int argc, char **argv) {
    if (independent_oracle_init() != 0) { fprintf(stderr, "FATAL: oracle init failed\n"); return 1; }
    const char *out = (argc > 1) ? argv[1] : "research/results/phase2_mem_logical_v1/raw.jsonl";
    int per = (argc > 3 && strcmp(argv[2], "--pilot") == 0) ? atoi(argv[3]) : 50;
    FILE *fp = fopen(out, "w");
    if (!fp) { perror("fopen"); return 1; }

    fc_ledger_t led; fc_ledger_init(&led);
    int id = 0;
    struct { tfib_mode_t m; const char *mn; const char *sn; tfib_fault_locus_t l; bool p; } S[] = {
        {TFIB_MODE_BASELINE,"BASELINE","CLEAN_CONTROL",TFIB_FAULT_NONE,false},
        {TFIB_MODE_BASELINE,"BASELINE","OP_TWIDDLE_TRANSIENT",TFIB_FAULT_OP_TWIDDLE,false},
        {TFIB_MODE_BASELINE,"BASELINE","OP_TWIDDLE_PERSISTENT",TFIB_FAULT_OP_TWIDDLE,true},
        {TFIB_MODE_REF,"TFIB_REF","CLEAN_CONTROL",TFIB_FAULT_NONE,false},
        {TFIB_MODE_REF,"TFIB_REF","OP_TWIDDLE_TRANSIENT",TFIB_FAULT_OP_TWIDDLE,false},
        {TFIB_MODE_REF,"TFIB_REF","OP_TWIDDLE_PERSISTENT",TFIB_FAULT_OP_TWIDDLE,true},
        {TFIB_MODE_REF,"TFIB_REF","REF_TWIDDLE_TRANSIENT",TFIB_FAULT_REF_TWIDDLE,false},
        {TFIB_MODE_REF,"TFIB_REF","REF_TWIDDLE_PERSISTENT",TFIB_FAULT_REF_TWIDDLE,true},
        {TFIB_MODE_REF,"TFIB_REF","SIMULTANEOUS_COMMON_MODE",TFIB_FAULT_SIMULTANEOUS,false},
        {TFIB_MODE_REF,"TFIB_REF","CHECKER_LOGIC_TRANSIENT",TFIB_FAULT_CHECKER_LOGIC,false},
        {TFIB_MODE_REF,"TFIB_REF","CHECKER_LOGIC_PERSISTENT",TFIB_FAULT_CHECKER_LOGIC,true},
        {TFIB_MODE_META,"TFIB_META","CLEAN_CONTROL",TFIB_FAULT_NONE,false},
        {TFIB_MODE_META,"TFIB_META","OP_TWIDDLE_TRANSIENT",TFIB_FAULT_OP_TWIDDLE,false},
        {TFIB_MODE_META,"TFIB_META","OP_TWIDDLE_PERSISTENT",TFIB_FAULT_OP_TWIDDLE,true},
        {TFIB_MODE_META,"TFIB_META","META_TAG_TRANSIENT",TFIB_FAULT_META_TAG,false},
        {TFIB_MODE_META,"TFIB_META","META_TAG_PERSISTENT",TFIB_FAULT_META_TAG,true},
        {TFIB_MODE_META,"TFIB_META","CHECKER_LOGIC_TRANSIENT",TFIB_FAULT_CHECKER_LOGIC,false},
        {TFIB_MODE_META,"TFIB_META","CHECKER_LOGIC_PERSISTENT",TFIB_FAULT_CHECKER_LOGIC,true},
    };
    for (size_t i = 0; i < sizeof(S)/sizeof(S[0]); i++)
        run_suite_v1(fp, &id, S[i].m, S[i].mn, S[i].sn, S[i].l, S[i].p, per, &led);
    fclose(fp);

    int lrc = fc_ledger_check(&led);
    printf("trials=%llu finalized=%llu ledger_check=%d inconsistent=%d\n",
           (unsigned long long)led.started, (unsigned long long)led.finalized, lrc, g_inconsistent);
    for (int o = 0; o < FC_OUT__COUNT; o++)
        if (led.by_outcome[o]) printf("  %-24s %llu\n", fc_outcome_name((fc_outcome_t)o),
                                      (unsigned long long)led.by_outcome[o]);
    printf("wrote %s\n", out);
    return (lrc == 0 && g_inconsistent == 0) ? 0 : 3;
}

