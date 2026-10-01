CC = clang
CFLAGS = -O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include
LDFLAGS = -L/opt/homebrew/lib -loqs

BIN_DIR = bin
OBJ_DIR = bin/obj

all: $(BIN_DIR)/ml_kem_harness $(BIN_DIR)/ml_dsa_harness $(BIN_DIR)/test_interop $(BIN_DIR)/test_fips_kats $(BIN_DIR)/mlkem768_internal_fault_experiment

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

# Path A C baseline harnesses
$(BIN_DIR)/ml_kem_harness: algorithms/ml-kem/ml_kem_harness.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

$(BIN_DIR)/ml_dsa_harness: algorithms/ml-dsa/ml_dsa_harness.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

# Path B Objects (Clean reference for interop)
$(OBJ_DIR)/mlkem768.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768 -c $< -o $@

$(OBJ_DIR)/mldsa65.o: algorithms/source_ref/mldsa/mldsa_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa -DMLD_CONFIG_PARAMETER_SET=65 -c $< -o $@

# Path B Multi-Level Objects for FIPS 203 & 204 KAT Verification
$(OBJ_DIR)/mlkem512.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem512 -DMLK_CONFIG_PARAMETER_SET=512 -c $< -o $@

$(OBJ_DIR)/mlkem768_kat.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 -c $< -o $@

$(OBJ_DIR)/mlkem1024.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem1024 -DMLK_CONFIG_PARAMETER_SET=1024 -c $< -o $@

$(OBJ_DIR)/mldsa44.o: algorithms/source_ref/mldsa/mldsa_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa44 -DMLD_CONFIG_PARAMETER_SET=44 -c $< -o $@

$(OBJ_DIR)/mldsa65_kat.o: algorithms/source_ref/mldsa/mldsa_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa65 -DMLD_CONFIG_PARAMETER_SET=65 -c $< -o $@

$(OBJ_DIR)/mldsa87.o: algorithms/source_ref/mldsa/mldsa_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa87 -DMLD_CONFIG_PARAMETER_SET=87 -c $< -o $@

# Path B Objects (Instrumented with fault hooks)
$(OBJ_DIR)/mlkem_fault_hooks.o: algorithms/source_ref/mlkem_fault_hooks.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mlkem768_instrumented.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

# Path A vs Path B Cross-Validation binary
$(BIN_DIR)/test_interop: tests/test_interop_path_a_b.c $(OBJ_DIR)/mlkem768.o $(OBJ_DIR)/mldsa65.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I algorithms/source_ref/mlkem -I algorithms/source_ref/mldsa $^ -o $@ $(LDFLAGS)

# Comprehensive NIST FIPS 203 & 204 KAT Runner (ML-KEM-512/768/1024 & ML-DSA-44/65/87)
$(BIN_DIR)/test_fips_kats: tests/test_fips_kats.c tests/kat_mlkem512.c tests/kat_mlkem768.c tests/kat_mlkem1024.c tests/kat_mldsa44.c tests/kat_mldsa65.c tests/kat_mldsa87.c $(OBJ_DIR)/mlkem512.o $(OBJ_DIR)/mlkem768_kat.o $(OBJ_DIR)/mlkem1024.o $(OBJ_DIR)/mldsa44.o $(OBJ_DIR)/mldsa65_kat.o $(OBJ_DIR)/mldsa87.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem -I algorithms/source_ref/mldsa $^ -o $@

# Phase 4B Internal Fault Experiment Binary
$(BIN_DIR)/mlkem768_internal_fault_experiment: experiments/fault_injection/mlkem768_internal_fault_experiment.c $(OBJ_DIR)/mlkem768_instrumented.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@

# Phase 2 Multi-Level Instrumented Objects (ML-KEM-512, ML-KEM-768, ML-KEM-1024)
$(OBJ_DIR)/mlkem512_inst.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem512 -DMLK_CONFIG_PARAMETER_SET=512 -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mlkem768_inst.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mlkem1024_inst.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem1024 -DMLK_CONFIG_PARAMETER_SET=1024 -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

# Phase 2 Comprehensive Campaign Runner Binary
$(BIN_DIR)/mlkem_campaign_runner: experiments/mlkem/mlkem_campaign_runner.c $(OBJ_DIR)/mlkem512_inst.o $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem1024_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

# Phase 3 Multi-Level Instrumented Objects (ML-DSA-44, ML-DSA-65, ML-DSA-87)
$(OBJ_DIR)/mldsa_fault_hooks.o: algorithms/source_ref/mldsa_fault_hooks.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLDSA_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mldsa44_inst.o: algorithms/source_ref/mldsa/mldsa_native.c algorithms/source_ref/mldsa/src/poly.c algorithms/source_ref/mldsa/src/sign.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa44 -DMLD_CONFIG_PARAMETER_SET=44 -DMLDSA_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mldsa65_inst.o: algorithms/source_ref/mldsa/mldsa_native.c algorithms/source_ref/mldsa/src/poly.c algorithms/source_ref/mldsa/src/sign.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa65 -DMLD_CONFIG_PARAMETER_SET=65 -DMLDSA_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mldsa87_inst.o: algorithms/source_ref/mldsa/mldsa_native.c algorithms/source_ref/mldsa/src/poly.c algorithms/source_ref/mldsa/src/sign.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa87 -DMLD_CONFIG_PARAMETER_SET=87 -DMLDSA_RESEARCH_FAULT_HOOKS -c $< -o $@

# Phase 3 Comprehensive Campaign Runner Binary
$(BIN_DIR)/mldsa_campaign_runner: experiments/mldsa/mldsa_campaign_runner.c $(OBJ_DIR)/mldsa44_inst.o $(OBJ_DIR)/mldsa65_inst.o $(OBJ_DIR)/mldsa87_inst.o $(OBJ_DIR)/mldsa_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mldsa $^ -o $@ $(LDFLAGS)

# Phase 5 Cross-Implementation ML-KEM Experiment
$(BIN_DIR)/phase5_mlkem: experiments/phase5/phase5_mlkem_cross_impl.c $(OBJ_DIR)/mlkem768.o $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

# Phase 5 Cross-Implementation ML-DSA Experiment
$(BIN_DIR)/phase5_mldsa: experiments/phase5/phase5_mldsa_cross_impl.c $(OBJ_DIR)/mldsa65.o $(OBJ_DIR)/mldsa65_inst.o $(OBJ_DIR)/mldsa_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mldsa $^ -o $@ $(LDFLAGS)

# Phase 5 Compiler Sensitivity Tests (multiple optimization levels)
$(OBJ_DIR)/mlkem768_inst_O0.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O0 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mlkem_fault_hooks_O0.o: algorithms/source_ref/mlkem_fault_hooks.c | $(OBJ_DIR)
	$(CC) -O0 -std=c99 -I algorithms/source_ref/mlkem -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

$(BIN_DIR)/phase5_compiler_O0: experiments/phase5/compiler_sensitivity_test.c $(OBJ_DIR)/mlkem768_inst_O0.o $(OBJ_DIR)/mlkem_fault_hooks_O0.o | $(BIN_DIR)
	$(CC) -O0 -Wall -std=c11 -I . -I algorithms/source_ref/mlkem $^ -o $@

$(BIN_DIR)/phase5_compiler_O3: experiments/phase5/compiler_sensitivity_test.c $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) -O3 -Wall -std=c11 -I . -I algorithms/source_ref/mlkem $^ -o $@

phase5: $(BIN_DIR)/phase5_mlkem $(BIN_DIR)/phase5_mldsa $(BIN_DIR)/phase5_compiler_O0 $(BIN_DIR)/phase5_compiler_O3

clean:
	rm -rf $(BIN_DIR)

test: all
	@echo "\n=== Running Path A ML-KEM Harness ==="
	./$(BIN_DIR)/ml_kem_harness
	@echo "\n=== Running Path A ML-DSA Harness ==="
	./$(BIN_DIR)/ml_dsa_harness
	@echo "\n=== Running Path A vs Path B Interoperability Test ==="
	./$(BIN_DIR)/test_interop
	@echo "\n=== Running Comprehensive NIST FIPS 203 & 204 KAT Verification ==="
	./$(BIN_DIR)/test_fips_kats
	@echo "\n=== Running Phase 4B Internal Fault Experiment ==="
	./$(BIN_DIR)/mlkem768_internal_fault_experiment

test-phase5: phase5
	@echo "\n=== Phase 5: ML-KEM Cross-Implementation ==="
	./$(BIN_DIR)/phase5_mlkem
	@echo "\n=== Phase 5: ML-DSA Cross-Implementation ==="
	./$(BIN_DIR)/phase5_mldsa
	@echo "\n=== Phase 5: Compiler Sensitivity -O0 ==="
	./$(BIN_DIR)/phase5_compiler_O0 O0
	@echo "\n=== Phase 5: Compiler Sensitivity -O3 ==="
	./$(BIN_DIR)/phase5_compiler_O3 O3

# Phase 6 Targeted Resilience Prototyping
$(BIN_DIR)/phase6_resilience: experiments/phase6/phase6_resilience_harness.c $(OBJ_DIR)/mlkem768.o $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o $(OBJ_DIR)/mldsa65.o $(OBJ_DIR)/mldsa65_inst.o $(OBJ_DIR)/mldsa_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem -I algorithms/source_ref/mldsa $^ -o $@ $(LDFLAGS)

phase6: $(BIN_DIR)/phase6_resilience

test-phase6: phase6
	@echo "\n=== Phase 6: Targeted Software Resilience Evaluation ==="
	./$(BIN_DIR)/phase6_resilience

# Phase 6B Independent Validation and Robustness Audit
$(BIN_DIR)/phase6b_audit: experiments/phase6b/phase6b_adversarial_audit.c $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

phase6b: $(BIN_DIR)/phase6b_audit

test-phase6b: phase6b
	@echo "\n=== Phase 6B: Independent Adversarial Validation & Robustness Audit ==="
	./$(BIN_DIR)/phase6b_audit

# Phase 7 Targeted Layered Resilience Engineering
$(BIN_DIR)/phase7_layered: experiments/phase7/phase7_layered_resilience.c $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

phase7: $(BIN_DIR)/phase7_layered

test-phase7: phase7
	@echo "\n=== Phase 7: Targeted Layered Fault-Resilience Evaluation ==="
	./$(BIN_DIR)/phase7_layered

# Phase 7B Independent Validation and Claim Reconciliation
$(BIN_DIR)/phase7b_validation: experiments/phase7b/independent_validation_harness.c $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

phase7b: $(BIN_DIR)/phase7b_validation

test-phase7b: phase7b
	@echo "\n=== Phase 7B: Independent Validation & Claim Reconciliation ==="
	./$(BIN_DIR)/phase7b_validation

# Phase 7C Oracle-Free Native Decapsulation Monitoring
$(BIN_DIR)/phase7c_oracle_free: experiments/phase7c/phase7c_oracle_free_harness.c $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

phase7c: $(BIN_DIR)/phase7c_oracle_free

test-phase7c: phase7c
	@echo "\n=== Phase 7C: Oracle-Free Native Decapsulation Monitoring ==="
	./$(BIN_DIR)/phase7c_oracle_free

# Phase 7D Adversarial Validation and Common-Mode Fault Analysis
$(BIN_DIR)/phase7d_adversarial: experiments/phase7d/phase7d_adversarial_harness.c $(OBJ_DIR)/mlkem768_inst.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@ $(LDFLAGS)

phase7d: $(BIN_DIR)/phase7d_adversarial

test-phase7d: phase7d
	@echo "\n=== Phase 7D: Adversarial Validation & Reproducibility Audit ==="
	./$(BIN_DIR)/phase7d_adversarial

.PHONY: all clean test phase5 test-phase5 phase6 test-phase6 phase6b test-phase6b phase7 test-phase7 phase7b test-phase7b phase7c test-phase7c phase7d test-phase7d
