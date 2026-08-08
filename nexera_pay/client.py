"""Client Nexera Pay — sync (NexeraPay) et async (NexeraPayAsync)."""

import json
import time
import uuid
from typing import Any, Dict, Optional

import httpx

from nexera_pay.signature import compute_signature
from nexera_pay.errors import NexeraError, make_error


DEFAULT_BASE_URL = "https://pay.nexera.africa"
USER_AGENT = "nexera-pay-python/0.1.0"


class _CoreBase:
    def __init__(self, api_key: str, secret: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        if not api_key:
            raise ValueError("api_key requis")
        if not secret:
            raise ValueError("secret requis")
        self.api_key = api_key
        self.secret = secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _build_request(self, method: str, path: str, body: Optional[Any] = None,
                       idempotency_key: Optional[str] = None) -> tuple[Dict[str, str], str]:
        body_str = json.dumps(body, separators=(",", ":")) if body is not None else ""
        ts = str(int(time.time()))
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        if method.upper() != "GET":
            headers["X-Timestamp"] = ts
            headers["X-Signature"] = compute_signature(self.secret, ts, method, path, body_str)
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers, body_str

    @staticmethod
    def _parse(status: int, headers: httpx.Headers, text: str) -> Any:
        try:
            data = json.loads(text) if "json" in headers.get("content-type", "") else {"raw": text}
        except Exception:
            data = {"raw": text}
        if 200 <= status < 300:
            return data
        raise make_error(status, data)

    @staticmethod
    def _url(base: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        url = f"{base}{path}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None and v != "")
            if qs:
                url += f"?{qs}"
        return url


class NexeraPay(_CoreBase):
    """Client sync."""

    def __init__(self, api_key: str, secret: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        super().__init__(api_key, secret, base_url, timeout)
        # Resources
        from nexera_pay.resources import Payments, Payouts, Refunds, Balance, Settlements
        self.payments = Payments(self)
        self.payouts = Payouts(self)
        self.refunds = Refunds(self)
        self.balance = Balance(self)
        self.settlements = Settlements(self)

    def _request(self, method: str, path: str, body: Optional[Any] = None,
                 idempotency_key: Optional[str] = None,
                 params: Optional[Dict[str, Any]] = None) -> Any:
        headers, body_str = self._build_request(method, path, body, idempotency_key)
        url = self._url(self.base_url, path, params)
        with httpx.Client(timeout=self.timeout) as client:
            r = client.request(method.upper(), url,
                               headers=headers,
                               content=body_str if body_str else None)
        return self._parse(r.status_code, r.headers, r.text)


class NexeraPayAsync(_CoreBase):
    """Client async — même API que NexeraPay mais retourne des coroutines."""

    def __init__(self, api_key: str, secret: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        super().__init__(api_key, secret, base_url, timeout)
        from nexera_pay.resources import PaymentsAsync, PayoutsAsync, RefundsAsync, BalanceAsync, SettlementsAsync
        self.payments = PaymentsAsync(self)
        self.payouts = PayoutsAsync(self)
        self.refunds = RefundsAsync(self)
        self.balance = BalanceAsync(self)
        self.settlements = SettlementsAsync(self)

    async def _request(self, method: str, path: str, body: Optional[Any] = None,
                       idempotency_key: Optional[str] = None,
                       params: Optional[Dict[str, Any]] = None) -> Any:
        headers, body_str = self._build_request(method, path, body, idempotency_key)
        url = self._url(self.base_url, path, params)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.request(method.upper(), url,
                                     headers=headers,
                                     content=body_str if body_str else None)
        return self._parse(r.status_code, r.headers, r.text)


def new_idempotency_key() -> str:
    return str(uuid.uuid4())
