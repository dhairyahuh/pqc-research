"""ASTRA-Sec: Public-Key Trust Configuration & Node Identities."""

from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator

from astra_sec.core.exceptions import AstraError
from astra_sec.schema.validators import validate_byte_length, validate_dtn_eid


class TrustError(AstraError):
    """Raised when peer authorization or public key verification fails."""


class KeyPair(BaseModel):
    """Container for a cryptographic keypair (development / node memory container).

    Secret key representation is protected from string / log exposure.
    """

    algorithm: str
    public_key: bytes
    secret_key: bytes

    def __repr__(self) -> str:
        return f"<KeyPair algorithm={self.algorithm} public_key_len={len(self.public_key)} sk=[REDACTED]>"

    def __str__(self) -> str:
        return self.__repr__()


class NodeIdentity(BaseModel):
    """Public identity and trusted post-quantum certificates for a network node."""

    eid: str = Field(..., description="RFC 9171 DTN Endpoint ID")
    role: str = Field(default="ground_station", description="Node operational role")
    kem_public_key: bytes = Field(..., description="ML-KEM-768 Public Key (1184 bytes)")
    dsa_public_key: bytes = Field(..., description="ML-DSA-65 Public Key (1952 bytes)")
    is_authorized: bool = Field(default=True, description="Whether node is authorized for secure messaging")

    @field_validator("eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)

    @field_validator("kem_public_key")
    @classmethod
    def check_kem_pk(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 1184, "ML-KEM-768 Public Key")

    @field_validator("dsa_public_key")
    @classmethod
    def check_dsa_pk(cls, v: bytes) -> bytes:
        return validate_byte_length(v, 1952, "ML-DSA-65 Public Key")


class PublicKeyTrustStore:
    """In-memory Public-Key Trust Store managing authenticated peer identities."""

    def __init__(self):
        self._peers: Dict[str, NodeIdentity] = {}

    def register_peer(self, peer: NodeIdentity) -> None:
        """Registers an authorized peer identity."""
        self._peers[peer.eid] = peer

    def get_peer(self, eid: str) -> Optional[NodeIdentity]:
        """Retrieves peer identity if present."""
        return self._peers.get(eid)

    def is_authorized(self, eid: str) -> bool:
        """Returns True if peer is registered and explicitly authorized."""
        peer = self.get_peer(eid)
        return peer is not None and peer.is_authorized

    def get_kem_public_key(self, eid: str) -> bytes:
        """Returns peer's ML-KEM-768 public key or raises TrustError."""
        peer = self.get_peer(eid)
        if not peer:
            raise TrustError(f"Peer '{eid}' is not recognized in trust store.")
        if not peer.is_authorized:
            raise TrustError(f"Peer '{eid}' is registered but unauthorized.")
        return peer.kem_public_key

    def get_dsa_public_key(self, eid: str) -> bytes:
        """Returns peer's ML-DSA-65 public key or raises TrustError."""
        peer = self.get_peer(eid)
        if not peer:
            raise TrustError(f"Peer '{eid}' is not recognized in trust store.")
        if not peer.is_authorized:
            raise TrustError(f"Peer '{eid}' is registered but unauthorized.")
        return peer.dsa_public_key
