/* fault_contract.h — Canonical fault-event schema, outcome taxonomy, and trial
 * accounting for the ML-KEM-768 space-resilience research extension (Phase 1).
 *
 * Design goals (see research/FAULT_MODEL_SPECIFICATION.md):
 *   - One versioned fault-event schema shared by all experiments.
 *   - Logical-value corruption vs persistent-storage corruption are distinct.
 *   - Injection eligibility/activation and terminal outcomes CANNOT be conflated.
 *   - RECOVERED is unreachable without an INDEPENDENT correctness verdict (VALID).
 *   - Every trial is accounted for (including ineligible / failed / excluded).
 *
 * Header-only, C11, no dependencies, no I/O. Pure functions + a plain ledger.
 */
#ifndef FAULT_CONTRACT_H
#define FAULT_CONTRACT_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define FC_SCHEMA_VERSION 1u

/* What is corrupted (component). Extend by appending; never renumber (schema stability). */
typedef enum {
    FC_TGT_NONE = 0,
    FC_TGT_OP_TWIDDLE,        /* operational NTT twiddle value/table           */
    FC_TGT_TRANSFORM_STATE,   /* intermediate NTT/invNTT coefficient state      */
    FC_TGT_REF_TABLE,         /* TFIB-Ref independent reference table           */
    FC_TGT_META_TAG,          /* TFIB-Meta integrity tag/metadata               */
    FC_TGT_CHECKER_LOGIC,     /* monitor comparison/decision state              */
    FC_TGT_PERSISTENT_KEY,    /* persistent secret-key state (test fixture)     */
    FC_TGT_CHANNEL_MESSAGE,   /* protocol/channel message bytes                 */
    FC_TGT__COUNT
} fc_target_t;

/* CRITERION 1: the physical nature of the corruption. */
typedef enum {
    FC_CLASS_LOGICAL_VALUE = 0, /* a value in a register/local copy is altered;
                                 * backing storage is NOT changed (transient read) */
    FC_CLASS_PERSISTENT_STORAGE /* the backing storage is altered; subsequent
                                 * reads observe the corruption until repaired     */
} fc_fault_class_t;

typedef enum { FC_DUR_TRANSIENT = 0, FC_DUR_PERSISTENT } fc_duration_t;

typedef enum { FC_LOC_BIT = 0, FC_LOC_BYTE, FC_LOC_WORD, FC_LOC_LOGICAL } fc_loc_kind_t;

/* CRITERION 2: injection status is first-class and derived, never asserted by a monitor. */
typedef enum {
    FC_INJ_NOT_ARMED = 0, /* no fault requested (clean control)                 */
    FC_INJ_INELIGIBLE,    /* target not accessible / cannot apply as specified  */
    FC_INJ_FAILED,        /* attempted, but mutation did not take effect        */
    FC_INJ_ACTIVATED      /* applied AND target actually affected (evidence)    */
} fc_injection_status_t;

/* CRITERION 3: the ONLY source of correctness truth is an independent oracle. */
typedef enum {
    FC_ORACLE_UNAVAILABLE = 0, /* no independent verdict -> cannot claim recovery */
    FC_ORACLE_VALID,           /* output == independent expected valid shared secret */
    FC_ORACLE_REJECT,          /* output == independent expected implicit-rejection  */
    FC_ORACLE_NEITHER          /* output matches neither -> silent data corruption    */
} fc_oracle_verdict_t;

/* Distinct, non-conflatable terminal outcomes. */
typedef enum {
    FC_OUT_CLEAN_COMPLETED = 0,
    FC_OUT_INELIGIBLE,
    FC_OUT_INJECTION_FAILED,
    FC_OUT_INEFFECTIVE,     /* activated, undetected, oracle VALID (absorbed)      */
    FC_OUT_RECOVERED,       /* activated, detected, oracle VALID (independently!)  */
    FC_OUT_SAFE_FAIL_DETECTED,    /* oracle REJECT, local checker detected (fail-stop)   */
    FC_OUT_SAFE_FAIL_FO_CONTAINED,/* oracle REJECT, locally UNdetected, FO re-enc caught */
    FC_OUT_TIMEOUT,         /* availability loss (channel/protocol layer)          */
    FC_OUT_SDC,             /* oracle NEITHER (wrong secret accepted)              */
    FC_OUT_EXCLUDED,        /* recorded but excluded from an analysis (reason req) */
    FC_OUT_INCONCLUSIVE,    /* harness-invariant violation (must be investigated)  */
    FC_OUT__COUNT
} fc_outcome_t;

/* ---- Fault event (versioned schema) ---------------------------------------- */
typedef struct {
    uint32_t schema_version;      /* must equal FC_SCHEMA_VERSION                 */
    char     model_id[32];        /* e.g. "mem.bitflip"                           */
    uint32_t model_version;
    fc_target_t target_component;
    uint32_t target_id;           /* e.g. butterfly/coefficient/byte index        */
    uint32_t phase;               /* logical phase id (experiment-defined)        */
    uint64_t seed;                /* deterministic campaign seed                  */
    uint64_t event_index;         /* deterministic event index within campaign    */
    uint64_t op_index;            /* time/operation index at injection            */
    fc_loc_kind_t location_kind;
    uint32_t location;            /* bit/byte/word offset                         */
    uint64_t mask;                /* corruption mask                              */
    fc_fault_class_t fault_class; /* CRITERION 1                                  */
    fc_duration_t duration;
    int32_t combo_group;          /* -1 standalone; >=0 = combined-fault group id  */
    uint8_t armed;                /* was a fault requested at all? (0/1)           */
    /* activation evidence, filled by the injector post-attempt (0/1 flags; NOT C
     * bool: records may be deserialized from bytes, so non-canonical values must
     * be representable without undefined behavior — see fuzz finding, L21): */
    uint8_t target_accessible;    /* eligibility                                   */
    uint8_t mutation_applied;     /* the injector performed the write/alteration   */
    uint8_t target_actually_affected;/* read-back confirms the intended change     */
} fc_event_t;

typedef struct { uint8_t detected; uint8_t claimed_recovery; uint8_t claimed_fail_stop; } fc_monitor_obs_t;

typedef struct {
    fc_event_t          event;
    fc_monitor_obs_t    monitor;      /* UNTRUSTED claims from the countermeasure  */
    fc_oracle_verdict_t oracle;       /* TRUSTED independent correctness verdict   */
    uint8_t             timed_out;    /* channel/protocol availability loss (0/1)  */
    uint8_t             excluded;     /* analyst-excluded trial (0/1)              */
    char                exclude_reason[48];
} fc_trial_t;

/* Derive injection status purely from recorded evidence. A monitor can NEVER
 * promote an ineligible/failed injection to "activated". Flags are compared !=0
 * so non-canonical serialized bytes are well-defined. */
static inline fc_injection_status_t fc_injection_status(const fc_event_t *e) {
    if (!e->armed)                return FC_INJ_NOT_ARMED;
    if (!e->target_accessible)    return FC_INJ_INELIGIBLE;
    if (!e->mutation_applied)     return FC_INJ_FAILED;
    if (!e->target_actually_affected) return FC_INJ_FAILED;
    return FC_INJ_ACTIVATED;
}

/* Terminal classification. Pure function of RECORDED facts. Key invariants:
 *   - RECOVERED is reachable only when oracle==VALID (CRITERION 3): the monitor's
 *     own "claimed_recovery" is never sufficient.
 *   - SDC is forced by oracle==NEITHER regardless of any monitor claim.
 *   - Ineligible/failed injections cannot be reported as activated outcomes.
 */
static inline fc_outcome_t fc_classify(const fc_trial_t *t) {
    if (t->excluded)
        return (t->exclude_reason[0] != '\0') ? FC_OUT_EXCLUDED : FC_OUT_INCONCLUSIVE;

    fc_injection_status_t inj = fc_injection_status(&t->event);

    if (inj == FC_INJ_INELIGIBLE) return FC_OUT_INELIGIBLE;
    if (inj == FC_INJ_FAILED)     return FC_OUT_INJECTION_FAILED;

    if (t->timed_out)             return FC_OUT_TIMEOUT;

    /* Correctness is decided ONLY by the independent oracle. */
    if (t->oracle == FC_ORACLE_NEITHER) return FC_OUT_SDC;

    if (inj == FC_INJ_NOT_ARMED) {
        if (t->oracle == FC_ORACLE_VALID) return FC_OUT_CLEAN_COMPLETED;
        return FC_OUT_INCONCLUSIVE; /* clean run that rejects / has no verdict: harness bug */
    }

    /* inj == FC_INJ_ACTIVATED from here. Detection is an ORTHOGONAL dimension and
     * is preserved in the terminal class (RECOVERED vs INEFFECTIVE; and
     * local-detected fail-stop vs FO-contained) so they are never conflated. */
    if (t->oracle == FC_ORACLE_VALID)
        return t->monitor.detected ? FC_OUT_RECOVERED : FC_OUT_INEFFECTIVE;
    if (t->oracle == FC_ORACLE_REJECT)
        return t->monitor.detected ? FC_OUT_SAFE_FAIL_DETECTED
                                   : FC_OUT_SAFE_FAIL_FO_CONTAINED;

    /* oracle UNAVAILABLE while armed+activated: cannot assert correctness. */
    return FC_OUT_INCONCLUSIVE;
}

/* ---- Trial ledger: every started trial must be finalized exactly once. ------ */
typedef struct {
    uint64_t started;
    uint64_t finalized;
    uint64_t by_outcome[FC_OUT__COUNT];
} fc_ledger_t;

static inline void fc_ledger_init(fc_ledger_t *l) { memset(l, 0, sizeof(*l)); }
static inline void fc_ledger_begin(fc_ledger_t *l) { l->started++; }
static inline void fc_ledger_record(fc_ledger_t *l, fc_outcome_t o) {
    if ((unsigned)o < (unsigned)FC_OUT__COUNT) { l->finalized++; l->by_outcome[o]++; }
}
/* Returns 0 iff accounting is complete and consistent; nonzero code otherwise. */
static inline int fc_ledger_check(const fc_ledger_t *l) {
    uint64_t sum = 0;
    for (int i = 0; i < FC_OUT__COUNT; i++) sum += l->by_outcome[i];
    if (l->started != l->finalized) return 1; /* dropped/missing trial record */
    if (sum != l->finalized)        return 2; /* counter/finalize mismatch     */
    return 0;
}

static inline const char *fc_outcome_name(fc_outcome_t o) {
    switch (o) {
        case FC_OUT_CLEAN_COMPLETED:  return "CLEAN_COMPLETED";
        case FC_OUT_INELIGIBLE:       return "INELIGIBLE";
        case FC_OUT_INJECTION_FAILED: return "INJECTION_FAILED";
        case FC_OUT_INEFFECTIVE:      return "INEFFECTIVE";
        case FC_OUT_RECOVERED:        return "RECOVERED";
        case FC_OUT_SAFE_FAIL_DETECTED:     return "SAFE_FAIL_DETECTED";
        case FC_OUT_SAFE_FAIL_FO_CONTAINED: return "SAFE_FAIL_FO_CONTAINED";
        case FC_OUT_TIMEOUT:          return "TIMEOUT";
        case FC_OUT_SDC:              return "SDC";
        case FC_OUT_EXCLUDED:         return "EXCLUDED";
        case FC_OUT_INCONCLUSIVE:     return "INCONCLUSIVE";
        default:                      return "UNKNOWN";
    }
}

static inline bool fc_event_valid(const fc_event_t *e) {
    if (e->schema_version != FC_SCHEMA_VERSION) return false;
    if ((unsigned)e->target_component >= (unsigned)FC_TGT__COUNT) return false;
    if ((unsigned)e->location_kind > (unsigned)FC_LOC_LOGICAL) return false;
    return true;
}

/* Cross-field consistency: catch internally inconsistent / malformed records
 * (CRITERION: "a malformed or internally inconsistent record fails validation").
 * Returns true iff the record is well-formed AND its evidence flags are monotone. */
static inline bool fc_trial_consistent(const fc_trial_t *t) {
    const fc_event_t *e = &t->event;
    if (!fc_event_valid(e)) return false;
    if ((unsigned)t->oracle > (unsigned)FC_ORACLE_NEITHER) return false;
    /* evidence monotonicity: affected => applied => armed; affected => accessible */
    if (e->mutation_applied        && !e->armed)             return false;
    if (e->target_actually_affected && !e->mutation_applied) return false;
    if (e->target_actually_affected && !e->target_accessible) return false;
    /* a clean (unarmed) trial must not carry activation evidence */
    if (!e->armed && (e->mutation_applied || e->target_actually_affected)) return false;
    /* exclusion requires a reason */
    if (t->excluded && t->exclude_reason[0] == '\0') return false;
    return true;
}

/* <!-- FC-APPEND --> */
#endif /* FAULT_CONTRACT_H */
