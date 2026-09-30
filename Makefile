CC = clang
CFLAGS = -O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include
LDFLAGS = -L/opt/homebrew/lib -loqs

BIN_DIR = bin

all: $(BIN_DIR)/ml_kem_harness $(BIN_DIR)/ml_dsa_harness

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/ml_kem_harness: algorithms/ml-kem/ml_kem_harness.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

$(BIN_DIR)/ml_dsa_harness: algorithms/ml-dsa/ml_dsa_harness.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR)

test: all
	@echo "\n=== Running ML-KEM Harness ==="
	./$(BIN_DIR)/ml_kem_harness
	@echo "\n=== Running ML-DSA Harness ==="
	./$(BIN_DIR)/ml_dsa_harness

.PHONY: all clean test
