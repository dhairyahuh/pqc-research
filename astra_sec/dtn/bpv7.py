"""ASTRA-Sec: IETF RFC 9171 Bundle Protocol Version 7 (BPv7) Implementation."""

import binascii
import struct
import time
from typing import Any, List, Optional, Tuple

from astra_sec.dtn.cbor import CborDecoder, CborEncoder, CborError
from astra_sec.schema.validators import validate_dtn_eid

# RFC 9171 Section 4.2.6: DTN Epoch is 2000-01-01 00:00:00 UTC (946684800 seconds past 1970-01-01)
DTN_EPOCH_OFFSET_SECONDS = 946684800

# Canonical Block Types
BLOCK_TYPE_PAYLOAD = 1
BLOCK_TYPE_PREVIOUS_NODE = 7
BLOCK_TYPE_BUNDLE_AGE = 8
BLOCK_TYPE_HOP_COUNT = 10
BLOCK_TYPE_BIB = 11  # RFC 9172 Block Integrity Block
BLOCK_TYPE_BCB = 12  # RFC 9172 Block Confidentiality Block

# Bundle Processing Control Flags
FLAG_IS_FRAGMENT = 0x000001
FLAG_PAYLOAD_IS_ADMIN = 0x000002
FLAG_MUST_NOT_FRAGMENT = 0x000004
FLAG_STATUS_TIME_REQ = 0x000020
FLAG_USER_ACK_REQ = 0x000040

# CRC Types
CRC_NONE = 0
CRC_16 = 1
CRC_32 = 2


def unix_to_dtn_epoch(unix_timestamp: int) -> int:
    """Converts a Unix timestamp (seconds since 1970) to DTN epoch (seconds since 2000)."""
    return max(0, unix_timestamp - DTN_EPOCH_OFFSET_SECONDS)


def dtn_to_unix_epoch(dtn_timestamp: int) -> int:
    """Converts a DTN timestamp (seconds since 2000) to Unix timestamp (seconds since 1970)."""
    return dtn_timestamp + DTN_EPOCH_OFFSET_SECONDS


class PrimaryBlock:
    """RFC 9171 Section 4.2.2 Primary Block."""

    def __init__(
        self,
        destination_eid: str,
        source_eid: str,
        report_to_eid: str = "dtn:none",
        creation_time_dtn: Optional[int] = None,
        sequence_number: int = 1,
        lifetime_ms: int = 3600000,  # 1 hour default
        bundle_control_flags: int = 0,
        crc_type: int = CRC_NONE,
    ):
        self.version = 7
        self.bundle_control_flags = bundle_control_flags
        self.crc_type = crc_type
        self.destination_eid = validate_dtn_eid(destination_eid)
        self.source_eid = validate_dtn_eid(source_eid)
        self.report_to_eid = report_to_eid
        self.creation_time_dtn = (
            creation_time_dtn
            if creation_time_dtn is not None
            else unix_to_dtn_epoch(int(time.time()))
        )
        self.sequence_number = sequence_number
        self.lifetime_ms = lifetime_ms

    @property
    def creation_timestamp(self) -> Tuple[int, int]:
        return (self.creation_time_dtn, self.sequence_number)

    @property
    def bundle_id(self) -> str:
        """Deterministic bundle identifier per RFC 9171 Section 4.2.5.1."""
        return f"{self.source_eid}::{self.creation_time_dtn}::{self.sequence_number}"

    def to_cbor_list(self) -> list:
        block_list = [
            self.version,
            self.bundle_control_flags,
            self.crc_type,
            self.destination_eid,
            self.source_eid,
            self.report_to_eid,
            [self.creation_time_dtn, self.sequence_number],
            self.lifetime_ms,
        ]
        if self.crc_type == CRC_16:
            block_list.append(b"\x00\x00")  # Placeholder or computed CRC
        elif self.crc_type == CRC_32:
            block_list.append(b"\x00\x00\x00\x00")
        return block_list

    @classmethod
    def from_cbor_list(cls, items: list) -> "PrimaryBlock":
        if len(items) < 8:
            raise ValueError(f"Primary block requires at least 8 elements, got {len(items)}")
        version = items[0]
        if version != 7:
            raise ValueError(f"Unsupported BP version {version}, expected 7")

        flags = items[1]
        crc_type = items[2]
        dst = items[3]
        src = items[4]
        report_to = items[5]
        creation_ts = items[6]
        lifetime_ms = items[7]

        return cls(
            destination_eid=dst,
            source_eid=src,
            report_to_eid=report_to,
            creation_time_dtn=creation_ts[0],
            sequence_number=creation_ts[1],
            lifetime_ms=lifetime_ms,
            bundle_control_flags=flags,
            crc_type=crc_type,
        )


class CanonicalBlock:
    """RFC 9171 Section 4.2.3 Canonical Block (Payload or Extension Block)."""

    def __init__(
        self,
        block_type_code: int,
        block_number: int,
        block_type_specific_data: bytes,
        block_control_flags: int = 0,
        crc_type: int = CRC_NONE,
    ):
        self.block_type_code = block_type_code
        self.block_number = block_number
        self.block_control_flags = block_control_flags
        self.crc_type = crc_type
        self.data = block_type_specific_data

    def to_cbor_list(self) -> list:
        block_list = [
            self.block_type_code,
            self.block_number,
            self.block_control_flags,
            self.crc_type,
            self.data,
        ]
        if self.crc_type == CRC_16:
            block_list.append(b"\x00\x00")
        elif self.crc_type == CRC_32:
            block_list.append(b"\x00\x00\x00\x00")
        return block_list

    @classmethod
    def from_cbor_list(cls, items: list) -> "CanonicalBlock":
        if len(items) < 5:
            raise ValueError(f"Canonical block requires at least 5 elements, got {len(items)}")
        return cls(
            block_type_code=items[0],
            block_number=items[1],
            block_control_flags=items[2],
            crc_type=items[3],
            block_type_specific_data=items[4],
        )


class BpV7Bundle:
    """Complete RFC 9171 Bundle Protocol Version 7 Data Unit."""

    def __init__(
        self,
        primary_block: PrimaryBlock,
        payload_data: bytes,
        extension_blocks: Optional[List[CanonicalBlock]] = None,
    ):
        self.primary = primary_block
        self.payload_block = CanonicalBlock(
            block_type_code=BLOCK_TYPE_PAYLOAD,
            block_number=1,
            block_type_specific_data=payload_data,
        )
        self.extension_blocks: List[CanonicalBlock] = extension_blocks or []

    @property
    def bundle_id(self) -> str:
        return self.primary.bundle_id

    def get_payload(self) -> bytes:
        return self.payload_block.data

    def is_expired(self, current_time_unix: Optional[int] = None) -> bool:
        """Evaluates whether bundle lifetime has expired per RFC 9171 Section 4.2.2."""
        now_unix = current_time_unix if current_time_unix is not None else int(time.time())
        now_dtn_ms = unix_to_dtn_epoch(now_unix) * 1000
        creation_dtn_ms = self.primary.creation_time_dtn * 1000
        expiry_time_ms = creation_dtn_ms + self.primary.lifetime_ms
        return now_dtn_ms > expiry_time_ms

    def to_cbor_bytes(self) -> bytes:
        """Serializes bundle into canonical RFC 9171 CBOR byte array."""
        blocks = [self.primary.to_cbor_list()]
        for ext in self.extension_blocks:
            blocks.append(ext.to_cbor_list())
        blocks.append(self.payload_block.to_cbor_list())
        return CborEncoder.encode(blocks)

    @classmethod
    def from_cbor_bytes(cls, data: bytes) -> "BpV7Bundle":
        """Deserializes bundle from canonical RFC 9171 CBOR byte array."""
        decoded = CborDecoder.decode(data)
        if not isinstance(decoded, list) or len(decoded) < 2:
            raise ValueError(f"Malformed BPv7 bundle: must contain at least primary and payload blocks")

        primary = PrimaryBlock.from_cbor_list(decoded[0])
        payload_block = None
        extensions = []

        for block_items in decoded[1:]:
            block = CanonicalBlock.from_cbor_list(block_items)
            if block.block_type_code == BLOCK_TYPE_PAYLOAD:
                payload_block = block
            else:
                extensions.append(block)

        if not payload_block:
            raise ValueError("Malformed BPv7 bundle: missing required Payload Block")

        bundle = cls(
            primary_block=primary,
            payload_data=payload_block.data,
            extension_blocks=extensions,
        )
        return bundle
