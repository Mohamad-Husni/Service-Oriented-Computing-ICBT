# Version 1 API contract

Base URLs: Usage `http://127.0.0.1:5101`; Payments `http://127.0.0.1:5102`. All `/api/v1` operations require `Authorization: Bearer <credential>`. JSON is the interchange format. `/health` is unauthenticated process liveness, not database readiness. GET responses use `Cache-Control: no-store`. Error responses use JSON Problem Details (`title`, `status`). See openapi.json for machine-readable schemas.

| Operation | Permissions | Success |
|---|---|---|
| GET /api/v1/accounts/{account}/usage | Owning customer, operator | 200 usage and latest 12 readings |
| POST /api/v1/accounts/{account}/readings | Operator | 201 updated usage |
| GET /api/v1/accounts/{account}/balance | Owning customer, partner, operator | 200 billed, paid, outstanding, dueDate, asOf |
| GET /api/v1/accounts/{account}/payments | Owning customer, operator; partner sees only its own receipts | 200 latest 100 receipts |
| POST /api/v1/payments | Owning customer or partner | 201 new receipt; 200 matching replay |

POST payment body: `{"accountId":"100000001","amount":25.50,"reference":"PARTNER-20260926-001"}`.

POST reading body: `{"meterValue":1261.250,"recordedAt":"2026-09-26T12:00:00Z"}`. Reading time must be strictly later than the account's latest reading and no later than current UTC. Values are cumulative cubic metres, at most three decimal places; meter resets are not supported. Stored timestamps are normalized to UTC.

Payment amount: positive, no more than LKR 1,000,000, at most two decimal places, no greater than the current balance. References: 8–80 ASCII letters/digits/hyphens/underscores. `(Channel, Reference)` is unique. Same reference plus same account and amount returns the original receipt. Reusing it for a changed payload returns 409. Account authorization runs before repository processing.

A payment changes the ledger atomically; the balance is derived from billed cents minus summed paid cents. The portal refreshes after acceptance; other clients see the latest balance on their next GET. This is request-driven freshness, not push notification or smart-meter telemetry. There is no charge to an actual bank card.

| Status | Meaning |
|---|---|
| 400 | Invalid amount, reference, timestamp, meter reading or request body |
| 401 | Missing/invalid credential or web session |
| 403 | Wrong role or customer account |
| 404 | Missing account/route |
| 409 | Overpayment or reused reference with a different payload |
| 429 | Portal login limiter exceeded (10 attempts per fixed one-minute window, shared demo policy) |
| 500 | Unexpected API failure; inspect correlation ID and server log |
| 503 | Portal cannot contact the target service within its eight-second timeout |

The portal exposes `/session`, `/logout`, and `/gateway/{service}/api/v1/...`. POST calls require `X-WaterLink: 1`; no cross-origin CORS permission is granted. An HTTP-only, SameSite=Strict cookie holds the web identity. Service credentials remain on the portal server. The demo uses environment-provisioned identities; replace them with OIDC/OAuth and per-partner scopes before public use.
