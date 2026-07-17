import uuid


def generate_id(prefix: str) -> str:
    """Generate a GUID-style ID with a human-readable prefix.

    Format: {prefix}{uuid4_hex_first_12_chars}
    Example: acc_a1b2c3d4e5f6
    """
    return f"{prefix}{uuid.uuid4().hex[:12]}"
