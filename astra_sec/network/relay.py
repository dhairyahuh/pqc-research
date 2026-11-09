"""ASTRA-Sec: Satellite Relay Node (L5 Store-Carry-Forward & L6 Disruption Recovery)."""

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set

from astra_sec.core.exceptions import AstraError
from astra_sec.network.routing import ContactSchedule, RoutingTable
from astra_sec.network.spool import PersistentMessageSpool
from astra_sec.schema.envelope import PqcMessageEnvelope
from astra_sec.schema.messages import FdirTelemetryReport
from astra_sec.schema.network import DeliveryStatus, ForwardingEvent, LinkState
from astra_sec.schema.validators import validate_dtn_eid

logger = logging.getLogger("astra_sec.network.relay")


class RelayRoutingError(AstraError):
    """Raised when an envelope cannot be routed to a next hop."""


class SatelliteRelayNode:
    """Intermediate satellite relay operating strictly at L5 (Store-Carry-Forward) and L6 (Disruption Spooling).

    Architectural Invariant:
    Satellite relays inspect ONLY routing metadata in EnvelopeHeader.
    Relays have NO knowledge of KEM secret keys, AEAD keys, or application plaintext.
    Payload remains end-to-end encrypted under AES-256-GCM and signed under ML-DSA-65.
    """

    def __init__(
        self,
        node_eid: str,
        spool_db_path: str,
        routing_table: Optional[RoutingTable] = None,
        contact_schedule: Optional[ContactSchedule] = None,
        forwarder_fn: Optional[Callable[[str, PqcMessageEnvelope], bool]] = None,
        authorized_peers: Optional[Set[str]] = None,
    ):
        self.node_eid = validate_dtn_eid(node_eid)
        self.role = "satellite_relay"
        self.routing_table = routing_table or RoutingTable()
        self.contact_schedule = contact_schedule or ContactSchedule(self.node_eid)
        self.spool = PersistentMessageSpool(spool_db_path)
        self.forwarder_fn = forwarder_fn
        self.authorized_peers = authorized_peers  # If None, all peers allowed

        # In-memory duplicate filter (envelope UUIDs)
        self._seen_envelope_ids: Set[str] = set()

        # Audit event ledger
        self.events: List[ForwardingEvent] = []

        # L7 Spacecraft FDIR Telemetry tracker
        self.fdir_telemetry = FdirTelemetryReport(node_eid=self.node_eid)

    def get_link_state(self, peer_eid: str, at_time: Optional[int] = None) -> LinkState:
        """Returns the current link state towards a peer node."""
        return self.contact_schedule.get_link_state(peer_eid, at_time)

    def count_pending(self) -> int:
        """Returns count of pending messages in the non-volatile spool."""
        return self.spool.count_pending()

    def log_event(
        self,
        event_type: str,
        envelope_id: str,
        source_eid: str,
        destination_eid: str,
        next_hop_eid: Optional[str],
        status: DeliveryStatus,
        details: Optional[Dict[str, Any]] = None,
    ) -> ForwardingEvent:
        """Records a structured forwarding lifecycle event."""
        event = ForwardingEvent(
            node_eid=self.node_eid,
            event_type=event_type,
            envelope_id=envelope_id,
            source_eid=source_eid,
            destination_eid=destination_eid,
            next_hop_eid=next_hop_eid,
            status=status,
            details=details or {},
        )
        self.events.append(event)
        logger.info(
            "[%s] %s | env=%s | %s -> %s | next=%s | status=%s",
            self.node_eid,
            event_type,
            envelope_id[:8],
            source_eid,
            destination_eid,
            next_hop_eid or "NONE",
            status.value,
        )
        return event

    def set_link_state(self, peer_eid: str, state: LinkState) -> None:
        """Dynamically updates link availability towards a peer."""
        self.contact_schedule.set_link_override(peer_eid, state)
        self.log_event(
            event_type="LINK_STATE_CHANGED",
            envelope_id="00000000-0000-0000-0000-000000000000",
            source_eid=self.node_eid,
            destination_eid=peer_eid,
            next_hop_eid=peer_eid,
            status=DeliveryStatus.QUEUED,
            details={"link_state": state.value},
        )

    def ingest(
        self,
        envelope: PqcMessageEnvelope,
        from_peer: Optional[str] = None,
        current_time: Optional[int] = None,
    ) -> ForwardingEvent:
        """Ingests an incoming envelope, executes security checks, spools, and forwards if link is open.

        Zero Decryption Guarantee:
        The relay reads only `envelope.header`. Plaintext is neither accessed nor accessible.
        """
        header = envelope.header
        env_id = header.envelope_id
        now = current_time if current_time is not None else int(time.time())

        # 1. Peer Authorization Check
        if self.authorized_peers is not None:
            peer_to_check = from_peer or header.source_eid
            if peer_to_check not in self.authorized_peers:
                return self.log_event(
                    event_type="REJECT_UNAUTHORIZED_PEER",
                    envelope_id=env_id,
                    source_eid=header.source_eid,
                    destination_eid=header.destination_eid,
                    next_hop_eid=None,
                    status=DeliveryStatus.DROPPED_UNAUTHORIZED,
                    details={"unauthorized_peer": peer_to_check},
                )

        # 2. Duplicate Detection
        if env_id in self._seen_envelope_ids:
            return self.log_event(
                event_type="REJECT_DUPLICATE_ENVELOPE",
                envelope_id=env_id,
                source_eid=header.source_eid,
                destination_eid=header.destination_eid,
                next_hop_eid=None,
                status=DeliveryStatus.DROPPED_DUPLICATE,
                details={"reason": "Envelope ID already processed by relay"},
            )
        self._seen_envelope_ids.add(env_id)

        # 3. Freshness / TTL Check
        if now > (header.timestamp_utc + header.ttl_seconds):
            return self.log_event(
                event_type="REJECT_EXPIRED_ENVELOPE",
                envelope_id=env_id,
                source_eid=header.source_eid,
                destination_eid=header.destination_eid,
                next_hop_eid=None,
                status=DeliveryStatus.EXPIRED,
                details={"expired_by_seconds": now - (header.timestamp_utc + header.ttl_seconds)},
            )

        # 4. Routing Table Lookup
        next_hop = self.routing_table.get_next_hop(header.destination_eid)
        if not next_hop:
            return self.log_event(
                event_type="ROUTING_FAILED_NO_ROUTE",
                envelope_id=env_id,
                source_eid=header.source_eid,
                destination_eid=header.destination_eid,
                next_hop_eid=None,
                status=DeliveryStatus.DROPPED_UNAUTHORIZED,
                details={"error": f"No route to destination '{header.destination_eid}'"},
            )

        # 5. Non-Volatile Spooling
        self.spool.enqueue(envelope, next_hop, initial_status=DeliveryStatus.QUEUED)

        # 6. Check Contact Availability towards Next Hop
        if not self.contact_schedule.is_contact_available(next_hop, at_time=now):
            self.spool.update_status(env_id, DeliveryStatus.WAITING_CONTACT)
            return self.log_event(
                event_type="MESSAGE_SPOOLED_WAITING_CONTACT",
                envelope_id=env_id,
                source_eid=header.source_eid,
                destination_eid=header.destination_eid,
                next_hop_eid=next_hop,
                status=DeliveryStatus.WAITING_CONTACT,
                details={"link_state": self.contact_schedule.get_link_state(next_hop, now).value},
            )

        # 7. Immediate Forwarding attempt
        forward_ok = False
        if self.forwarder_fn:
            try:
                forward_ok = self.forwarder_fn(next_hop, envelope, from_peer=self.node_eid)
            except TypeError:
                try:
                    forward_ok = self.forwarder_fn(next_hop, envelope)
                except Exception as e:
                    logger.warning("Forwarding to %s failed: %s", next_hop, e)
                    forward_ok = False
            except Exception as e:
                logger.warning("Forwarding to %s failed: %s", next_hop, e)
                forward_ok = False
        else:
            forward_ok = True

        if forward_ok:
            self.spool.mark_forwarded(env_id)
            return self.log_event(
                event_type="MESSAGE_FORWARDED",
                envelope_id=env_id,
                source_eid=header.source_eid,
                destination_eid=header.destination_eid,
                next_hop_eid=next_hop,
                status=DeliveryStatus.FORWARDED,
            )
        else:
            self.spool.update_status(env_id, DeliveryStatus.WAITING_CONTACT)
            return self.log_event(
                event_type="FORWARDING_DEFERRED_UNAVAILABLE",
                envelope_id=env_id,
                source_eid=header.source_eid,
                destination_eid=header.destination_eid,
                next_hop_eid=next_hop,
                status=DeliveryStatus.WAITING_CONTACT,
            )

    def process_spool(self, current_time: Optional[int] = None) -> List[ForwardingEvent]:
        """Flushes spooled messages when contact windows become available."""
        now = current_time if current_time is not None else int(time.time())
        pending = self.spool.get_pending()
        flushed_events: List[ForwardingEvent] = []

        for item in pending:
            env = item.envelope
            header = env.header

            # Check expiration in queue
            if now > (header.timestamp_utc + header.ttl_seconds):
                self.spool.mark_expired(item.envelope_id)
                evt = self.log_event(
                    event_type="SPOOL_MESSAGE_EXPIRED",
                    envelope_id=item.envelope_id,
                    source_eid=header.source_eid,
                    destination_eid=header.destination_eid,
                    next_hop_eid=item.next_hop_eid,
                    status=DeliveryStatus.EXPIRED,
                )
                flushed_events.append(evt)
                continue

            # Check contact availability
            if self.contact_schedule.is_contact_available(item.next_hop_eid, at_time=now):
                forward_ok = False
                if self.forwarder_fn:
                    try:
                        forward_ok = self.forwarder_fn(item.next_hop_eid, env, from_peer=self.node_eid)
                    except TypeError:
                        try:
                            forward_ok = self.forwarder_fn(item.next_hop_eid, env)
                        except Exception as e:
                            logger.warning("Spool flush to %s failed: %s", item.next_hop_eid, e)
                            forward_ok = False
                    except Exception as e:
                        logger.warning("Spool flush to %s failed: %s", item.next_hop_eid, e)
                        forward_ok = False
                else:
                    forward_ok = True

                if forward_ok:
                    self.spool.mark_forwarded(item.envelope_id)
                    evt = self.log_event(
                        event_type="SPOOL_MESSAGE_FORWARDED",
                        envelope_id=item.envelope_id,
                        source_eid=header.source_eid,
                        destination_eid=header.destination_eid,
                        next_hop_eid=item.next_hop_eid,
                        status=DeliveryStatus.FORWARDED,
                    )
                    flushed_events.append(evt)

        return flushed_events
