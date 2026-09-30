cmake_minimum_required(VERSION 3.20)
project(pqc_fault_resilience C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

find_path(LIBOQS_INCLUDE_DIR oqs/oqs.h
    PATHS /opt/homebrew/include /usr/local/include
)

find_library(LIBOQS_LIBRARY NAMES oqs
    PATHS /opt/homebrew/lib /usr/local/lib
)

if (NOT LIBOQS_INCLUDE_DIR OR NOT LIBOQS_LIBRARY)
    message(FATAL_ERROR "liboqs not found. Install via 'brew install liboqs' or build from source.")
endif()

message(STATUS "Found liboqs include: ${LIBOQS_INCLUDE_DIR}")
message(STATUS "Found liboqs library: ${LIBOQS_LIBRARY}")

include_directories(${LIBOQS_INCLUDE_DIR})

add_executable(ml_kem_harness algorithms/ml-kem/ml_kem_harness.c)
target_link_libraries(ml_kem_harness PRIVATE ${LIBOQS_LIBRARY})

add_executable(ml_dsa_harness algorithms/ml-dsa/ml_dsa_harness.c)
target_link_libraries(ml_dsa_harness PRIVATE ${LIBOQS_LIBRARY})
