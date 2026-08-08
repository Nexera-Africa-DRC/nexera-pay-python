"""Exceptions typées Nexera Pay."""

from typing import Any


class NexeraError(Exception):
    def __init__(self, status: int, body: Any):
        self.status = status
        self.type = (body or {}).get("type", "") if isinstance(body, dict) else ""
        self.title = (body or {}).get("title") if isinstance(body, dict) else None
        self.detail = (body or {}).get("detail") if isinstance(body, dict) else None
        self.request_id = (body or {}).get("request_id") if isinstance(body, dict) else None
        self.raw = body
        super().__init__(self.title or f"HTTP {status}")


class AuthError(NexeraError):
    pass


class SignatureError(NexeraError):
    pass


class IdempotencyConflictError(NexeraError):
    pass


class RateLimitError(NexeraError):
    def __init__(self, status: int, body: Any):
        super().__init__(status, body)
        self.retry_after = (body or {}).get("retry_after") if isinstance(body, dict) else None


class ValidationError(NexeraError):
    pass


class ProviderError(NexeraError):
    def __init__(self, status: int, body: Any):
        super().__init__(status, body)
        self.provider = (body or {}).get("provider") if isinstance(body, dict) else None


def make_error(status: int, body: Any) -> NexeraError:
    t = ((body or {}).get("type", "") if isinstance(body, dict) else "")
    if "signature-invalid" in t:
        return SignatureError(status, body)
    if "auth" in t or "api-key" in t:
        return AuthError(status, body)
    if "idempotency" in t:
        return IdempotencyConflictError(status, body)
    if "rate-limit" in t:
        return RateLimitError(status, body)
    if "validation" in t:
        return ValidationError(status, body)
    if "provider" in t:
        return ProviderError(status, body)
    return NexeraError(status, body)
