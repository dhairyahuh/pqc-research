/* combined_campaign.c — Phase 4 combined memory+channel fault coordinator.
 *
 * ONE real decapsulation path carries BOTH fault classes (resolving the Gate-0
 * obstacle): the channel fault acts on the wire ciphertext BEFORE decapsulation;
 * the memory fault (TFIB hooks) acts DURING decapsulation of the same path.
 * liboqs + standalone SHAKE remain the INDEPENDENT oracle. Deterministic; emits
 * COMBINED_SCHEMA_VERSION=1 records with memory and channel dimensions kept
 * strictly separate. Isolated Phase-2/3 runners are NOT modified.
 *
 * SCOPE: memory faults are LOGICAL_VALUE only (persistent-storage BLOCKED);
 * channel faults are a software emulator. NOT physical radiation / RF / qualification.
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

#define PK 1184
#define SK 2400
#define CT 1088
#define SS 32
#define FRAME 18
#define TAG 32
#define WIRE (CT + FRAME + TAG)
#define RETRY_MAX 2
#define DEADLINE 100
#define COMBINED_SCHEMA_VERSION 1

int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *st);
int randombytes(uint8_t *o, size_t n){ for(size_t i=0;i<n;i++) o[i]=(uint8_t)(i^0xAA); return 0; }

static uint16_t crc16(const uint8_t *d, size_t n){
    uint16_t c=0xFFFF;
    for(size_t i=0;i<n;i++){ c^=(uint16_t)(d[i]<<8);
        for(int b=0;b<8;b++) c=(c&0x8000)?(uint16_t)((c<<1)^0x1021):(uint16_t)(c<<1); }
    return c;
}
static void put_be16(uint8_t*p,uint16_t v){p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static void put_be32(uint8_t*p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}

static void build_frame(uint8_t f[FRAME], uint16_t seq){
    memcpy(f,"SPAC",4); put_be16(f+4,seq); f[6]=1; f[7]=0x10;    /* ADCS POINT_NADIR */
    put_be32(f+8,45); put_be32(f+12,60000); put_be16(f+16,crc16(f,16));
}
static int parse_frame(const uint8_t f[FRAME], uint16_t wmin, uint16_t wmax){
    if(memcmp(f,"SPAC",4)!=0) return 1;                 /* bad_magic */
    uint16_t seq=(uint16_t)((f[4]<<8)|f[5]);
    if(seq<wmin||seq>wmax) return 2;                    /* seq_out_of_window */
    if(f[6]!=1||f[7]!=0x10) return 3;                   /* bad_command */
    if(crc16(f,16)!=(uint16_t)((f[16]<<8)|f[17])) return 4; /* crc */
    return 0;                                           /* OK */
}
/* abstract keyed primitives via standalone SHAKE (documented model choice) */
static void keystream(const uint8_t ss_[SS], uint8_t *out, size_t n){
    uint8_t in[1+SS]; in[0]=0x01; memcpy(in+1,ss_,SS); fips202_ref_shake256(out,n,in,sizeof in);
}
static void mactag(const uint8_t ss_[SS], const uint8_t *enc, size_t n, uint8_t out[TAG]){
    uint8_t in[1+SS+FRAME]; in[0]=0x02; memcpy(in+1,ss_,SS); memcpy(in+1+SS,enc,n);
    fips202_ref_shake256(out,TAG,in,1+SS+n);
}
/* <!-- CB-APPEND --> */
/* channel classes */
enum { CH_CLEAN=0, CH_BIT, CH_TRUNC, CH_LOSS, CH_DELAY, CH_DUP, CH_REORDER, CH_INTERRUPT };
static const char *CH_NAME[]={"CLEAN","BIT_CORRUPTION","TRUNCATION","PACKET_LOSS","DELAY",
                              "DUPLICATION","REORDER","INTERRUPTION"};
static const char *VERD[]={"UNAVAILABLE","VALID","REJECT","NEITHER"};
enum { V_UNAVAIL=0, V_VALID, V_REJECT, V_NEITHER };
enum { K_EST=0, K_MISMATCH, K_MALFORMED, K_LOST, K_TIMEOUT };

typedef struct { int kind; int verdict; const char*effect; int mem_activated; int mem_detected; int decaps_ran; } att_t;

/* one transmission attempt. Channel acts on the wire; memory fault acts in decaps. */
static att_t one_attempt(int a, const uint8_t pk[PK], const uint8_t sk[SK],
                         const uint8_t ct_clean[CT], const uint8_t ss_ground[SS],
                         uint16_t seq, uint16_t wmin, uint16_t wmax,
                         int ch_active, int ch_class, int reorder_active,
                         int mem_active, tfib_fault_locus_t locus, unsigned stage,
                         unsigned bidx, uint8_t bit, bool mem_persist, const uint8_t pseed[16]){
    (void)a; (void)pk;
    att_t r={K_MALFORMED,V_UNAVAIL,"DELIVERED",0,0,0};
    uint16_t use_seq = (ch_active && reorder_active) ? (uint16_t)(seq-100) : seq;
    uint8_t frame[FRAME], enc[FRAME], ks[FRAME], tag[TAG];
    build_frame(frame, use_seq);
    keystream(ss_ground, ks, FRAME);
    for(int i=0;i<FRAME;i++) enc[i]=frame[i]^ks[i];
    mactag(ss_ground, enc, FRAME, tag);
    uint8_t wire[WIRE];
    memcpy(wire, ct_clean, CT); memcpy(wire+CT, enc, FRAME); memcpy(wire+CT+FRAME, tag, TAG);
    size_t wlen=WIRE; const char*eff="DELIVERED"; int latency=1;
    uint64_t rr = ((uint64_t)pseed[0]<<24)|((uint64_t)pseed[1]<<16)|((uint64_t)pseed[2]<<8)|pseed[3];
    if(ch_active){
        switch(ch_class){
            case CH_LOSS: r.kind=K_LOST; r.effect="LOST"; return r;
            case CH_INTERRUPT: r.kind=K_LOST; r.effect="LINK_DOWN"; return r;
            case CH_DELAY: latency=DEADLINE+1+(int)(rr%50); eff="DELAYED"; break;
            case CH_TRUNC: wlen=WIRE-(1+(size_t)(rr%64)); eff="TRUNCATED"; break;
            case CH_BIT: { size_t pos=rr%CT; wire[pos]^=(uint8_t)(1<<((rr>>8)&7)); eff="CORRUPTED"; } break;
            case CH_DUP: eff="DUPLICATED"; break;
            case CH_REORDER: eff="REORDERED"; break;
            default: break;
        }
    }
    r.effect=eff;
    if(latency>DEADLINE){ r.kind=K_TIMEOUT; r.effect="DELAYED"; return r; }
    if(wlen < (size_t)WIRE){ r.kind=K_MALFORMED; return r; }   /* truncation */
    const uint8_t *ct2=wire, *enc2=wire+CT, *tag2=wire+CT+FRAME;
    /* ---- decapsulation of delivered ct2, with memory fault armed as configured ---- */
    tfib_fault_reset(); tfib_reset_all_stats();
    if(mem_active && locus!=TFIB_FAULT_NONE) tfib_fault_arm(locus,stage,bidx,bit,mem_persist);
    uint8_t ss_sc[SS]; uint32_t st=0;
    r.decaps_ran=1;
    (void)mlkem768_dec_monitored(ss_sc, ct2, sk, &st);
    r.mem_activated = (g_tfib_fault.trigger_count>0)?1:0;
    r.mem_detected  = (tfib_get_total_mismatches()>0)?1:0;
    uint8_t ss_rej[SS]; independent_oracle_compute_rejection(ss_rej, sk, ct2);
    r.verdict = (memcmp(ss_sc,ss_ground,SS)==0)?V_VALID : (memcmp(ss_sc,ss_rej,SS)==0?V_REJECT:V_NEITHER);
    uint8_t tagc[TAG]; mactag(ss_sc, enc2, FRAME, tagc);
    if(memcmp(tagc,tag2,TAG)!=0){ r.kind=K_MISMATCH; return r; }   /* MAC fail = detected mismatch */
    uint8_t ks2[FRAME], pt[FRAME]; keystream(ss_sc,ks2,FRAME);
    for(int i=0;i<FRAME;i++) pt[i]=enc2[i]^ks2[i];
    r.kind = (parse_frame(pt,wmin,wmax)==0)? K_EST : K_MALFORMED;
    return r;
}
/* <!-- CB-APPEND2 --> */
#define BASE_SEQ 5020
static const char *OUT_NAME[]={"KEY_ESTABLISHED","RECOVERED_ON_RETRY","PROTOCOL_ABORT",
                               "MALFORMED_MESSAGE","MESSAGE_LOST","TIMEOUT_RETRY_EXHAUSTED","INCONCLUSIVE"};
enum { O_EST=0,O_REC,O_ABORT,O_MALF,O_LOST,O_TIMEOUT,O_INC };

static void prf_bytes(const char*dom,uint64_t a,uint64_t b,uint64_t c,uint8_t*out,size_t n){
    uint8_t ctx[32]; size_t L=0; size_t dl=strlen(dom);
    for(size_t i=0;i<dl&&i<8;i++) ctx[L++]=(uint8_t)dom[i];
    uint64_t v[3]={a,b,c};
    for(int k=0;k<3;k++) for(int s=56;s>=0;s-=8) ctx[L++]=(uint8_t)(v[k]>>s);
    fips202_ref_shake256(out,n,ctx,L);
}

typedef struct {
    int outcome; int established; int retry_count; int crypto;
    int mem_activated; int mem_detected; const char*channel_effect; int excluded; const char*mem_status;
} cond_rec_t;

static cond_rec_t run_condition(uint64_t gseed, int condid,
        const uint8_t pk[PK], const uint8_t sk[SK], const uint8_t ct_clean[CT],
        const uint8_t ss_ground[SS], uint16_t seq,
        int mem_on, tfib_fault_locus_t locus, unsigned stage, unsigned bidx, uint8_t bit, bool mem_persist,
        int ch_on, int ch_class, bool ch_persist){
    uint16_t wmin=(uint16_t)(seq-2), wmax=(uint16_t)(seq+32);
    int terminal=-1, crypto=V_UNAVAIL, attempts=0, mem_act=0, mem_det=0, last=K_MALFORMED, mem_decaps=0;
    const char*first_eff="DELIVERED";
    for(int a=0;a<=RETRY_MAX;a++){
        attempts++;
        int ch_active = ch_on && (ch_persist || a==0);
        int mem_active = mem_on && (mem_persist || a==0);
        int reorder = ch_active && ch_class==CH_REORDER;
        uint8_t pseed[16]; prf_bytes("chan",gseed,(uint64_t)condid,(uint64_t)a,pseed,16);
        att_t r = one_attempt(a,pk,sk,ct_clean,ss_ground,seq,wmin,wmax,
                              ch_active,ch_class,reorder,mem_active,locus,stage,bidx,bit,mem_persist,pseed);
        if(a==0) first_eff=r.effect;
        if(mem_active && r.decaps_ran) mem_decaps=1;
        mem_act|=r.mem_activated; mem_det|=r.mem_detected; crypto=r.verdict; last=r.kind;
        if(r.kind==K_EST){ terminal=(a>0)?O_REC:O_EST; break; }
    }
    if(terminal<0){
        terminal = (last==K_LOST)?O_LOST : (last==K_TIMEOUT)?O_TIMEOUT :
                   (last==K_MALFORMED)?O_MALF : (last==K_MISMATCH)?O_ABORT : O_INC;
    }
    cond_rec_t c; c.outcome=terminal; c.established=(terminal==O_EST||terminal==O_REC);
    c.retry_count=attempts-1; c.crypto=crypto; c.mem_activated=mem_act; c.mem_detected=mem_det;
    c.channel_effect=first_eff;
    /* memory status: a fault that never activated BECAUSE the channel blocked delivery is a
     * legitimate MASKING interaction (retained), NOT an injection failure (excluded). */
    c.mem_status = !mem_on ? "NOT_ARMED" : (mem_act ? "ACTIVATED" :
                   (mem_decaps ? "FAILED" : "MASKED_BY_CHANNEL"));
    c.excluded = (mem_on && mem_decaps && !mem_act) ? 1 : 0;   /* true injection failure only */
    return c;
}
/* <!-- CB-APPEND3 --> */
static const char *CFG_NAME[]={"BASELINE","TFIB_REF","TFIB_META"};
static const char *LOC_NAME(tfib_fault_locus_t l){
    return l==TFIB_FAULT_OP_TWIDDLE?"OP_TWIDDLE":l==TFIB_FAULT_REF_TWIDDLE?"REF_TWIDDLE":
           l==TFIB_FAULT_META_TAG?"META_TAG":l==TFIB_FAULT_CHECKER_LOGIC?"CHECKER_LOGIC":"NONE";
}
static FILE *g_fp; static long g_started=0,g_final=0,g_inc=0,g_excl=0;

static void emit(uint64_t gseed,const char*cond,const char*cfg,tfib_fault_locus_t loc,bool mdur,
                 int mem_on,int ch_class,bool chp,int ch_on,cond_rec_t r){
    g_started++; g_final++; if(r.outcome==O_INC) g_inc++; if(r.excluded) g_excl++;
    fprintf(g_fp,
      "{\"seed\":%llu,\"condition\":\"%s\",\"schema_version\":%d,\"config\":\"%s\","
      "\"mem_locus\":\"%s\",\"mem_duration\":\"%s\",\"mem_armed\":%d,\"mem_activated\":%d,\"mem_detected\":%d,"
      "\"mem_injection_status\":\"%s\","
      "\"channel_class\":\"%s\",\"channel_persistent\":%d,\"channel_armed\":%d,\"channel_effect\":\"%s\","
      "\"crypto_verdict\":\"%s\",\"protocol_outcome\":\"%s\",\"established\":%d,\"retry_count\":%d,\"excluded\":%d}\n",
      (unsigned long long)gseed,cond,COMBINED_SCHEMA_VERSION,cfg,LOC_NAME(loc),mdur?"PERSISTENT":"TRANSIENT",
      mem_on,r.mem_activated,r.mem_detected,r.mem_status,
      CH_NAME[ch_class],chp?1:0,ch_on,r.channel_effect,
      VERD[r.crypto],OUT_NAME[r.outcome],r.established,r.retry_count,r.excluded);
}

static void run_seed(uint64_t g){
    uint8_t seed64[64],seed32[32],pk[PK],sk[SK],ct[CT],ssg[SS];
    prf_bytes("kemkp",g,0,0,seed64,64); prf_bytes("kemenc",g,0,0,seed32,32);
    independent_oracle_keypair_derand(pk,sk,seed64);
    independent_oracle_encaps_derand(ct,ssg,pk,seed32);
    uint16_t seq=(uint16_t)(BASE_SEQ+(g%10));
    uint8_t dm[8],dc[8]; prf_bytes("fmem",g,0,0,dm,8); prf_bytes("fchan",g,0,0,dc,8);
    int cfg=dm[0]%3; tfib_mode_t mode=cfg==0?TFIB_MODE_BASELINE:cfg==1?TFIB_MODE_REF:TFIB_MODE_META;
    tfib_fault_locus_t locset_ref[3]={TFIB_FAULT_OP_TWIDDLE,TFIB_FAULT_REF_TWIDDLE,TFIB_FAULT_CHECKER_LOGIC};
    tfib_fault_locus_t locset_meta[3]={TFIB_FAULT_OP_TWIDDLE,TFIB_FAULT_META_TAG,TFIB_FAULT_CHECKER_LOGIC};
    tfib_fault_locus_t loc = cfg==0?TFIB_FAULT_OP_TWIDDLE:(cfg==1?locset_ref[dm[1]%3]:locset_meta[dm[1]%3]);
    bool mdur=(dm[2]&1); unsigned stage=(unsigned)(g%7)+1,bidx=(unsigned)((g*17)%128); uint8_t bit=(uint8_t)(g%15)+1;
    int chcls=1+(dc[0]%7); bool chp=(dc[1]&1);
    tfib_set_mode(mode);
    cond_rec_t c00=run_condition(g,0,pk,sk,ct,ssg,seq, 0,TFIB_FAULT_NONE,stage,bidx,bit,mdur, 0,CH_CLEAN,false);
    cond_rec_t c10=run_condition(g,1,pk,sk,ct,ssg,seq, 1,loc,stage,bidx,bit,mdur, 0,CH_CLEAN,false);
    cond_rec_t c01=run_condition(g,2,pk,sk,ct,ssg,seq, 0,TFIB_FAULT_NONE,stage,bidx,bit,mdur, 1,chcls,chp);
    cond_rec_t c11=run_condition(g,3,pk,sk,ct,ssg,seq, 1,loc,stage,bidx,bit,mdur, 1,chcls,chp);
    emit(g,"C00",CFG_NAME[cfg],TFIB_FAULT_NONE,mdur,0,CH_CLEAN,false,0,c00);
    emit(g,"C10",CFG_NAME[cfg],loc,mdur,1,CH_CLEAN,false,0,c10);
    emit(g,"C01",CFG_NAME[cfg],TFIB_FAULT_NONE,mdur,0,chcls,chp,1,c01);
    emit(g,"C11",CFG_NAME[cfg],loc,mdur,1,chcls,chp,1,c11);
}

int main(int argc,char**argv){
    if(independent_oracle_init()!=0){ fprintf(stderr,"oracle init failed\n"); return 1; }
    const char*out=(argc>1)?argv[1]:"research/results/phase4_combined_v1/raw.jsonl";
    long N=(argc>3&&strcmp(argv[2],"--pilot")==0)?atol(argv[3]):500;
    g_fp=fopen(out,"w"); if(!g_fp){ perror("fopen"); return 1; }
    for(long i=0;i<N;i++) run_seed((uint64_t)i);
    fclose(g_fp);
    printf("seeds=%ld trials=%ld finalized=%ld inconclusive=%ld excluded=%ld\n",
           N,g_started,g_final,g_inc,g_excl);
    printf("wrote %s\n",out);
    return (g_started==g_final && g_inc==0)?0:3;
}



