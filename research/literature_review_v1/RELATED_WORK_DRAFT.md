# Related Work (manuscript-ready draft) — Phase 6

> Status: DRAFT for insertion into `MANUSCRIPT.md` **after authorization**. Cites only sources whose
> host page was fetched this session, except where explicitly marked *(metadata provisional)* or
> *(tooling)*. A systematic review remains outstanding; this section must not be read as exhaustive.
> Citation keys refer to `BIBLIOGRAPHY.md`.

## Related work

**Fault attacks on lattice KEMs.** A substantial body of work shows that single, precisely placed
faults can break the CCA security of Fujisaki–Okamoto (FO) based lattice KEMs. Pessl and Prokop
demonstrate key recovery from a single instruction-skipping fault in the decoding step of
decapsulation (TCHES 2021). Xagawa et al. show that skipping the FO equality test compromises Kyber
and other Round-3 KEMs (ASIACRYPT 2021). Hermelink, Pessl, and Pöppelmann combine a ciphertext
bit-flip with a corrective fault to use FO as a decryption-failure oracle (INDOCRYPT 2021); Ravi et
al. survey side-channel and fault chosen-ciphertext attacks and countermeasures *(metadata
provisional)*. These works are **adversarial**: faults are tools for key recovery, typically modeled
at the physical/instruction level. Our study differs in intent and model — it **measures resilience/
availability** under *logical-value* faults rather than mounting an attack — and therefore does not
claim to extend this attack literature.

**Detecting and defending the FO check.** Because the FO re-encryption/equality check is security-
critical but not functionally necessary, a faulty implementation can silently omit it. Glabush,
Günther, Hövelmanns, and Stebila propose *verifiable decapsulation*, binding the check to
functionality so that omission also fails correctness tests, and note a real HQC implementation that
omitted re-encryption unnoticed for 19 months (CRYPTO 2025). Our work is complementary and
operational: rather than a construction-level guarantee, we enforce a *measurement* discipline in
which detection and recovery are credited only against an independent oracle, and "recovery" under
logical-value faults is reported as structural.

**Network and protocol disruption.** Network-impairment emulation — loss, delay, duplication,
reordering, corruption — is standard practice (e.g., Linux `tc-netem`) *(tooling)*, and
distributed-systems fault testing such as Jepsen injects partitions, crashes, and clock skew while
checking consistency *(tooling)*. We reuse these impairment mechanisms in a deterministic in-process
emulator around ML-KEM key establishment, with the distinction that we keep the protocol outcome
strictly separate from the cryptographic verdict and use a retry that redraws the channel so that
recovery is not tautological.

**Cross-layer fault interactions.** Formal treatments of *combined* faults exist for physical fault
plus physical probing, and cross-layer post-quantum analyses consider per-layer algorithm
vulnerability across the network stack *(preprint; abstract only)*. Within the literature we
reviewed we did not find a matched experiment crossing *in-decapsulation computation faults* with
*channel/protocol faults* on a KEM. We therefore position our combined experiment as, to our
knowledge within the reviewed sources, a new cross-layer design — while explicitly cautioning that
our search was not systematic and that the general notion of *fault masking/derating* is well known
in dependability engineering; our contribution is the specific instantiation and the methodological
caution that channel masking of a computation fault must not be scored as recovery.

> **OUTSTANDING (do not remove before submission):** systematic cross-layer and dependability-masking
> search; verification of all *(metadata provisional)* citations; full bibliographic fields for the
> tooling references. See `SEARCH_LOG.md` and `NOVELTY_AUDIT.md`.
