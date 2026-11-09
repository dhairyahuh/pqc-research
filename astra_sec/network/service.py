"""ASTRA-Sec: Isolated Node Service, Network Transport, and Process Daemon."""

import argparse
import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, Optional
import urllib.error
import urllib.request

from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import RoutingTable
from astra_sec.schema.envelope import PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState
from astra_sec.service.ground_station import GroundStationNode

logger = logging.getLogger("astra_sec.network.service")


class NodeTransport:
    """Base transport interface for delivering envelopes between nodes."""

    def send(self, target_eid: str, envelope: PqcMessageEnvelope, from_peer: Optional[str] = None) -> bool:
        raise NotImplementedError


class DirectMemoryTransport(NodeTransport):
    """In-memory direct transport registry for multi-node simulation within one process."""

    def __init__(self):
        self._nodes: Dict[str, Any] = {}

    def register_node(self, eid: str, node: Any) -> None:
        self._nodes[eid] = node

    def get_node(self, eid: str) -> Optional[Any]:
        return self._nodes.get(eid)

    def send(self, target_eid: str, envelope: PqcMessageEnvelope, from_peer: Optional[str] = None) -> bool:
        node = self._nodes.get(target_eid)
        if not node:
            logger.error("Destination node %s not found in transport registry", target_eid)
            return False

        if isinstance(node, SatelliteRelayNode):
            evt = node.ingest(envelope, from_peer=from_peer)
            return evt.status in (DeliveryStatus.FORWARDED, DeliveryStatus.WAITING_CONTACT)
        elif isinstance(node, GroundStationNode):
            try:
                node.receive_message(envelope)
                return True
            except Exception as e:
                logger.error("Ground station %s receive failed: %s", target_eid, e)
                return False
        elif callable(node):
            try:
                return node(target_eid, envelope, from_peer=from_peer)
            except TypeError:
                return node(target_eid, envelope)
        return False


class HttpNodeTransport(NodeTransport):
    """HTTP client transport for delivering envelopes to isolated node server processes."""

    def __init__(self, endpoint_map: Optional[Dict[str, str]] = None):
        # Maps EID -> http://localhost:<port>
        self._endpoints: Dict[str, str] = endpoint_map or {}

    def register_endpoint(self, eid: str, base_url: str) -> None:
        self._endpoints[eid] = base_url.rstrip("/")

    def send(self, target_eid: str, envelope: PqcMessageEnvelope, from_peer: Optional[str] = None) -> bool:
        base_url = self._endpoints.get(target_eid)
        if not base_url:
            logger.error("No HTTP endpoint configured for %s", target_eid)
            return False

        url = f"{base_url}/ingest"
        data = envelope.to_binary()
        headers = {"Content-Type": "application/octet-stream"}
        if from_peer:
            headers["X-From-Peer"] = from_peer

        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("status") in ("OK", "FORWARDED", "WAITING_CONTACT", "DELIVERED")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            logger.warning("HTTP %d error sending to %s: %s", e.code, target_eid, err_body)
            return False
        except Exception as e:
            logger.warning("HTTP send to %s failed: %s", target_eid, e)
            return False


class NodeHttpServer:
    """Embedded HTTP server hosting a GroundStationNode or SatelliteRelayNode."""

    def __init__(self, node: Any, host: str = "127.0.0.1", port: int = 0):
        self.node = node
        self.host = host
        self.requested_port = port
        self.actual_port: int = 0
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

        node_ref = self.node

        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress default noisy stdio logging

            def do_GET(self):
                if self.path == "/health":
                    eid = getattr(node_ref, "node_eid", "unknown")
                    role = getattr(node_ref, "role", "unknown")
                    pending = 0
                    if hasattr(node_ref, "spool"):
                        pending = node_ref.spool.count_pending()
                    self._send_json(200, {"status": "OK", "eid": eid, "role": role, "pending_spool": pending})
                else:
                    self._send_json(404, {"error": "Not Found"})

            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                if self.path == "/ingest":
                    try:
                        from_peer = self.headers.get("X-From-Peer")
                        envelope = PqcMessageEnvelope.from_binary(body)
                        if isinstance(node_ref, SatelliteRelayNode):
                            evt = node_ref.ingest(envelope, from_peer=from_peer)
                            self._send_json(200, {
                                "status": evt.status.value,
                                "event_type": evt.event_type,
                                "envelope_id": evt.envelope_id,
                            })
                        elif isinstance(node_ref, GroundStationNode):
                            plaintext, ack = node_ref.receive_message(envelope)
                            self._send_json(200, {
                                "status": "DELIVERED",
                                "plaintext_len": len(plaintext),
                                "ack_id": ack.ack_id,
                            })
                        else:
                            self._send_json(500, {"error": "Unsupported node type"})
                    except Exception as e:
                        self._send_json(400, {"status": "ERROR", "error": str(e)})

                elif self.path == "/link":
                    try:
                        data = json.loads(body.decode("utf-8"))
                        peer = data["peer_eid"]
                        state_val = data["state"]
                        state = LinkState(state_val)
                        if hasattr(node_ref, "set_link_state"):
                            node_ref.set_link_state(peer, state)
                            self._send_json(200, {"status": "OK", "link_state": state.value})
                        else:
                            self._send_json(400, {"error": "Node does not support link state"})
                    except Exception as e:
                        self._send_json(400, {"error": str(e)})

                elif self.path == "/spool/flush":
                    if hasattr(node_ref, "process_spool"):
                        evts = node_ref.process_spool()
                        self._send_json(200, {"status": "OK", "flushed_count": len(evts)})
                    else:
                        self._send_json(400, {"error": "Node does not have spool"})
                else:
                    self._send_json(404, {"error": "Not Found"})

            def _send_json(self, code: int, payload: dict):
                data = json.dumps(payload).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.handler_class = RequestHandler

    def start(self) -> int:
        self.server = HTTPServer((self.host, self.requested_port), self.handler_class)
        self.actual_port = self.server.server_port
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        logger.info("Node service for %s listening on http://%s:%d", getattr(self.node, "node_eid", "unknown"), self.host, self.actual_port)
        return self.actual_port

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
