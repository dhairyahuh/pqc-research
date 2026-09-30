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

# Path B Objects (Clean reference)
$(OBJ_DIR)/mlkem768.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768 -c $< -o $@

$(OBJ_DIR)/mldsa65.o: algorithms/source_ref/mldsa/mldsa_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa -DMLD_CONFIG_PARAMETER_SET=65 -c $< -o $@

# Path B Objects (Instrumented with fault hooks)
$(OBJ_DIR)/mlkem_fault_hooks.o: algorithms/source_ref/mlkem_fault_hooks.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

$(OBJ_DIR)/mlkem768_instrumented.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS -c $< -o $@

# Path A vs Path B Cross-Validation binary
$(BIN_DIR)/test_interop: tests/test_interop_path_a_b.c $(OBJ_DIR)/mlkem768.o $(OBJ_DIR)/mldsa65.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I algorithms/source_ref/mlkem -I algorithms/source_ref/mldsa $^ -o $@ $(LDFLAGS)

# Reproducible NIST FIPS 203 KAT Runner
$(BIN_DIR)/test_fips_kats: tests/test_fips_kats.c $(OBJ_DIR)/mlkem768.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@

# Phase 4B Internal Fault Experiment Binary
$(BIN_DIR)/mlkem768_internal_fault_experiment: experiments/fault_injection/mlkem768_internal_fault_experiment.c $(OBJ_DIR)/mlkem768_instrumented.o $(OBJ_DIR)/mlkem_fault_hooks.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem $^ -o $@

clean:
	rm -rf $(BIN_DIR)

test: all
	@echo "\n=== Running Path A ML-KEM Harness ==="
	./$(BIN_DIR)/ml_kem_harness
	@echo "\n=== Running Path A ML-DSA Harness ==="
	./$(BIN_DIR)/ml_dsa_harness
	@echo "\n=== Running Path A vs Path B Interoperability Test ==="
	./$(BIN_DIR)/test_interop
	@echo "\n=== Running NIST FIPS KAT Verification ==="
	./$(BIN_DIR)/test_fips_kats
	@echo "\n=== Running Phase 4B Internal Fault Experiment ==="
	./$(BIN_DIR)/mlkem768_internal_fault_experiment

.PHONY: all clean test
