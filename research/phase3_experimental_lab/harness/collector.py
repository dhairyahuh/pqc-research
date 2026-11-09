"""ASTRA-Sec Phase 3: System Resource and Measurement Collector.

Captures CPU utilization, RSS memory footprint, storage expansion,
and microsecond-precision operational latencies.
"""

import os
import time
from typing import Any, Dict, List, Optional
import psutil


class MeasurementCollector:
    """Collects system-level resource utilization and per-message metrics."""

    def __init__(self, target_spool_dir: Optional[str] = None):
        self.target_spool_dir = target_spool_dir
        self.process = psutil.Process(os.getpid())
        self.measurements: List[Dict[str, Any]] = []
        self.cpu_samples: List[float] = []
        self.rss_samples: List[int] = []
        self.start_time = time.time()
        self.initial_rss = self.process.memory_info().rss

    def sample_system_resources(self) -> Dict[str, Any]:
        """Samples instantaneous CPU and memory metrics."""
        cpu = psutil.cpu_percent(interval=None)
        rss = self.process.memory_info().rss
        self.cpu_samples.append(cpu)
        self.rss_samples.append(rss)

        disk_bytes = 0
        if self.target_spool_dir and os.path.exists(self.target_spool_dir):
            for root, _, files in os.walk(self.target_spool_dir):
                for f in files:
                    try:
                        disk_bytes += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass

        return {
            "timestamp": time.time(),
            "cpu_percent": cpu,
            "memory_rss_bytes": rss,
            "memory_growth_bytes": rss - self.initial_rss,
            "spool_disk_bytes": disk_bytes,
        }

    def record_message_metric(self, metric: Dict[str, Any]) -> None:
        """Records per-message operational measurement."""
        # Attach instantaneous resource snapshot
        metric.update(self.sample_system_resources())
        self.measurements.append(metric)

    def get_resource_summary(self) -> Dict[str, Any]:
        """Summarizes resource usage across the experiment lifecycle."""
        mean_cpu = sum(self.cpu_samples) / max(1, len(self.cpu_samples))
        peak_rss = max(self.rss_samples) if self.rss_samples else self.initial_rss
        return {
            "mean_cpu_percent": round(mean_cpu, 2),
            "peak_rss_bytes": peak_rss,
            "initial_rss_bytes": self.initial_rss,
            "rss_growth_bytes": peak_rss - self.initial_rss,
            "sample_count": len(self.cpu_samples),
        }
