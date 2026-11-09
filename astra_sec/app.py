"""ASTRA-Sec Main Application CLI and Health-Check Entry Point."""

import argparse
import json
import sys

from astra_sec import __version__
from astra_sec.core.config import load_node_config
from astra_sec.core.logging import configure_logging
from astra_sec.service.health import HealthService


def main() -> int:
    """Main CLI entry point for ASTRA-Sec runtime."""
    parser = argparse.ArgumentParser(
        prog="astra_sec",
        description="ASTRA-Sec: Post-Quantum Resilient Space Communications Framework",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: health
    health_parser = subparsers.add_parser("health", help="Execute diagnostic health checks")
    health_parser.add_argument(
        "--json",
        action="store_true",
        help="Output health diagnostics in JSON format",
    )

    # Subcommand: info
    subparsers.add_parser("info", help="Print node identity and configuration")

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_node_config()
    except Exception as exc:
        print(f"[FATAL] Configuration load failed: {exc}", file=sys.stderr)
        return 1

    logger = configure_logging(level=config.log_level, json_output=config.json_logs)

    if args.command == "health":
        service = HealthService(config)
        status_dict = service.get_health_status()
        if args.json:
            print(json.dumps(status_dict, indent=2))
        else:
            print("=========================================================================")
            print(f" ASTRA-Sec System Diagnostic Health Report — Version {__version__}")
            print("=========================================================================")
            print(f" Node EID:        {status_dict['node_eid']}")
            print(f" Node Role:       {status_dict['role']}")
            print(f" Overall Status:  {status_dict['status']}")
            print(f" Uptime (sec):    {status_dict['uptime_seconds']}")
            print(" Component Breakdown:")
            for comp_name, comp_info in status_dict["components"].items():
                status_icon = "[PASS]" if comp_info["status"] == "PASS" else f"[{comp_info['status']}]"
                print(f"   {status_icon} {comp_name:<18} : {comp_info.get('status', 'N/A')}")
            print("=========================================================================")
        return 0 if status_dict["status"] in ("OK", "PASS") else 2

    elif args.command == "info":
        print(f"ASTRA-Sec Version: {__version__}")
        print(f"Node EID:         {config.node_eid}")
        print(f"Role:             {config.role}")
        print(f"Listen Address:   {config.listen_host}:{config.listen_port}")
        print(f"Health Port:      {config.health_port}")
        print(f"Spool Directory:  {config.spool_directory}")
        print(f"Ratchet Interval: {config.ratchet_interval_bundles} bundles")
        print(f"Default TTL:      {config.bundle_ttl_seconds}s")
        return 0

    else:
        parser.print_help()
        return 0


def __getattr__(name: str):
    """Lazy-load dashboard ASGI application when invoked via `uvicorn astra_sec.app:app`."""
    if name == "app":
        from astra_sec.dashboard.app import app
        return app
    if name == "create_app":
        from astra_sec.dashboard.app import create_app
        return create_app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


if __name__ == "__main__":
    sys.exit(main())

