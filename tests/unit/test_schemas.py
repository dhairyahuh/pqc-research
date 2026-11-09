"""Unit tests for ASTRA-Sec Message Schemas and Validation."""

import unittest
from astra_sec.core.exceptions import SchemaValidationError
from astra_sec.schema.messages import (
    ApplicationDataUnit,
    CryptoEnvelopeHeader,
    FdirTelemetryReport,
)
from astra_sec.schema.validators import validate_byte_length, validate_dtn_eid


class TestAstraSchemas(unittest.TestCase):
    """Verifies message schemas, canonical AAD byte generation, and validators."""

    def test_dtn_eid_validator(self) -> None:
        """Verifies RFC 9171 EID syntax validation."""
        self.assertEqual(validate_dtn_eid("dtn://gsa/app"), "dtn://gsa/app")
        self.assertEqual(validate_dtn_eid("dtn://sat1/relay"), "dtn://sat1/relay")
        self.assertEqual(validate_dtn_eid("dtn://constellation-1.node/telemetry"), "dtn://constellation-1.node/telemetry")

        with self.assertRaises(SchemaValidationError):
            validate_dtn_eid("http://gsa/app")
        with self.assertRaises(SchemaValidationError):
            validate_dtn_eid("invalid_uri")
        with self.assertRaises(SchemaValidationError):
            validate_dtn_eid("dtn://missing_service")

    def test_byte_length_validator(self) -> None:
        """Verifies exact byte buffer length assertions."""
        valid_buf = b"\x00" * 32
        self.assertEqual(validate_byte_length(valid_buf, 32, "test_key"), valid_buf)

        with self.assertRaises(SchemaValidationError):
            validate_byte_length(b"\x00" * 31, 32, "test_key")

    def test_application_data_unit(self) -> None:
        """Verifies ApplicationDataUnit creation and validation."""
        adu = ApplicationDataUnit(
            source_eid="dtn://gsa/app",
            destination_eid="dtn://gsb/app",
            command_code=0x0042,
            payload_bytes=b"TELECOMMAND_THRUSTER_FIRE",
            priority=2,
        )
        self.assertEqual(adu.command_code, 0x0042)
        self.assertEqual(adu.priority, 2)
        self.assertEqual(adu.payload_bytes, b"TELECOMMAND_THRUSTER_FIRE")

    def test_crypto_envelope_header_aad(self) -> None:
        """Verifies canonical AAD serialization for AES-GCM binding."""
        header = CryptoEnvelopeHeader(
            sequence_id=42,
            ratchet_step=7,
            timestamp_utc=1700000000,
            ttl_seconds=3600,
            source_eid="dtn://gsa/app",
            destination_eid="dtn://gsb/app",
        )
        aad = header.to_aad_bytes()
        self.assertIsInstance(aad, bytes)
        # Check magic
        self.assertEqual(aad[:4], b"ASTR")
        # Check version (2 bytes) = 1
        self.assertEqual(aad[4:6], (1).to_bytes(2, "big"))
        # Check sequence ID (8 bytes) = 42
        self.assertEqual(aad[6:14], (42).to_bytes(8, "big"))
        # Check ratchet step (8 bytes) = 7
        self.assertEqual(aad[14:22], (7).to_bytes(8, "big"))
        # Total AAD size: 4 + 2 + 8 + 8 + 8 + 4 + 64 + 64 = 162 bytes
        self.assertEqual(len(aad), 162)

    def test_fdir_telemetry_report(self) -> None:
        """Verifies FDIR telemetry metrics schema."""
        report = FdirTelemetryReport(
            node_eid="dtn://sat1/relay",
            uptime_seconds=3600.5,
            transient_recoveries=14,
            persistent_fail_stops=1,
            twiddle_faults_detected=0,
            bundles_forwarded=120,
            bundles_rejected=1,
        )
        self.assertEqual(report.transient_recoveries, 14)
        self.assertEqual(report.persistent_fail_stops, 1)
        self.assertTrue(report.sdc_prevention_engaged)


if __name__ == "__main__":
    unittest.main()
