"""ASTRA-Sec: Lightweight Canonical CBOR (RFC 8949) Encoder and Decoder.

Implements deterministic canonical CBOR serialization for RFC 9171 (BPv7)
Primary, Payload, and Extension Blocks without external dependencies.
"""

import struct
from typing import Any, List, Tuple, Union


class CborError(Exception):
    """Base exception for CBOR encoding/decoding errors."""


class CborEncoder:
    """Encodes Python primitives into canonical CBOR (RFC 8949)."""

    @classmethod
    def encode(cls, value: Any) -> bytes:
        if isinstance(value, bool):
            return b"\xf5" if value else b"\xf4"
        elif value is None:
            return b"\xf6"
        elif isinstance(value, int):
            if value >= 0:
                return cls._encode_uint(0, value)
            else:
                return cls._encode_uint(1, -1 - value)
        elif isinstance(value, (bytes, bytearray)):
            return cls._encode_uint(2, len(value)) + bytes(value)
        elif isinstance(value, str):
            encoded = value.encode("utf-8")
            return cls._encode_uint(3, len(encoded)) + encoded
        elif isinstance(value, (list, tuple)):
            head = cls._encode_uint(4, len(value))
            return head + b"".join(cls.encode(item) for item in value)
        elif isinstance(value, dict):
            # Canonical CBOR sorts keys by length then lexicographically
            encoded_items = [
                (cls.encode(k), cls.encode(v)) for k, v in value.items()
            ]
            encoded_items.sort(key=lambda pair: (len(pair[0]), pair[0]))
            head = cls._encode_uint(5, len(value))
            return head + b"".join(k + v for k, v in encoded_items)
        else:
            raise CborError(f"Unsupported CBOR type: {type(value)}")

    @staticmethod
    def _encode_uint(major: int, val: int) -> bytes:
        major_shifted = major << 5
        if val < 24:
            return bytes([major_shifted | val])
        elif val < 256:
            return bytes([major_shifted | 24, val])
        elif val < 65536:
            return struct.pack(">BH", major_shifted | 25, val)
        elif val < 4294967296:
            return struct.pack(">BI", major_shifted | 26, val)
        elif val < 18446744073709551616:
            return struct.pack(">BQ", major_shifted | 27, val)
        else:
            raise CborError(f"Integer too large for CBOR 64-bit uint: {val}")


class CborDecoder:
    """Decodes canonical CBOR byte sequences into Python primitives."""

    @classmethod
    def decode(cls, data: bytes) -> Any:
        value, offset = cls._decode_item(data, 0)
        if offset != len(data):
            raise CborError(f"Extra trailing bytes in CBOR payload: {len(data) - offset} bytes")
        return value

    @classmethod
    def decode_stream(cls, data: bytes, offset: int = 0) -> Tuple[Any, int]:
        """Decodes next item and returns (value, new_offset)."""
        return cls._decode_item(data, offset)

    @classmethod
    def _decode_item(cls, data: bytes, offset: int) -> Tuple[Any, int]:
        if offset >= len(data):
            raise CborError("Unexpected end of CBOR buffer")

        initial_byte = data[offset]
        major = initial_byte >> 5
        additional_info = initial_byte & 0x1F
        offset += 1

        val, offset = cls._decode_additional_info(data, offset, additional_info)

        if major == 0:  # Unsigned integer
            return val, offset
        elif major == 1:  # Negative integer
            return -1 - val, offset
        elif major == 2:  # Byte string
            end = offset + val
            if end > len(data):
                raise CborError("Byte string exceeds CBOR buffer length")
            return data[offset:end], end
        elif major == 3:  # Text string
            end = offset + val
            if end > len(data):
                raise CborError("Text string exceeds CBOR buffer length")
            try:
                return data[offset:end].decode("utf-8"), end
            except UnicodeDecodeError as e:
                raise CborError(f"Invalid UTF-8 in CBOR string: {e}") from e
        elif major == 4:  # Array
            items: List[Any] = []
            for _ in range(val):
                item, offset = cls._decode_item(data, offset)
                items.append(item)
            return items, offset
        elif major == 5:  # Map
            mapping = {}
            for _ in range(val):
                k, offset = cls._decode_item(data, offset)
                v, offset = cls._decode_item(data, offset)
                mapping[k] = v
            return mapping, offset
        elif major == 7:  # Simple / float
            if additional_info == 20:
                return False, offset
            elif additional_info == 21:
                return True, offset
            elif additional_info == 22:
                return None, offset
            raise CborError(f"Unsupported major 7 value: {additional_info}")
        else:
            raise CborError(f"Unsupported major type: {major}")

    @staticmethod
    def _decode_additional_info(data: bytes, offset: int, info: int) -> Tuple[int, int]:
        if info < 24:
            return info, offset
        elif info == 24:
            if offset + 1 > len(data):
                raise CborError("Unexpected EOF reading 1-byte uint")
            return data[offset], offset + 1
        elif info == 25:
            if offset + 2 > len(data):
                raise CborError("Unexpected EOF reading 2-byte uint")
            val = struct.unpack(">H", data[offset : offset + 2])[0]
            return val, offset + 2
        elif info == 26:
            if offset + 4 > len(data):
                raise CborError("Unexpected EOF reading 4-byte uint")
            val = struct.unpack(">I", data[offset : offset + 4])[0]
            return val, offset + 4
        elif info == 27:
            if offset + 8 > len(data):
                raise CborError("Unexpected EOF reading 8-byte uint")
            val = struct.unpack(">Q", data[offset : offset + 8])[0]
            return val, offset + 8
        else:
            raise CborError(f"Invalid CBOR additional info: {info}")
