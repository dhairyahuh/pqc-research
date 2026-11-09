"""Unit tests for ASTRA-Sec DTN subsystem (RFC 9171 BPv7, CBOR, RFC 9172 BPSec, ION config)."""

import os
import shutil
import tempfile
import time
import unittest

from astra_sec.dtn.adapter import AstraDtnBridge, BpSecVerificationError, BpV7ExpiredError
from astra_sec.dtn.bpsec import BpSecError, BpSecSecurityContext
from astra_sec.dtn.bpv7 import (
    BLOCK_TYPE_BIB,
    BLOCK_TYPE_PAYLOAD,
    BpV7Bundle,
    CanonicalBlock,
    PrimaryBlock,
    dtn_to_unix_epoch,
    unix_to_dtn_epoch,
)
from astra_sec.dtn.cbor import CborDecoder, CborEncoder
from astra_sec.dtn.contact_plan import IonContactPlan
from astra_sec.dtn.ion_config import IonNodeConfig
from astra_sec.schema.envelope import EnvelopeHeader, PqcMessageEnvelope


class TestBpV7Cbor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cbor_primitives(self):
        cases = [
            0,
            23,
            24,
            255,
            65535,
            4294967295,
            -1,
            -100,
            b"binary_string",
            "hello_space",
            [1, 2, "three", b"four"],
            {"b": 2, "a": 1},
            True,
            False,
            None,
        ]
        for c in cases:
            enc = CborEncoder.encode(c)
            dec = CborDecoder.decode(enc)
            self.assertEqual(dec, c)

    def test_dtn_epoch_conversion(self):
        now_unix = int(time.time())
        dtn_epoch = unix_to_dtn_epoch(now_unix)
        round_trip_unix = dtn_to_unix_epoch(dtn_epoch)
        self.assertEqual(now_unix, round_trip_unix)

    def test_primary_block_roundtrip(self):
        pb = PrimaryBlock(
            destination_eid="dtn://gsb/app",
            source_eid="dtn://gsa/app",
            report_to_eid="dtn:none",
            creation_time_dtn=1000,
            sequence_number=42,
            lifetime_ms=7200000,
        )
        cbor_list = pb.to_cbor_list()
        pb_decoded = PrimaryBlock.from_cbor_list(cbor_list)

        self.assertEqual(pb_decoded.destination_eid, "dtn://gsb/app")
        self.assertEqual(pb_decoded.source_eid, "dtn://gsa/app")
        self.assertEqual(pb_decoded.creation_time_dtn, 1000)
        self.assertEqual(pb_decoded.sequence_number, 42)
        self.assertEqual(pb_decoded.lifetime_ms, 7200000)
        self.assertEqual(pb_decoded.bundle_id, "dtn://gsa/app::1000::42")

    def test_bpv7_bundle_cbor_wire_encoding(self):
        pb = PrimaryBlock(
            destination_eid="dtn://gsb/app",
            source_eid="dtn://gsa/app",
        )
        payload = b"SPACE_PAYLOAD_TEST_DATA"
        bundle = BpV7Bundle(primary_block=pb, payload_data=payload)

        wire_bytes = bundle.to_cbor_bytes()
        decoded_bundle = BpV7Bundle.from_cbor_bytes(wire_bytes)

        self.assertEqual(decoded_bundle.primary.destination_eid, "dtn://gsb/app")
        self.assertEqual(decoded_bundle.primary.source_eid, "dtn://gsa/app")
        self.assertEqual(decoded_bundle.get_payload(), payload)

    def test_bpsec_bib_integrity_and_tampering(self):
        shared_key = os.urandom(32)
        payload = b"AUTHENTICATED_BUNDLE_DATA"
        bib = BpSecSecurityContext.create_bib(1, payload, shared_key)
        self.assertEqual(bib.block_type_code, BLOCK_TYPE_BIB)

        # Verification succeeds with valid key
        self.assertTrue(BpSecSecurityContext.verify_bib(bib, payload, shared_key))

        # Verification fails if payload altered
        tampered_payload = b"TAMPERED_BUNDLE_DATA"
        with self.assertRaises(BpSecError):
            BpSecSecurityContext.verify_bib(bib, tampered_payload, shared_key)

        # Verification fails with incorrect key
        wrong_key = os.urandom(32)
        with self.assertRaises(BpSecError):
            BpSecSecurityContext.verify_bib(bib, payload, wrong_key)

    def test_astra_dtn_bridge_roundtrip(self):
        header = EnvelopeHeader(
            envelope_id="00000000-0000-0000-0000-000000000001",
            source_eid="dtn://gsa/app",
            destination_eid="dtn://gsb/app",
            sequence_id=1,
            kem_ciphertext=b"\x01" * 1088,
            nonce=b"\x02" * 12,
        )
        envelope = PqcMessageEnvelope(
            header=header,
            ciphertext=b"AES_GCM_ENCRYPTED_SECRET",
            tag=b"\x03" * 16,
            signature=b"\x04" * 3309,
        )
        bib_key = os.urandom(32)

        # Wrap in BPv7 with BPSec BIB
        bundle = AstraDtnBridge.envelope_to_bundle(envelope, bib_key=bib_key)
        self.assertEqual(len(bundle.extension_blocks), 1)

        # Unwrap and verify
        unwrapped = AstraDtnBridge.bundle_to_envelope(bundle, bib_key=bib_key)
        self.assertEqual(unwrapped.header.envelope_id, envelope.header.envelope_id)
        self.assertEqual(unwrapped.ciphertext, envelope.ciphertext)

    def test_ion_contact_plan_and_export(self):
        cp = IonContactPlan()
        now = int(time.time())
        cp.add_contact(1, 2, start_time=now - 10, stop_time=now + 500, xmit_rate_bps=1000000)
        cp.add_range(1, 2, start_time=now - 10, stop_time=now + 500, owlt_seconds=1)

        self.assertTrue(cp.is_contact_open(1, 2, now))
        self.assertFalse(cp.is_contact_open(2, 3, now))

        script = cp.export_ionrc_script()
        self.assertIn("a contact", script)
        self.assertIn("a range", script)

    def test_ion_node_config_generation(self):
        out_dir = os.path.join(self.temp_dir, "ion_configs")
        files = IonNodeConfig.generate_4node_constellation(out_dir)
        self.assertEqual(len(files), 16)  # 4 nodes * 4 config files
        self.assertTrue(os.path.exists(os.path.join(out_dir, "node1.bprc")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "node2.ionconfig")))


if __name__ == "__main__":
    unittest.main()
