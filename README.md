# nexera-pay

[![PyPI version](https://img.shields.io/pypi/v/nexera-pay?style=flat-square&color=a78bfa&logo=pypi&logoColor=white)](https://pypi.org/project/nexera-pay/)
[![PyPI downloads](https://img.shields.io/pypi/dm/nexera-pay?style=flat-square&color=67e8f9)](https://pypi.org/project/nexera-pay/)
[![Python versions](https://img.shields.io/pypi/pyversions/nexera-pay?style=flat-square)](https://pypi.org/project/nexera-pay/)
[![license](https://img.shields.io/pypi/l/nexera-pay?style=flat-square)](./LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Nexera-Africa-DRC/nexera-pay-python/publish.yml?style=flat-square&label=publish)](https://github.com/Nexera-Africa-DRC/nexera-pay-python/actions)

SDK Python officiel pour **Nexera Pay** — API paiement Payment Facilitator RDC (Mobile Money + Carte, wrapper Moko/PayDRC/Cybersource).

## Installation

```bash
pip install nexera-pay
```

## Quickstart

```python
from nexera_pay import NexeraPay
import os

nexera = NexeraPay(
    api_key=os.environ["NEXERA_PAY_API_KEY"],
    secret=os.environ["NEXERA_PAY_SECRET"],
)

# Créer un paiement Mobile Money (STK)
payment = nexera.payments.create(
    amount=10000,          # 100.00 USD en cents
    currency="USD",
    method="mobile_money",
    operator="mpesa",
    phone="243812345001",
    reference="INV-2026-0001",
    description="Facture #INV-2026-0001",
)

print(payment["id"], payment["status"])   # pay_xxxx  processing
```

## Client async

```python
from nexera_pay import NexeraPayAsync
import asyncio

async def main():
    nexera = NexeraPayAsync(api_key="...", secret="...")
    p = await nexera.payments.create(
        amount=100, currency="CDF", method="mobile_money",
        operator="mpesa", phone="243828584688", reference="TEST-1",
    )
    print(p)

asyncio.run(main())
```

## Créer un paiement carte

```python
payment = nexera.payments.create(
    amount=50000, currency="USD", method="card",
    reference="INV-002",
    customer_email="client@example.com",
    customer_name="Jean Kabala",
    return_url="https://monsite.cd/facture/002",
)
# Rediriger le client :
# checkout_url = payment["checkout_url"]
```

## Vérifier un webhook (Django/Flask/FastAPI)

```python
from nexera_pay import verify_webhook_signature
from flask import Flask, request

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_..."

@app.route("/webhooks/nexera", methods=["POST"])
def webhook():
    sig = request.headers.get("X-Nexera-Signature", "")
    if not verify_webhook_signature(WEBHOOK_SECRET, sig, request.get_data(as_text=True)):
        return "invalid signature", 401
    event = request.json
    if event["type"] == "payment.succeeded":
        tx = event["data"]["object"]
        # Marquer la facture tx["reference"] comme payée
    return "ok", 200
```

## Payout B2C

```python
payout = nexera.payouts.create(
    amount=100, currency="CDF",
    operator="mpesa", phone="243828584688",
    reference="REMB-001", description="Remboursement client",
)
```

## Refund

```python
# Refund total
nexera.refunds.create("pay_xxx")

# Refund partiel
nexera.refunds.create("pay_xxx", amount=5000, reason="Article manquant")
```

## Balance

```python
bal = nexera.balance.get()
print(bal["available"]["USD"], bal["available"]["CDF"])   # en cents
```

## Gestion d'erreurs

```python
from nexera_pay import NexeraPay, ValidationError, RateLimitError, SignatureError

try:
    p = nexera.payments.create(amount=10000, ...)
except RateLimitError as e:
    print(f"Rate limited, retry dans {e.retry_after}s")
except ValidationError as e:
    print(f"Validation failed: {e.detail}")
except SignatureError:
    # Clé/secret incorrect ou horloge système décalée
    pass
```

## Sandbox

Clé `nex_test_...` → tout mocké, aucun vrai argent. Patterns MSISDN de test :

| MSISDN | Résultat |
|--------|----------|
| `...001` | Succès en 3s |
| `...002` | Failed |
| `...003` | Timeout puis failed |
| `...004` | Failed (wrong PIN) |

## Docs

https://docs.nexera.africa/pay

## License

MIT
