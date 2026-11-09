"""ASTRA-Sec: Cryptographic Engine Factory & Discovery."""

import logging
from typing import Any, Dict, Optional

from astra_sec.crypto.aead import Aes256GcmAead, HkdfSha256Engine
from astra_sec.crypto.base import DsaAdapter, KemAdapter
from astra_sec.crypto.monitored_c import (
    MonitoredCLoadError,
    MonitoredNativeDsaAdapter,
    MonitoredNativeKemAdapter,
)
from astra_sec.crypto.oqs_adapter import OqsDsaAdapter, OqsKemAdapter

logger = logging.getLogger("astra_sec.crypto")


class CryptoEngineFactory:
    """Factory for instantiating verified Post-Quantum Cryptographic adapters."""

    @classmethod
    def get_kem_adapter(cls, prefer_monitored: bool = True) -> KemAdapter:
        """Returns the active ML-KEM-768 adapter.

        Prioritizes the monitored native C implementation (intended research path).
        Falls back to liboqs if native shared library is unavailable.
        """
        if prefer_monitored:
            try:
                adapter = MonitoredNativeKemAdapter()
                logger.info("Using Monitored Native ML-KEM-768 (Intended Research Path)")
                return adapter
            except (MonitoredCLoadError, Exception) as e:
                logger.warning(
                    f"Monitored C KEM engine unavailable ({e}). Falling back to LibOQS baseline."
                )

        # Fallback to LibOQS
        try:
            adapter = OqsKemAdapter()
            logger.info("Using LibOQS ML-KEM-768 (Reference Baseline)")
            return adapter
        except Exception as e:
            raise RuntimeError(
                f"No usable ML-KEM-768 implementation available on host: {e}"
            ) from e

    @classmethod
    def get_dsa_adapter(cls, prefer_monitored: bool = True) -> DsaAdapter:
        """Returns the active ML-DSA-65 adapter."""
        if prefer_monitored:
            try:
                adapter = MonitoredNativeDsaAdapter()
                logger.info("Using Monitored Native ML-DSA-65 (Intended Research Path)")
                return adapter
            except (MonitoredCLoadError, Exception) as e:
                logger.warning(
                    f"Monitored C DSA engine unavailable ({e}). Falling back to LibOQS baseline."
                )

        try:
            adapter = OqsDsaAdapter()
            logger.info("Using LibOQS ML-DSA-65 (Reference Baseline)")
            return adapter
        except Exception as e:
            raise RuntimeError(
                f"No usable ML-DSA-65 implementation available on host: {e}"
            ) from e

    @classmethod
    def get_aead_engine(cls) -> Aes256GcmAead:
        """Returns the AES-256-GCM AEAD encryption engine."""
        return Aes256GcmAead(enforce_nonce_uniqueness=True)

    @classmethod
    def get_engine_status(cls) -> Dict[str, Any]:
        """Audits available cryptographic engines."""
        native_ok = False
        oqs_ok = False
        native_err = None
        oqs_err = None

        try:
            MonitoredNativeKemAdapter()
            native_ok = True
        except Exception as e:
            native_err = str(e)

        try:
            OqsKemAdapter()
            oqs_ok = True
        except Exception as e:
            oqs_err = str(e)

        return {
            "native_monitored_ready": native_ok,
            "native_error": native_err,
            "liboqs_baseline_ready": oqs_ok,
            "liboqs_error": oqs_err,
            "preferred_engine": "Native-Monitored" if native_ok else "LibOQS",
        }
