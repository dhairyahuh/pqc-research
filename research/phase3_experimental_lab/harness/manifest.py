"""ASTRA-Sec Phase 3: Experiment Manifest and Provenance Tracker.

Generates immutable JSON manifests certifying execution environment,
Git commit, configuration SHA-256, seeds, and output file locations.
"""

import json
import os
import platform
import subprocess
import sys
import time
from typing import Any, Dict, Optional
import psutil


class ExperimentManifest:
    """Certifies the provenance and reproducibility of an experimental run."""

    @staticmethod
    def gather_environment_metadata() -> Dict[str, Any]:
        """Collects host hardware, operating system, and runtime details."""
        # Git information
        commit_hash = "UNKNOWN"
        branch = "UNKNOWN"
        is_dirty = True
        try:
            commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
            is_dirty = len(status) > 0
        except Exception:
            pass

        return {
            "git_commit": commit_hash,
            "git_branch": branch,
            "git_dirty": is_dirty,
            "python_version": sys.version.split()[0],
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_architecture": platform.machine(),
            "processor": platform.processor() or "Apple Silicon",
            "cpu_logical_cores": psutil.cpu_count(logical=True),
            "total_ram_bytes": psutil.virtual_memory().total,
        }

    @classmethod
    def create_manifest(
        cls,
        experiment_id: str,
        config: Dict[str, Any],
        config_hash: str,
        start_time_utc: str,
        end_time_utc: str,
        status: str,
        raw_output_path: str,
        summary_statistics: Dict[str, Any],
        error_details: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "manifest_version": "1.0",
            "experiment_id": experiment_id,
            "status": status,
            "start_time_utc": start_time_utc,
            "end_time_utc": end_time_utc,
            "environment": cls.gather_environment_metadata(),
            "config_hash": config_hash,
            "configuration": config,
            "raw_output_path": raw_output_path,
            "summary_statistics": summary_statistics,
            "error_details": error_details,
        }

    @staticmethod
    def save_manifest(manifest_data: Dict[str, Any], output_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
