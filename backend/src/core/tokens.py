import secrets


def generate_public_code() -> str:
    """Capability token para reservas (regla B5: CSPRNG, alta entropía)."""
    return secrets.token_urlsafe(32)
