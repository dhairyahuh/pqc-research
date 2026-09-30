"""
Deterministic Software Fault Injection Engine for PQC Research.
Performs bounds-checked, reproducible memory and buffer corruptions.
"""

import random
from typing import Tuple, List, Union
from fault_injection.fault_models.fault_definitions import FaultClass, FaultDescriptor


class FaultInjectorEngine:
    """
    Executes controlled fault injections into byte buffers representing
    cryptographic keys, ciphertexts, signatures, and serialized objects.
    """

    @staticmethod
    def inject_seu_bit_flip(data: bytes, byte_index: int, bit_index: int) -> bytes:
        """Flips exactly 1 bit at (byte_index, bit_index)."""
        if byte_index < 0 or byte_index >= len(data):
            raise IndexError(f"Byte index {byte_index} out of bounds for buffer of size {len(data)}")
        if bit_index < 0 or bit_index > 7:
            raise ValueError(f"Bit index {bit_index} must be in range [0, 7]")

        buf = bytearray(data)
        buf[byte_index] ^= (1 << bit_index)
        return bytes(buf)

    @staticmethod
    def inject_multi_bit_flip(data: bytes, bit_coordinates: List[Tuple[int, int]]) -> bytes:
        """Flips multiple independent bits specified as list of (byte_index, bit_index)."""
        buf = bytearray(data)
        for byte_idx, bit_idx in bit_coordinates:
            if 0 <= byte_idx < len(buf) and 0 <= bit_idx <= 7:
                buf[byte_idx] ^= (1 << bit_idx)
        return bytes(buf)

    @staticmethod
    def inject_burst_corruption(data: bytes, start_byte: int, burst_len: int, seed: int) -> bytes:
        """Injects a contiguous multi-byte corruption pattern using deterministic PRNG."""
        if start_byte < 0 or start_byte >= len(data):
            raise IndexError(f"Start byte {start_byte} out of bounds for size {len(data)}")

        buf = bytearray(data)
        end_byte = min(len(buf), start_byte + burst_len)
        rng = random.Random(seed)

        for i in range(start_byte, end_byte):
            mask = rng.randint(1, 255)
            buf[i] ^= mask
        return bytes(buf)

    @staticmethod
    def inject_byte_corruption(data: bytes, byte_index: int, xor_mask: int = 0xFF) -> bytes:
        """Applies a specific XOR mask to a target byte."""
        if byte_index < 0 or byte_index >= len(data):
            raise IndexError(f"Byte index {byte_index} out of bounds for size {len(data)}")

        buf = bytearray(data)
        buf[byte_index] ^= (xor_mask & 0xFF)
        return bytes(buf)

    @staticmethod
    def inject_truncation(data: bytes, truncated_len: int) -> bytes:
        """Truncates buffer to specified length."""
        if truncated_len >= len(data) or truncated_len < 0:
            raise ValueError(f"Truncated length {truncated_len} must be strictly less than {len(data)}")
        return data[:truncated_len]
