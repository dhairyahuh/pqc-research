CC = clang
CFLAGS = -O3 -Wall -Wextra -I. -I/opt/homebrew/opt/liboqs/include -I../../
LDFLAGS = -L/opt/homebrew/opt/liboqs/lib -loqs

all: libindependent_oracle.a test_independent_oracle

fips202_ref.o: fips202_ref.c fips202_ref.h
	$(CC) $(CFLAGS) -c fips202_ref.c -o fips202_ref.o

independent_oracle.o: independent_oracle.c independent_oracle.h fips202_ref.h
	$(CC) $(CFLAGS) -c independent_oracle.c -o independent_oracle.o

libindependent_oracle.a: independent_oracle.o fips202_ref.o
	ar rcs libindependent_oracle.a independent_oracle.o fips202_ref.o

test_independent_oracle: test_independent_oracle.c libindependent_oracle.a
	$(CC) $(CFLAGS) test_independent_oracle.c libindependent_oracle.a $(LDFLAGS) -o test_independent_oracle

clean:
	rm -f *.o *.a test_independent_oracle kat_validation_results.json

.PHONY: all clean
