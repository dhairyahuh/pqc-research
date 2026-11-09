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


class SecurityContinuityError(AstraError):
    """Base class for security state and authorization violations."""

    def __init__(self, message: str, error_code: str = "ASTRA_SECURITY_ERROR") -> None:
        super().__init__(message, error_code=error_code)


class SecurityStateCorruptionError(SecurityContinuityError):
    """Raised when persistent cryptographic security state has been tampered or corrupted."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_SECURITY_STATE_CORRUPTED")


class KeyLifecycleError(SecurityContinuityError):
    """Raised when key transition, rotation, or retirement rules are violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_KEY_LIFECYCLE_ERROR")


class IdentityRevokedError(SecurityContinuityError):
    """Raised when a revoked or blacklisted peer attempts an operation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_IDENTITY_REVOKED")


class InvalidAcknowledgmentError(SecurityContinuityError):
    """Raised when a cryptographic receipt fails verification or correlation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ASTRA_INVALID_ACK")

