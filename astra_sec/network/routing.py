"""ASTRA-Sec: Routing Tables and Contact Availability Management."""

import fnmatch
import logging
import time
from typing import Dict, List, Optional

from astra_sec.schema.network import ContactWindow, LinkState
from astra_sec.schema.validators import validate_dtn_eid

logger = logging.getLogger("astra_sec.network.routing")


class RoutingTable:
    """Next-hop route table mapping destination EIDs to intermediate next hops."""

    def __init__(self, routes: Optional[Dict[str, str]] = None):
        self._routes: Dict[str, str] = {}
        if routes:
            for dst, next_hop in routes.items():
                self.add_route(dst, next_hop)

    def add_route(self, destination_pattern: str, next_hop_eid: str) -> None:
        """Adds a routing entry. Pattern can be exact EID or wildcard (e.g. 'dtn://gsb/*')."""
        next_hop = validate_dtn_eid(next_hop_eid)
        self._routes[destination_pattern] = next_hop
        logger.debug("Added route: %s -> %s", destination_pattern, next_hop)

    def remove_route(self, destination_pattern: str) -> bool:
        """Removes a routing entry."""
        if destination_pattern in self._routes:
            del self._routes[destination_pattern]
            return True
        return False

    def get_next_hop(self, destination_eid: str) -> Optional[str]:
        """Resolves the next hop for a destination EID using exact match then wildcard match."""
        # 1. Exact match
        if destination_eid in self._routes:
            return self._routes[destination_eid]

        # 2. Wildcard prefix match
        for pattern, next_hop in self._routes.items():
            if fnmatch.fnmatch(destination_eid, pattern):
                return next_hop

        return None

    def get_all_routes(self) -> Dict[str, str]:
        """Returns copy of all configured routes."""
        return dict(self._routes)


class ContactSchedule:
    """Manages orbital contact schedules and real-time link availability."""

    def __init__(self, source_eid: str):
        self.source_eid = validate_dtn_eid(source_eid)
        self._windows: List[ContactWindow] = []
        self._link_overrides: Dict[str, LinkState] = {}

    def add_contact_window(
        self,
        peer_eid: str,
        start_time_utc: int,
        end_time_utc: int,
        is_active: bool = True,
    ) -> ContactWindow:
        """Schedules an orbital line-of-sight contact window."""
        window = ContactWindow(
            source_eid=self.source_eid,
            peer_eid=peer_eid,
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
            is_active=is_active,
        )
        self._windows.append(window)
        return window

    def set_link_override(self, peer_eid: str, state: LinkState) -> None:
        """Forces physical link state (UP/DOWN/OCCULTED) overriding scheduled windows."""
        peer = validate_dtn_eid(peer_eid)
        self._link_overrides[peer] = state
        logger.info("Node %s link override for %s set to %s", self.source_eid, peer, state.value)

    def clear_link_override(self, peer_eid: str) -> None:
        """Clears manual link override, reverting to scheduled contact windows."""
        peer = validate_dtn_eid(peer_eid)
        if peer in self._link_overrides:
            del self._link_overrides[peer]

    def get_link_state(self, peer_eid: str, at_time: Optional[int] = None) -> LinkState:
        """Determines the current link state towards a peer node."""
        peer = validate_dtn_eid(peer_eid)

        # 1. Check manual override first
        if peer in self._link_overrides:
            return self._link_overrides[peer]

        now = at_time if at_time is not None else int(time.time())

        # 2. Check scheduled contact windows
        for window in self._windows:
            if window.peer_eid == peer and window.is_in_contact(now):
                return LinkState.UP

        # If no explicit windows configured for peer, default to UP for continuous links
        peer_has_windows = any(w.peer_eid == peer for w in self._windows)
        if not peer_has_windows:
            return LinkState.UP

        return LinkState.OCCULTED

    def is_contact_available(self, peer_eid: str, at_time: Optional[int] = None) -> bool:
        """Returns True if link state is UP."""
        return self.get_link_state(peer_eid, at_time) == LinkState.UP
