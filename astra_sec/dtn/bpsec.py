"""ASTRA-Sec: IETF RFC 9172 Bundle Protocol Security (BPSec) Standard Implementation."""

import hashlib
import hmac
import os
import struct
from typing import Optional, Tuple

from astra_sec.dtn.bpv7 import (
    BLOCK_TYPE_BCB,
    BLOCK_TYPE_BIB,
    BLOCK_TYPE_PAYLOAD,
    BpV7Bundle,
    CanonicalBlock,
)

# RFC 9172 Standard Security Context Identifiers
SEC_CTX_AES_GCM_256 = 1    # RFC 9172 Context 1: AES-GCM-256 (Confidentiality & Integrity)
SEC_CTX_HMAC_SHA256 = 2    # RFC 9172 Context 2: HMAC-SHA-256 (Block Integrity)


class BpSecError(Exception):
    """Base exception for BPSec verification failures."""


class BpSecSecurityContext:
    """Evaluates and applies standard RFC 9172 BPSec security blocks."""

    @staticmethod
    def create_bib(target_block_number: int, target_data: bytes, shared_key: bytes) -> CanonicalBlock:
        """Constructs an RFC 9172 Block Integrity Block (BIB) using HMAC-SHA256."""
        # Calculate standard HMAC-SHA256 over target block data
        sig = hmac.new(shared_key, target_data, hashlib.sha256).digest()
        # Security block data: [target_block_num, sec_ctx_id, signature]
        sec_data = struct.pack(">BH", target_block_number, SEC_CTX_HMAC_SHA256) + sig

        return CanonicalBlock(
            block_type_code=BLOCK_TYPE_BIB,
            block_number=2,
            block_type_specific_data=sec_data,
        )

    @staticmethod
    def verify_bib(bib_block: CanonicalBlock, target_data: bytes, shared_key: bytes) -> bool:
        """Verifies an RFC 9172 Block Integrity Block (BIB)."""
        if bib_block.block_type_code != BLOCK_TYPE_BIB:
            raise BpSecError("Block is not a Block Integrity Block (type 11)")
        data = bib_block.data
        if len(data) < 3 + 32:
            raise BpSecError("BIB block data too short")

        target_block_num, sec_ctx = struct.unpack(">BH", data[:3])
        expected_sig = data[3 : 3 + 32]

        if sec_ctx != SEC_CTX_HMAC_SHA256:
            raise BpSecError(f"Unsupported BPSec security context: {sec_ctx}")

        actual_sig = hmac.new(shared_key, target_data, hashlib.sha256).digest()
        if not hmac.compare_digest(actual_sig, expected_sig):
            raise BpSecError("BPSec BIB HMAC signature verification failed")

        return True
