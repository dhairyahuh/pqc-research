"""ASTRA-Sec Core Exception Hierarchy."""


class AstraError(Exception):
    """Base exception for all ASTRA-Sec runtime errors."""

    def __init__(self, message: str, error_code: str = "ASTRA_GENERIC_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ConfigurationError(AstraError):
    """Raised when environment or node configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_CONFIG_ERROR")


class SchemaValidationError(AstraError):
    """Raised when an application data unit or cryptographic envelope fails schema validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_SCHEMA_VALIDATION_ERROR")


class ProtocolError(AstraError):
    """Raised when bundle protocol sequencing, framing, or ratcheting fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_PROTOCOL_ERROR")


class ReplayDetectedError(ProtocolError):
    """Raised when a duplicated bundle sequence or ratchet index is detected."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.error_code = "ASTRA_REPLAY_DETECTED"


class StaleMessageError(ProtocolError):
    """Raised when a bundle exceeds its time-to-live validity window."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.error_code = "ASTRA_STALE_MESSAGE"
