"""ASTRA-Sec Structured Configuration Management."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from astra_sec.core.exceptions import ConfigurationError


class AstraNodeConfig(BaseModel):
    """Configuration for an ASTRA-Sec network node (Ground Station or Satellite Relay)."""

    node_eid: str = Field(
        default="dtn://gsa/app",
        description="RFC 9171 Endpoint Identifier (EID) for the local node",
    )
    role: str = Field(
        default="originator",
        description="Node role: 'originator', 'relay', or 'destination'",
    )
    listen_host: str = Field(default="127.0.0.1", description="Binding IP address")
    listen_port: int = Field(default=4556, ge=1024, le=65535, description="Convergence layer port")
    health_port: int = Field(default=8080, ge=1024, le=65535, description="HTTP Health check port")
    log_level: str = Field(default="INFO", description="Logging verbosity (DEBUG, INFO, WARN, ERROR)")
    json_logs: bool = Field(default=False, description="Whether to output structured JSON logs")
    spool_directory: Path = Field(
        default=Path("./data/spool"),
        description="Persistent store-carry-forward bundle directory",
    )
    peer_endpoints: List[str] = Field(
        default_factory=list,
        description="List of downstream peer EIDs for routing",
    )
    ratchet_interval_bundles: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Number of bundles between asymmetric ratchet rotations",
    )
    bundle_ttl_seconds: int = Field(
        default=86400,
        ge=60,
        description="Default bundle Time-To-Live in seconds",
    )

    @field_validator("node_eid")
    @classmethod
    def validate_node_eid(cls, v: str) -> str:
        if not v.startswith("dtn://"):
            raise ValueError(f"node_eid must start with 'dtn://', got '{v}'")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = {"originator", "relay", "destination"}
        if v.lower() not in valid_roles:
            raise ValueError(f"role must be one of {valid_roles}, got '{v}'")
        return v.lower()


def load_env_file(env_path: Optional[Path] = None) -> None:
    """Loads key-value pairs from a .env file into os.environ if not already set."""
    target_path = env_path or Path(".env")
    if not target_path.is_file():
        return
    with open(target_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                k, v = stripped.split("=", 1)
                k_clean = k.strip()
                v_clean = v.strip().strip("'\"")
                if k_clean and k_clean not in os.environ:
                    os.environ[k_clean] = v_clean


def load_node_config(env_file: Optional[Path] = None) -> AstraNodeConfig:
    """Loads and validates node configuration from environment variables and .env file.

    Returns:
        A validated AstraNodeConfig instance.

    Raises:
        ConfigurationError: If any setting is invalid or malformed.
    """
    load_env_file(env_file)
    try:
        raw_peers = os.getenv("ASTRA_PEER_ENDPOINTS", "")
        peers_list = [p.strip() for p in raw_peers.split(",") if p.strip()]

        config = AstraNodeConfig(
            node_eid=os.getenv("ASTRA_NODE_EID", "dtn://gsa/app"),
            role=os.getenv("ASTRA_NODE_ROLE", "originator"),
            listen_host=os.getenv("ASTRA_LISTEN_HOST", "127.0.0.1"),
            listen_port=int(os.getenv("ASTRA_LISTEN_PORT", "4556")),
            health_port=int(os.getenv("ASTRA_HEALTH_PORT", "8080")),
            log_level=os.getenv("ASTRA_LOG_LEVEL", "INFO"),
            json_logs=os.getenv("ASTRA_JSON_LOGS", "false").lower() in ("true", "1", "yes"),
            spool_directory=Path(os.getenv("ASTRA_SPOOL_DIR", "./data/spool")),
            peer_endpoints=peers_list,
            ratchet_interval_bundles=int(os.getenv("ASTRA_RATCHET_INTERVAL", "100")),
            bundle_ttl_seconds=int(os.getenv("ASTRA_BUNDLE_TTL", "86400")),
        )
        return config
    except Exception as exc:
        raise ConfigurationError(f"Failed to load ASTRA-Sec configuration: {exc}") from exc
