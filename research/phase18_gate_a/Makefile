# Makefile for Phase 18H Gate A: Vector Preflight & Oracle Validation

CC ?= clang
CFLAGS ?= -O3 -std=c99 -Wall -Wextra -Wno-unused-parameter
INCLUDES = -I ../../algorithms/source_ref/mlkem \
           -I ../../tfib_experiments/phase11_oracle \
           -I /opt/homebrew/include \
           -I ../../

LDFLAGS = -L /opt/homebrew/lib -loqs
DEFS = -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768

SRCS = validate_vectors.c \
       ../../algorithms/source_ref/mlkem/mlkem_native.c \
       ../../tfib_experiments/phase11_oracle/fips202_ref.c \
       ../../tfib_experiments/phase11_oracle/independent_oracle.c

TARGET = validate_vectors

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $(DEFS) $(INCLUDES) $(SRCS) -o $@ $(LDFLAGS)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all run clean
