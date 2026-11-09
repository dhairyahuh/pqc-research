"""ASTRA-Sec Phase 3: Experiment Orchestrator and Runner.

Executes end-to-end experimental campaigns:
1. Validates configuration.
2. Initializes isolated runtime environment.
3. Spawns appropriate baseline adapter.
4. Enforces network impairments and fault schedules.
5. Injects deterministic workloads.
6. Records immutable raw JSONL measurements.
7. Computes distribution statistics.
8. Generates reproducibility manifest.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
import shutil
import tempfile
import time
import uuid
from typing import Any, Dict, List, Optional

from research.phase3_experimental_lab.adapters.astra_adapter import AstraSecTreatmentAdapter
from research.phase3_experimental_lab.adapters.base import ExperimentAdapter
from research.phase3_experimental_lab.adapters.baseline_non_pqc import BaselineNonPqcAdapter
from research.phase3_experimental_lab.adapters.baseline_unmonitored_pqc import BaselineUnmonitoredPqcAdapter
from research.phase3_experimental_lab.analysis.stats import compute_distribution_metrics
from research.phase3_experimental_lab.fault_campaigns.controller import FaultInjectionController
from research.phase3_experimental_lab.harness.collector import MeasurementCollector
from research.phase3_experimental_lab.harness.config import BaselineType, ExperimentConfig
from research.phase3_experimental_lab.harness.manifest import ExperimentManifest
from research.phase3_experimental_lab.impairments.network import NetworkImpairmentController
from research.phase3_experimental_lab.workloads.generator import WorkloadGenerator


class ExperimentOrchestrator:
    """Coordinates the execution of an experimental trial."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.experiment_id = str(uuid.uuid4())
        self.temp_dir = tempfile.mkdtemp(prefix=f"astra_exp_{self.config.scenario_id.lower()}_")
        self.adapter: Optional[ExperimentAdapter] = None
        self.impairment_ctrl: Optional[NetworkImpairmentController] = None
        self.fault_ctrl: Optional[FaultInjectionController] = None
        self.collector: Optional[MeasurementCollector] = None

    def _select_adapter(self) -> ExperimentAdapter:
        if self.config.baseline == BaselineType.BASELINE_A_NON_PQC:
            return BaselineNonPqcAdapter(use_in_memory_spool=False)
        elif self.config.baseline == BaselineType.BASELINE_B_UNMONITORED_PQC:
            return BaselineUnmonitoredPqcAdapter(use_in_memory_spool=False)
        else:
            return AstraSecTreatmentAdapter(use_in_memory_spool=False)

    def run(self) -> Dict[str, Any]:
        """Executes the full experiment trial from start to manifest generation."""
        start_time_iso = datetime.now(timezone.utc).isoformat()
        config_hash = self.config.compute_config_hash()

        # Initialize output directories
        raw_output_dir = os.path.abspath(self.config.output_dir)
        manifest_dir = os.path.abspath(os.path.join(raw_output_dir, "..", "manifests"))
        os.makedirs(raw_output_dir, exist_ok=True)
        os.makedirs(manifest_dir, exist_ok=True)

        raw_filename = f"{self.config.scenario_id}_{self.experiment_id[:8]}.jsonl"
        raw_output_path = os.path.join(raw_output_dir, raw_filename)
        manifest_filename = f"{self.config.scenario_id}_{self.experiment_id[:8]}_manifest.json"
        manifest_path = os.path.join(manifest_dir, manifest_filename)

        status = "COMPLETED"
        error_details = None
        latencies_us: List[float] = []

        try:
            # 1. Setup Controllers
            self.impairment_ctrl = NetworkImpairmentController(self.config.impairment, self.config.random_seed)
            self.fault_ctrl = FaultInjectionController(self.config.fault, self.config.random_seed)
            self.collector = MeasurementCollector(self.temp_dir)

            # 2. Setup Adapter
            self.adapter = self._select_adapter()
            self.adapter.setup(self.temp_dir, self.impairment_ctrl, self.fault_ctrl)

            # 3. Workload Warm-up (unmetered)
            if self.config.warmup_messages > 0:
                warmup_gen = WorkloadGenerator(self.config.workload, self.config.random_seed)
                for i in range(self.config.warmup_messages):
                    payload = warmup_gen.generate_payload(i)
                    self.adapter.send_and_receive(payload, ttl_seconds=300)

            # 4. Execute Metered Workload
            workload_gen = WorkloadGenerator(self.config.workload, self.config.random_seed)
            t_exp_start = time.perf_counter_ns()

            with open(raw_output_path, "w", encoding="utf-8") as raw_file:
                if self.config.workload.concurrency == 1:
                    # Sequential execution
                    for idx, payload, target_time in workload_gen.iter_workload():
                        # Rate throttling
                        now = time.time()
                        if target_time > now and not self.config.workload.burst_mode:
                            time.sleep(target_time - now)

                        metric = self.adapter.send_and_receive(payload, ttl_seconds=300)
                        metric["message_index"] = idx
                        metric["experiment_id"] = self.experiment_id
                        metric["scenario_id"] = self.config.scenario_id

                        # Record fault outcome if fault active
                        if self.fault_ctrl:
                            has_sdc = metric["status"] == "CORRUPT_PAYLOAD_SDC"
                            self.fault_ctrl.record_outcome(metric["status"], has_sdc)

                        self.collector.record_message_metric(metric)
                        if metric["delivered"]:
                            latencies_us.append(metric["e2e_latency_us"])

                        raw_file.write(json.dumps(metric) + "\n")
                else:
                    # Concurrent execution via ThreadPoolExecutor
                    concurrency = self.config.workload.concurrency
                    with ThreadPoolExecutor(max_workers=concurrency) as executor:
                        futures = []
                        for idx, payload, _ in workload_gen.iter_workload():
                            f = executor.submit(self.adapter.send_and_receive, payload, 300, idx + 100)
                            futures.append((idx, f))

                        for idx, f in futures:
                            metric = f.result()
                            metric["message_index"] = idx
                            metric["experiment_id"] = self.experiment_id
                            metric["scenario_id"] = self.config.scenario_id
                            self.collector.record_message_metric(metric)
                            if metric["delivered"]:
                                latencies_us.append(metric["e2e_latency_us"])
                            raw_file.write(json.dumps(metric) + "\n")

            t_exp_end = time.perf_counter_ns()
            total_duration_s = (t_exp_end - t_exp_start) / 1e9

        except Exception as e:
            status = "FAILED"
            error_details = str(e)
            total_duration_s = 0.0

        finally:
            if self.adapter:
                self.adapter.teardown()
            shutil.rmtree(self.temp_dir, ignore_errors=True)

        end_time_iso = datetime.now(timezone.utc).isoformat()

        # Compute summary statistics
        distribution_stats = compute_distribution_metrics(latencies_us)
        resource_stats = self.collector.get_resource_summary() if self.collector else {}
        impairment_stats = self.impairment_ctrl.get_summary() if self.impairment_ctrl else {}
        fault_stats = self.fault_ctrl.get_summary() if self.fault_ctrl else {}

        delivered_count = len(latencies_us)
        total_attempted = self.config.workload.total_messages
        delivery_rate_pct = (delivered_count / max(1, total_attempted)) * 100.0
        throughput_msg_per_sec = delivered_count / max(0.001, total_duration_s)

        summary = {
            "total_attempted": total_attempted,
            "delivered_count": delivered_count,
            "delivery_rate_pct": round(delivery_rate_pct, 2),
            "throughput_msg_per_sec": round(throughput_msg_per_sec, 2),
            "total_duration_seconds": round(total_duration_s, 4),
            "latency_distribution_us": distribution_stats,
            "resource_utilization": resource_stats,
            "impairment_telemetry": impairment_stats,
            "fault_telemetry": fault_stats,
        }

        # Build and save manifest
        manifest_data = ExperimentManifest.create_manifest(
            experiment_id=self.experiment_id,
            config=self.config.model_dump(mode="json"),
            config_hash=config_hash,
            start_time_utc=start_time_iso,
            end_time_utc=end_time_iso,
            status=status,
            raw_output_path=raw_output_path,
            summary_statistics=summary,
            error_details=error_details,
        )
        ExperimentManifest.save_manifest(manifest_data, manifest_path)

        return {
            "experiment_id": self.experiment_id,
            "status": status,
            "raw_output_path": raw_output_path,
            "manifest_path": manifest_path,
            "summary": summary,
        }
