"""ASTRA-Sec: Ground Station Node Services (Point-to-Point Post-Quantum Messaging)."""

import logging
import time
import uuid
from typing import Any, Callable, Optional, Tuple

from astra_sec.core.exceptions import AstraError, ProtocolError, SchemaValidationError
from astra_sec.crypto.aead import Aes256GcmAead, HkdfSha256Engine
from astra_sec.crypto.base import DecapsulationStatus, DsaAdapter, KemAdapter
from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.schema.envelope import (
    EnvelopeHeader,
    MessageAcknowledgment,
    PqcMessageEnvelope,
)
from astra_sec.schema.messages import FdirTelemetryReport
from astra_sec.schema.trust import KeyPair, NodeIdentity, PublicKeyTrustStore, TrustError
from astra_sec.service.replay import AntiReplayFilter

logger = logging.getLogger("astra_sec.ground_station")


class GroundStationSecurityError(AstraError):
    """Base class for ground station communication security violations."""


class SignatureVerificationError(GroundStationSecurityError):
    """Raised when an incoming ML-DSA signature fails cryptographic verification."""


class DecapsulationFaultError(GroundStationSecurityError):
    """Raised when ML-KEM decapsulation fails or monitor detects internal corruption."""


class DestinationMismatchError(GroundStationSecurityError):
    """Raised when incoming message destination EID does not match the receiving node."""


class UnauthorizedSenderError(GroundStationSecurityError):
    """Raised when sender EID is unknown or not authorized in the trust store."""


class GroundStationNode:
    """Ground Station communication endpoint supporting end-to-end post-quantum messaging."""

    def __init__(
        self,
        node_eid: str,
        role: str = "ground_station",
        kem_adapter: Optional[KemAdapter] = None,
        dsa_adapter: Optional[DsaAdapter] = None,
        aead_engine: Optional[Aes256GcmAead] = None,
        trust_store: Optional[PublicKeyTrustStore] = None,
        replay_filter: Optional[AntiReplayFilter] = None,
        policy: Optional[Any] = None,
    ):
        self.node_eid = node_eid
        self.role = role
        self.policy = policy

        # Cryptographic adapters (defaulting to primary native monitored engines)
        self.kem = kem_adapter or CryptoEngineFactory.get_kem_adapter()
        self.dsa = dsa_adapter or CryptoEngineFactory.get_dsa_adapter()
        self.aead = aead_engine or CryptoEngineFactory.get_aead_engine()

        # Trust management and replay protection
        self.trust_store = trust_store or PublicKeyTrustStore()
        self.replay_filter = replay_filter or AntiReplayFilter()

        # Keypairs for this node instance
        self._init_node_keys()

        # FDIR Telemetry tracker
        self.fdir_telemetry = FdirTelemetryReport(node_eid=self.node_eid)

        # Monotonic outgoing sequence counter
        self._next_sequence_id: int = 1

    def get_fdir_telemetry(self) -> FdirTelemetryReport:
        """Returns the current FDIR fault resilience telemetry report."""
        return self.fdir_telemetry

    def _init_node_keys(self) -> None:
        """Initializes ML-KEM and ML-DSA keys for this node."""
        kem_pk, kem_sk = self.kem.generate_keypair()
        dsa_pk, dsa_sk = self.dsa.generate_keypair()

        self.kem_keys = KeyPair(algorithm=self.kem.ALGORITHM_NAME, public_key=kem_pk, secret_key=kem_sk)
        self.dsa_keys = KeyPair(algorithm=self.dsa.ALGORITHM_NAME, public_key=dsa_pk, secret_key=dsa_sk)

        # Register self in local trust store
        self.identity = NodeIdentity(
            eid=self.node_eid,
            role=self.role,
            kem_public_key=kem_pk,
            dsa_public_key=dsa_pk,
            is_authorized=True,
        )
        self.trust_store.register_peer(self.identity)

    def get_public_identity(self) -> NodeIdentity:
        """Exports the public certificate / identity for peer trust distribution."""
        return self.identity

    def rotate_node_keys(self) -> Tuple[KeyPair, KeyPair]:
        """Rotates ML-KEM-768 and ML-DSA-65 keys for this node and updates trust identity."""
        kem_pk, kem_sk = self.kem.generate_keypair()
        dsa_pk, dsa_sk = self.dsa.generate_keypair()

        self.kem_keys = KeyPair(algorithm=self.kem.ALGORITHM_NAME, public_key=kem_pk, secret_key=kem_sk)
        self.dsa_keys = KeyPair(algorithm=self.dsa.ALGORITHM_NAME, public_key=dsa_pk, secret_key=dsa_sk)

        self.identity = NodeIdentity(
            eid=self.node_eid,
            role=self.role,
            kem_public_key=kem_pk,
            dsa_public_key=dsa_pk,
            is_authorized=True,
        )
        self.trust_store.register_peer(self.identity)
        logger.info("Node %s rotated cryptographic keys.", self.node_eid)
        return self.kem_keys, self.dsa_keys

    def revoke_peer(self, peer_eid: str, reason: str = "Revocation") -> None:
        """Revokes authorization for a peer in local trust store and policy."""
        peer = self.trust_store.get_peer(peer_eid)
        if peer:
            peer.is_authorized = False
        if self.policy is not None and hasattr(self.policy, "revoke_identity"):
            self.policy.revoke_identity(peer_eid, reason)
        logger.warning("Node %s revoked authorization for peer '%s': %s", self.node_eid, peer_eid, reason)


    def send_message(
        self,
        destination_eid: str,
        payload: bytes,
        ttl_seconds: int = 3600,
        custom_sequence_id: Optional[int] = None,
        custom_timestamp: Optional[int] = None,
        override_kem_pk: Optional[bytes] = None,
    ) -> PqcMessageEnvelope:
        """Originates, encapsulates, encrypts, and signs an end-to-end PQC message.

        Steps:
        1. Validate destination authorization in trust store.
        2. Generate message identifier and sequence ID.
        3. Encapsulate ML-KEM-768 shared secret under recipient's public key.
        4. Derive symmetric encryption key via HKDF-SHA256.
        5. Encrypt payload with AES-256-GCM using unique nonce & canonical AAD.
        6. Sign canonical envelope representation with sender's ML-DSA-65 key.
        """
        # 1. Trust validation
        if override_kem_pk:
            peer_kem_pk = override_kem_pk
        else:
            try:
                peer_kem_pk = self.trust_store.get_kem_public_key(destination_eid)
            except TrustError as e:
                raise UnauthorizedSenderError(f"Cannot send to '{destination_eid}': {e}") from e

        # 2. Metadata setup
        seq_id = custom_sequence_id if custom_sequence_id is not None else self._next_sequence_id
        if custom_sequence_id is None:
            self._next_sequence_id += 1

        timestamp = custom_timestamp if custom_timestamp is not None else int(time.time())
        envelope_id = str(uuid.uuid4())

        # 3. ML-KEM-768 Encapsulation
        kem_ciphertext, shared_secret = self.kem.encapsulate(peer_kem_pk)

        # 4. HKDF-SHA256 Key Derivation
        aead_key = HkdfSha256Engine.derive_payload_key(shared_secret)

        # 5. Nonce generation
        nonce = self.aead.generate_nonce()

        # Build header
        header = EnvelopeHeader(
            version=1,
            envelope_id=envelope_id,
            source_eid=self.node_eid,
            destination_eid=destination_eid,
            sequence_id=seq_id,
            timestamp_utc=timestamp,
            ttl_seconds=ttl_seconds,
            kem_ciphertext=kem_ciphertext,
            nonce=nonce,
        )

        # 6. AES-256-GCM Encryption with canonical AAD
        aad = header.to_canonical_aad()
        ciphertext, tag = self.aead.encrypt(aead_key, nonce, payload, aad)

        # 7. ML-DSA-65 Signature over canonical signable representation
        signable_bytes = header.to_signable_representation(ciphertext, tag)
        signature = self.dsa.sign(signable_bytes, self.dsa_keys.secret_key)

        return PqcMessageEnvelope(
            header=header,
            ciphertext=ciphertext,
            tag=tag,
            signature=signature,
        )

    def receive_message(
        self,
        envelope: PqcMessageEnvelope,
        current_time: Optional[int] = None,
    ) -> Tuple[bytes, MessageAcknowledgment]:
        """Ingests, verifies, decapsulates, and decrypts an incoming PQC envelope.

        Security Enforcement:
        - Plaintext is NEVER exposed before all verification stages pass.
        - Sender must be authorized in trust store.
        - Destination must match this node.
        - Freshness and anti-replay must succeed.
        - Signature must verify under sender's ML-DSA-65 public key.
        - Decapsulation must complete with SUCCESS status.
        - AEAD tag must verify with canonical AAD.

        Returns: (plaintext_bytes, signed_acknowledgment)
        """
        header = envelope.header

        # 1. Verify Destination matches this node
        if header.destination_eid != self.node_eid:
            raise DestinationMismatchError(
                f"Destination mismatch: envelope targeted '{header.destination_eid}', "
                f"but this node is '{self.node_eid}'."
            )

        # 2. Verify Sender Authorization in Trust Store
        if self.policy is not None and hasattr(self.policy, "validate_sender"):
            self.policy.validate_sender(header.source_eid)

        try:
            sender_dsa_pk = self.trust_store.get_dsa_public_key(header.source_eid)
        except TrustError as e:
            raise UnauthorizedSenderError(
                f"Sender '{header.source_eid}' is not recognized or unauthorized: {e}"
            ) from e

        # 3. Verify Freshness & Anti-Replay
        try:
            self.replay_filter.check_and_update(
                source_eid=header.source_eid,
                sequence_id=header.sequence_id,
                timestamp_utc=header.timestamp_utc,
                ttl_seconds=header.ttl_seconds,
                envelope_id=header.envelope_id,
                current_time=current_time,
            )
        except TypeError:
            self.replay_filter.check_and_update(
                source_eid=header.source_eid,
                sequence_id=header.sequence_id,
                timestamp_utc=header.timestamp_utc,
                ttl_seconds=header.ttl_seconds,
                current_time=current_time,
            )

        # 4. Verify ML-DSA-65 Signature
        signable_bytes = header.to_signable_representation(envelope.ciphertext, envelope.tag)
        is_sig_valid = self.dsa.verify(signable_bytes, envelope.signature, sender_dsa_pk)
        if not is_sig_valid:
            raise SignatureVerificationError(
                f"Signature verification failed for envelope '{header.envelope_id}' from '{header.source_eid}'."
            )

        # 5. Decapsulate ML-KEM-768 Shared Secret (Monitored Native C Engine)
        if hasattr(self.kem, "decapsulate_with_telemetry"):
            try:
                shared_secret, telemetry = self.kem.decapsulate_with_telemetry(
                    header.kem_ciphertext, self.kem_keys.secret_key
                )
                self.fdir_telemetry.transient_recoveries += telemetry.recovered_count
                self.fdir_telemetry.twiddle_faults_detected += telemetry.twiddle_faults_detected
            except Exception as e:
                self.fdir_telemetry.persistent_fail_stops += 1
                self.fdir_telemetry.bundles_rejected += 1
                raise DecapsulationFaultError(
                    f"Monitored ML-KEM decapsulation fault suppression engaged: {e}"
                ) from e
        else:
            shared_secret, dec_status = self.kem.decapsulate(header.kem_ciphertext, self.kem_keys.secret_key)
            if not dec_status.is_success:
                self.fdir_telemetry.persistent_fail_stops += 1
                self.fdir_telemetry.bundles_rejected += 1
                raise DecapsulationFaultError(
                    f"ML-KEM decapsulation rejected or faulted with status {dec_status.name} (0x{dec_status.value:08X})."
                )

        self.fdir_telemetry.bundles_forwarded += 1

        # 6. Derive AES key via HKDF-SHA256
        aead_key = HkdfSha256Engine.derive_payload_key(shared_secret)

        # 7. AES-256-GCM Decryption and Tag Verification
        aad = header.to_canonical_aad()
        plaintext = self.aead.decrypt(aead_key, header.nonce, envelope.ciphertext, envelope.tag, aad)

        # 8. Construct and sign Verified Cryptographic Acknowledgment
        ack_timestamp = current_time if current_time is not None else int(time.time())
        ack = MessageAcknowledgment(
            original_envelope_id=header.envelope_id,
            source_eid=self.node_eid,
            destination_eid=header.source_eid,
            timestamp_utc=ack_timestamp,
            status="SUCCESS",
            signature=b"\x00" * 3309,  # Placeholder before signing
        )
        ack_signable = ack.to_signable_bytes()
        ack_sig = self.dsa.sign(ack_signable, self.dsa_keys.secret_key)
        ack.signature = ack_sig

        return plaintext, ack

    def verify_acknowledgment(self, ack: MessageAcknowledgment, original_envelope: PqcMessageEnvelope) -> bool:
        """Verifies a returned acknowledgment from the recipient."""
        if ack.original_envelope_id != original_envelope.header.envelope_id:
            return False
        if ack.source_eid != original_envelope.header.destination_eid:
            return False
        if ack.destination_eid != self.node_eid:
            return False

        try:
            peer_dsa_pk = self.trust_store.get_dsa_public_key(ack.source_eid)
        except TrustError:
            return False

        ack_signable = ack.to_signable_bytes()
        return self.dsa.verify(ack_signable, ack.signature, peer_dsa_pk)

    def transmit(
        self,
        envelope: PqcMessageEnvelope,
        next_hop_eid: str,
        forwarder_fn: Optional[Callable[[str, PqcMessageEnvelope], bool]] = None,
    ) -> bool:
        """Transmits an originated envelope to the designated next-hop relay or destination."""
        if forwarder_fn is not None:
            return forwarder_fn(next_hop_eid, envelope)
        raise ProtocolError("No forwarder function provided for transmission.")


