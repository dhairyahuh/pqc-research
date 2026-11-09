"""ASTRA-Sec: Versioned Cryptographic Message Envelope and Canonical Serializations."""

import hashlib
import struct
import time
import uuid
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from astra_sec.schema.validators import validate_byte_length, validate_dtn_eid


class EnvelopeHeader(BaseModel):
    """Authenticated Header covering routing, freshness, anti-replay, and KEM encapsulation."""

    version: int = Field(default=1, ge=1, le=65535)
    envelope_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_eid: str = Field(..., description="Originating node RFC 9171 EID")
    destination_eid: str = Field(..., description="Destination node RFC 9171 EID")
    sequence_id: int = Field(default=1, ge=1, description="Strictly monotonic sequence number")
    timestamp_utc: int = Field(default_factory=lambda: int(time.time()))
    ttl_seconds: int = Field(default=3600, ge=10, description="Freshness validity window in seconds")
    kem_ciphertext: bytes = Field(..., description="ML-KEM-768 Ciphertext (1088 bytes)")
    nonce: bytes = Field(..., description="AES-256-GCM Nonce (12 bytes)")

    @field_validator("source_eid", "destination_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)

    @field_validator("kem_ciphertext")
    @classmethod
    def check_kem_ct(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 1088, "ML-KEM-768 Ciphertext")

    @field_validator("nonce")
    @classmethod
    def check_nonce(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 12, "AES-GCM Nonce")

    def to_canonical_aad(self) -> bytes:
        """Constructs canonical Authenticated Additional Data (AAD) for AES-256-GCM.

        Covers all routing metadata, sequence ID, timestamps, KEM ciphertext, and nonce.
        """
        magic = b"ASTR-AEAD-V1"
        env_id_bytes = self.envelope_id.encode("ascii").ljust(36, b"\x00")[:36]
        src_bytes = self.source_eid.encode("utf-8")
        dst_bytes = self.destination_eid.encode("utf-8")

        fixed_prefix = struct.pack(
            ">12sH36sHHQQI",
            magic,
            self.version,
            env_id_bytes,
            len(src_bytes),
            len(dst_bytes),
            self.sequence_id,
            self.timestamp_utc,
            self.ttl_seconds,
        )

        return (
            fixed_prefix
            + src_bytes
            + dst_bytes
            + self.kem_ciphertext
            + self.nonce
        )

    def to_signable_representation(self, ciphertext: bytes, tag: bytes) -> bytes:
        """Constructs the canonical byte sequence signed by the sender's ML-DSA-65 key.

        Binds:
        1. Magic header (b"ASTR-SIG-V1")
        2. Full canonical AAD (all metadata + KEM ciphertext + nonce)
        3. SHA-256 hash of ciphertext (32 bytes)
        4. Authentication tag (16 bytes)
        """
        magic = b"ASTR-SIG-V1"
        ct_hash = hashlib.sha256(ciphertext).digest()
        aad = self.to_canonical_aad()
        prefix = struct.pack(">11sI", magic, len(aad))
        return prefix + aad + ct_hash + tag


class PqcMessageEnvelope(BaseModel):
    """Complete Encrypted and Signed ASTRA-Sec Message Envelope."""

    header: EnvelopeHeader
    ciphertext: bytes = Field(..., description="AES-256-GCM encrypted application payload")
    tag: bytes = Field(..., description="AES-256-GCM 16-byte authentication tag")
    signature: bytes = Field(..., description="ML-DSA-65 3309-byte digital signature")

    @field_validator("tag")
    @classmethod
    def check_tag(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 16, "AES-GCM Tag")

    @field_validator("signature")
    @classmethod
    def check_signature(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 3309, "ML-DSA-65 Signature")

    def to_binary(self) -> bytes:
        """Encodes envelope into canonical binary wire format."""
        aad = self.header.to_canonical_aad()
        aad_len = len(aad)
        ct_len = len(self.ciphertext)
        wire_magic = b"ASTRA_MSG_V1"

        header_packed = struct.pack(
            ">12sII",
            wire_magic,
            aad_len,
            ct_len,
        )
        return (
            header_packed
            + aad
            + self.ciphertext
            + self.tag
            + self.signature
        )

    @classmethod
    def from_binary(cls, data: bytes) -> "PqcMessageEnvelope":
        """Decodes envelope from canonical binary wire format."""
        if len(data) < 20:
            raise ValueError(f"Binary envelope too short: {len(data)} bytes")
        wire_magic, aad_len, ct_len = struct.unpack(">12sII", data[:20])
        if wire_magic != b"ASTRA_MSG_V1":
            raise ValueError(f"Invalid binary envelope magic: {wire_magic}")

        expected_min_len = 20 + aad_len + ct_len + 16 + 3309
        if len(data) != expected_min_len:
            raise ValueError(
                f"Binary envelope size mismatch: expected {expected_min_len} bytes, got {len(data)} bytes"
            )

        aad = data[20 : 20 + aad_len]
        if len(aad) < 74 + 1088 + 12:
            raise ValueError("Corrupt canonical AAD in binary envelope")

        magic, version, env_id_raw, src_len, dst_len, seq_id, ts, ttl = struct.unpack(
            ">12sH36sHHQQI", aad[:74]
        )
        if magic != b"ASTR-AEAD-V1":
            raise ValueError("Invalid AAD magic in binary envelope")

        env_id = env_id_raw.rstrip(b"\x00").decode("ascii")
        offset = 74
        src_eid = aad[offset : offset + src_len].decode("utf-8")
        offset += src_len
        dst_eid = aad[offset : offset + dst_len].decode("utf-8")
        offset += dst_len
        kem_ct = aad[offset : offset + 1088]
        offset += 1088
        nonce = aad[offset : offset + 12]

        header = EnvelopeHeader(
            version=version,
            envelope_id=env_id,
            source_eid=src_eid,
            destination_eid=dst_eid,
            sequence_id=seq_id,
            timestamp_utc=ts,
            ttl_seconds=ttl,
            kem_ciphertext=kem_ct,
            nonce=nonce,
        )

        env_offset = 20 + aad_len
        ciphertext = data[env_offset : env_offset + ct_len]
        env_offset += ct_len
        tag = data[env_offset : env_offset + 16]
        env_offset += 16
        signature = data[env_offset : env_offset + 3309]

        return cls(
            header=header,
            ciphertext=ciphertext,
            tag=tag,
            signature=signature,
        )



class MessageAcknowledgment(BaseModel):
    """Signed Cryptographic Receipt returned by recipient (GSB) upon valid receipt."""

    ack_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_envelope_id: str = Field(...)
    source_eid: str = Field(..., description="Acknowledging node EID (GSB)")
    destination_eid: str = Field(..., description="Original sender node EID (GSA)")
    timestamp_utc: int = Field(default_factory=lambda: int(time.time()))
    status: str = Field(default="SUCCESS")
    signature: bytes = Field(..., description="ML-DSA-65 signature by recipient")

    @field_validator("source_eid", "destination_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)

    @field_validator("signature")
    @classmethod
    def check_signature(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 3309, "ML-DSA-65 Signature")

    def to_signable_bytes(self) -> bytes:
        """Constructs canonical bytes for ACK signature verification."""
        magic = b"ASTR-ACK-V1"
        packed = struct.pack(
            ">11s36s36sQI",
            magic,
            self.ack_id.encode("ascii").ljust(36, b"\x00")[:36],
            self.original_envelope_id.encode("ascii").ljust(36, b"\x00")[:36],
            self.timestamp_utc,
            len(self.status.encode("utf-8")),
        )
        return (
            packed
            + self.source_eid.encode("utf-8")
            + self.destination_eid.encode("utf-8")
            + self.status.encode("utf-8")
        )
