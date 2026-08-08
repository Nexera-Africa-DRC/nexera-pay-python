"""Nexera Pay — SDK Python officiel.

Usage :
    from nexera_pay import NexeraPay
    nexera = NexeraPay(api_key="nex_test_...", secret="sk_...")
    p = nexera.payments.create(
        amount=100, currency="CDF", method="mobile_money",
        operator="mpesa", phone="243828584688", reference="INV-001",
    )
"""

from nexera_pay.client import NexeraPay, NexeraPayAsync
from nexera_pay.errors import (
    NexeraError, AuthError, SignatureError,
    IdempotencyConflictError, RateLimitError,
    ValidationError, ProviderError,
)
from nexera_pay.webhooks import verify_webhook_signature
from nexera_pay.signature import compute_signature

__version__ = "0.1.0"

__all__ = [
    "NexeraPay", "NexeraPayAsync",
    "NexeraError", "AuthError", "SignatureError",
    "IdempotencyConflictError", "RateLimitError",
    "ValidationError", "ProviderError",
    "verify_webhook_signature", "compute_signature",
]
