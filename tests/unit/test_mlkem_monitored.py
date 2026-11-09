"""Unit tests for Monitored ML-KEM-768 Native Cryptographic Adapter."""

import concurrent.futures
import unittest

from astra_sec.crypto.base import DecapsulationStatus
from astra_sec.crypto.mlkem_monitored import (
    AstraFaultStatus,
    MonitoredMlkemAdapter,
    MonitoredMlkemError,
)
from astra_sec.crypto.oqs_adapter import OqsKemAdapter


class TestMonitoredMlkem(unittest.TestCase):
    """Verifies functional correctness, invariant checking, fault recovery, and fail-stop handling."""

    def setUp(self):
        self.kem = MonitoredMlkemAdapter()
        self.kem.reset_faults()
        self.pk, self.sk = self.kem.generate_keypair()
        self.ct, self.ss_expected = self.kem.encapsulate(self.pk)

    def tearDown(self):
        self.kem.reset_faults()

    def test_01_clean_decapsulation(self):
        """Test 1: Clean decapsulation with zero invariant violations."""
        ss_out, telemetry = self.kem.decapsulate_with_telemetry(self.ct, self.sk)
        self.assertEqual(ss_out, self.ss_expected)
        self.assertEqual(telemetry.status, AstraFaultStatus.SUCCESS)
        self.assertEqual(telemetry.raw_internal_code, 0x5A5A5A5A)
        self.assertEqual(telemetry.mismatch_count, 0)
        self.assertEqual(telemetry.persistent_count, 0)
        self.assertFalse(telemetry.fail_stop_engaged)
        self.assertTrue(telemetry.is_clean)

    def test_02_transient_fault_recovery(self):
        """Test 2: Transient operational twiddle fault is detected and recovered via rollback."""
        # Inject transient twiddle fault: Layer 2, Butterfly 17, Bit 3, persistent=False
        self.kem.inject_op_twiddle_fault(layer=2, butterfly=17, bit=3, persistent=False)

        ss_out, telemetry = self.kem.decapsulate_with_telemetry(self.ct, self.sk)
        # Shared secret must match because transient fault was repaired in-place!
        self.assertEqual(ss_out, self.ss_expected)
        self.assertEqual(telemetry.status, AstraFaultStatus.RECOVERED)
        self.assertGreater(telemetry.mismatch_count, 0)
        self.assertGreater(telemetry.recovered_count, 0)
        self.assertEqual(telemetry.persistent_count, 0)
        self.assertFalse(telemetry.fail_stop_engaged)
        self.assertTrue(telemetry.is_recovered)

    def test_03_persistent_fault_detection_and_fail_stop(self):
        """Test 3: Persistent operational twiddle fault forces fail-stop suppression."""
        # Inject persistent twiddle fault: Layer 3, Butterfly 25, Bit 5, persistent=True
        self.kem.inject_op_twiddle_fault(layer=3, butterfly=25, bit=5, persistent=True)

        with self.assertRaises(MonitoredMlkemError) as ctx:
            self.kem.decapsulate_with_telemetry(self.ct, self.sk)

        telemetry = ctx.exception.telemetry
        self.assertIsNotNone(telemetry)
        self.assertEqual(telemetry.status, AstraFaultStatus.PERSISTENT)
        self.assertGreater(telemetry.persistent_count, 0)
        self.assertTrue(telemetry.fail_stop_engaged)
        self.assertTrue(telemetry.is_fail_stop)

    def test_04_ref_twiddle_transient_and_persistent(self):
        """Test 4: TFIB-Ref reference twiddle checker corruption."""
        # Transient reference twiddle fault: recovers
        self.kem.inject_ref_twiddle_fault(layer=4, butterfly=12, bit=7, persistent=False)
        ss_out, telemetry = self.kem.decapsulate_with_telemetry(self.ct, self.sk)
        self.assertEqual(ss_out, self.ss_expected)
        self.assertGreater(telemetry.mismatch_count, 0)
        self.assertGreater(telemetry.recovered_count, 0)

        # Persistent reference twiddle fault: triggers fail-stop
        self.kem.reset_faults()
        self.kem.inject_ref_twiddle_fault(layer=4, butterfly=12, bit=7, persistent=True)
        with self.assertRaises(MonitoredMlkemError):
            self.kem.decapsulate_with_telemetry(self.ct, self.sk)

    def test_05_checker_logic_perturbation(self):
        """Test 5: Fault in checker evaluation decision logic."""
        # Transient checker logic glitch: recovers via rollback retry
        self.kem.inject_checker_logic_fault(layer=3, butterfly=10, persistent=False)
        ss_out, telemetry = self.kem.decapsulate_with_telemetry(self.ct, self.sk)
        self.assertEqual(ss_out, self.ss_expected)
        self.assertGreater(telemetry.mismatch_count, 0)

        # Persistent checker corruption: triggers fail-stop
        self.kem.reset_faults()
        self.kem.inject_checker_logic_fault(layer=3, butterfly=10, persistent=True)
        with self.assertRaises(MonitoredMlkemError):
            self.kem.decapsulate_with_telemetry(self.ct, self.sk)

    def test_06_invalid_input_rejection(self):
        """Test 6: Invalid ciphertext or secret key lengths must be rejected."""
        with self.assertRaises(ValueError):
            self.kem.decapsulate_with_telemetry(b"\x00" * 500, self.sk)

        with self.assertRaises(ValueError):
            self.kem.decapsulate_with_telemetry(self.ct, b"\x00" * 1000)

        with self.assertRaises(ValueError):
            self.kem.encapsulate(b"\x00" * 500)

    def test_07_repeated_decapsulation_operations(self):
        """Test 7: 100 consecutive clean decapsulations without state leakage or degradation."""
        for i in range(100):
            ss_out, telemetry = self.kem.decapsulate_with_telemetry(self.ct, self.sk)
            self.assertEqual(ss_out, self.ss_expected)
            self.assertEqual(telemetry.status, AstraFaultStatus.SUCCESS)
            self.assertEqual(telemetry.mismatch_count, 0)

    def test_08_concurrent_operations(self):
        """Test 8: Concurrent multi-threaded decapsulations verifying thread safety."""
        num_threads = 8
        iterations_per_thread = 25

        def worker():
            for _ in range(iterations_per_thread):
                ss, telem = self.kem.decapsulate_with_telemetry(self.ct, self.sk)
                if ss != self.ss_expected or not telem.is_clean:
                    return False
            return True

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            for f in concurrent.futures.as_completed(futures):
                self.assertTrue(f.result())

    def test_09_differential_comparison_with_liboqs(self):
        """Test 9: Differential cross-validation between Monitored C and LibOQS."""
        oqs_kem = OqsKemAdapter()

        # 1. Monitored generates keypair, LibOQS encapsulates, Monitored decapsulates
        pk_m, sk_m = self.kem.generate_keypair()
        ct_oqs, ss_oqs = oqs_kem.encapsulate(pk_m)
        ss_m, telem = self.kem.decapsulate_with_telemetry(ct_oqs, sk_m)
        self.assertEqual(ss_m, ss_oqs)
        self.assertTrue(telem.is_clean)

        # 2. LibOQS generates keypair, Monitored encapsulates, LibOQS decapsulates
        pk_oqs, sk_oqs = oqs_kem.generate_keypair()
        ct_m, ss_m_enc = self.kem.encapsulate(pk_oqs)
        ss_oqs_dec, status_oqs = oqs_kem.decapsulate(ct_m, sk_oqs)
        self.assertEqual(status_oqs, DecapsulationStatus.SUCCESS)
        self.assertEqual(ss_m_enc, ss_oqs_dec)


if __name__ == "__main__":
    unittest.main()
