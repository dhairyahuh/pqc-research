"""ASTRA-Sec Schema Validators."""

import re
from astra_sec.core.exceptions import SchemaValidationError

DTN_URI_PATTERN = re.compile(r"^dtn://[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\./]+$")


def validate_dtn_eid(eid: str) -> str:
    """Validates that a string is a well-formed RFC 9171 DTN Endpoint Identifier.

    Args:
        eid: The URI string to validate.

    Returns:
        The validated EID string.

    Raises:
        SchemaValidationError: If the EID does not match the DTN URI specification.
    """
    if not isinstance(eid, str) or not DTN_URI_PATTERN.match(eid):
        raise SchemaValidationError(
            f"Invalid DTN Endpoint Identifier (EID): '{eid}'. Must match 'dtn://<node>/<service>'."
        )
    return eid


def validate_byte_length(data: bytes, expected_length: int, field_name: str) -> bytes:
    """Validates that a byte buffer matches an exact required cryptographic length."""
    if not isinstance(data, (bytes, bytearray)):
        raise SchemaValidationError(f"{field_name} must be bytes, got {type(data).__name__}")
    if len(data) != expected_length:
        raise SchemaValidationError(
            f"{field_name} length error: expected {expected_length} bytes, got {len(data)} bytes."
        )
    return bytes(data)
