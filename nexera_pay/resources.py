"""Resources — sync + async factorisés."""

from typing import Any, Dict, Optional

from nexera_pay.client import new_idempotency_key


# ────────────────────────  SYNC  ────────────────────────

class Payments:
    def __init__(self, client): self.c = client

    def create(self, *, amount: int, currency: str, method: str,
               operator: Optional[str] = None, phone: Optional[str] = None,
               reference: Optional[str] = None, description: Optional[str] = None,
               callback_url: Optional[str] = None, return_url: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None,
               fee_bearer: Optional[str] = None,
               customer_email: Optional[str] = None, customer_name: Optional[str] = None,
               idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        body = {k: v for k, v in {
            "amount": amount, "currency": currency, "method": method,
            "operator": operator, "phone": phone, "reference": reference,
            "description": description, "callback_url": callback_url,
            "return_url": return_url, "metadata": metadata,
            "fee_bearer": fee_bearer, "customer_email": customer_email,
            "customer_name": customer_name,
        }.items() if v is not None}
        return self.c._request("POST", "/v1/payments", body,
                               idempotency_key=idempotency_key or new_idempotency_key())

    def get(self, id: str) -> Dict[str, Any]:
        return self.c._request("GET", f"/v1/payments/{id}")

    def list(self, *, reference: Optional[str] = None, status: Optional[str] = None,
             limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
        return self.c._request("GET", "/v1/payments",
                               params={"reference": reference, "status": status,
                                       "limit": limit, "cursor": cursor})


class Payouts:
    def __init__(self, client): self.c = client

    def create(self, *, amount: int, currency: str, method: str = "mobile_money",
               operator: str, phone: str,
               reference: Optional[str] = None, description: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None,
               idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        body = {k: v for k, v in {
            "amount": amount, "currency": currency, "method": method,
            "operator": operator, "phone": phone,
            "reference": reference, "description": description, "metadata": metadata,
        }.items() if v is not None}
        return self.c._request("POST", "/v1/payouts", body,
                               idempotency_key=idempotency_key or new_idempotency_key())

    def get(self, id: str) -> Dict[str, Any]:
        return self.c._request("GET", f"/v1/payouts/{id}")

    def list(self, *, limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
        return self.c._request("GET", "/v1/payouts", params={"limit": limit, "cursor": cursor})


class Refunds:
    def __init__(self, client): self.c = client

    def create(self, payment_id: str, *, amount: Optional[int] = None,
               reason: Optional[str] = None) -> Dict[str, Any]:
        body = {k: v for k, v in {"amount": amount, "reason": reason}.items() if v is not None}
        return self.c._request("POST", f"/v1/payments/{payment_id}/refund", body)

    def list(self, payment_id: str) -> Dict[str, Any]:
        return self.c._request("GET", f"/v1/payments/{payment_id}/refunds")


class Balance:
    def __init__(self, client): self.c = client
    def get(self) -> Dict[str, Any]:
        return self.c._request("GET", "/v1/balance")


class Settlements:
    def __init__(self, client): self.c = client
    def list(self, *, limit: int = 50) -> Dict[str, Any]:
        return self.c._request("GET", "/v1/settlements", params={"limit": limit})


# ────────────────────────  ASYNC  ────────────────────────

class PaymentsAsync(Payments):
    async def create(self, **kwargs):
        return await self.c._request("POST", "/v1/payments",
                                     {k: v for k, v in kwargs.items() if v is not None and k != "idempotency_key"},
                                     idempotency_key=kwargs.get("idempotency_key") or new_idempotency_key())
    async def get(self, id): return await self.c._request("GET", f"/v1/payments/{id}")
    async def list(self, **params): return await self.c._request("GET", "/v1/payments", params=params)


class PayoutsAsync(Payouts):
    async def create(self, **kwargs):
        return await self.c._request("POST", "/v1/payouts",
                                     {k: v for k, v in kwargs.items() if v is not None and k != "idempotency_key"},
                                     idempotency_key=kwargs.get("idempotency_key") or new_idempotency_key())
    async def get(self, id): return await self.c._request("GET", f"/v1/payouts/{id}")
    async def list(self, **params): return await self.c._request("GET", "/v1/payouts", params=params)


class RefundsAsync(Refunds):
    async def create(self, payment_id, **kwargs):
        return await self.c._request("POST", f"/v1/payments/{payment_id}/refund",
                                     {k: v for k, v in kwargs.items() if v is not None})
    async def list(self, payment_id): return await self.c._request("GET", f"/v1/payments/{payment_id}/refunds")


class BalanceAsync(Balance):
    async def get(self): return await self.c._request("GET", "/v1/balance")


class SettlementsAsync(Settlements):
    async def list(self, *, limit=50): return await self.c._request("GET", "/v1/settlements", params={"limit": limit})
