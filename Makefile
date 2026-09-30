CC = clang
CFLAGS = -O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include
LDFLAGS = -L/opt/homebrew/lib -loqs

BIN_DIR = bin
OBJ_DIR = bin/obj

all: $(BIN_DIR)/ml_kem_harness $(BIN_DIR)/ml_dsa_harness $(BIN_DIR)/test_interop

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

# Path A C baseline harnesses
$(BIN_DIR)/ml_kem_harness: algorithms/ml-kem/ml_kem_harness.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

$(BIN_DIR)/ml_dsa_harness: algorithms/ml-dsa/ml_dsa_harness.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

# Path B Objects
$(OBJ_DIR)/mlkem768.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768 -c $< -o $@

$(OBJ_DIR)/mldsa65.o: algorithms/source_ref/mldsa/mldsa_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mldsa -DMLD_CONFIG_NAMESPACE_PREFIX=mldsa -DMLD_CONFIG_PARAMETER_SET=65 -c $< -o $@

# Path A vs Path B Cross-Validation binary
$(BIN_DIR)/test_interop: tests/test_interop_path_a_b.c $(OBJ_DIR)/mlkem768.o $(OBJ_DIR)/mldsa65.o | $(BIN_DIR)
	$(CC) $(CFLAGS) -I algorithms/source_ref/mlkem -I algorithms/source_ref/mldsa $^ -o $@ $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR)

test: all
	@echo "\n=== Running Path A ML-KEM Harness ==="
	./$(BIN_DIR)/ml_kem_harness
	@echo "\n=== Running Path A ML-DSA Harness ==="
	./$(BIN_DIR)/ml_dsa_harness
	@echo "\n=== Running Path A vs Path B Interoperability Test ==="
	./$(BIN_DIR)/test_interop

.PHONY: all clean test
