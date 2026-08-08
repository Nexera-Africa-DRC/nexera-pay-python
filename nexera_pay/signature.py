"""Signature HMAC pour requêtes API + vérification webhooks."""

import hashlib
import hmac
import time
from typing import Optional


def compute_signature(secret: str, timestamp: str, method: str, path: str, body: str) -> str:
    """Retourne 'sha256=<hex>' pour signer une requête Nexera Pay."""
    payload = f"{timestamp}.{method.upper()}.{path}.{body or ''}"
    mac = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"sha256={mac}"


def verify_webhook_signature(
    secret: str, signature_header: str, body: str,
    tolerance_seconds: int = 300,
) -> bool:
    """Vérifie X-Nexera-Signature (format Stripe : t=ts,v1=hex).
    Retourne True si signature valide ET timestamp fresh."""
    if not secret or not signature_header:
        return False
    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        ts = int(parts["t"])
        v1 = parts["v1"]
    except (ValueError, KeyError):
        return False
    if abs(int(time.time()) - ts) > tolerance_seconds:
        return False
    expected = hmac.new(secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)
