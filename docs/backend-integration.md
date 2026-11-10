# Backend integration guidelines

## Contract and ownership

The merchant authenticates its users. The Mini App service trusts an asymmetric JWT, not the merchant password or cookie. The reference implementation inspected on 2026-11-10 uses `jwks_v1` and client prefix `/api/v1/mini-app/{merchant_code}`. Its source was on `feature/miniapp-platform` with uncommitted changes; observations are not claims about deployed behavior.

For service owners, the receiving repository's `docs/merchant-integration.md`, route registrars and authenticator implementation remain the implementation reference. This guide contains the simulator-specific details needed without sibling repository access.

## Merchant onboarding (administrator action)

Supply the following configuration to the Mini App service administrator:

```json
{
  "code":"murid_wukong_demo",
  "name":"Murid Wukong Demo Merchant",
  "downstream_merchant_id":"<UUID supplied by Product/Order owners>",
  "auth": {
    "authenticator_key":"jwks_v1",
    "issuer":"https://merchant.example",
    "audience":"bevia-miniapp",
    "jwks_url":"https://merchant.example/.well-known/jwks.json"
  }
}
```

This is the body for `POST /api/v1/admin/mini-app/merchants`, authenticated using the service's configured admin identity. The simulator neither obtains admin credentials nor invokes admin endpoints. Do not invent a downstream merchant UUID. Merchant code must use lowercase `^[a-z0-9][a-z0-9_-]{0,40}$`.

Merchants are created disabled. Enabling requires a valid downstream merchant identity, complete auth config, and an enabled payment option still offered by PG. Auth settings are locked while enabled or after transactions exist. Agree issuer/audience and a stable public JWKS URL before testing purchases. Return URL storage is not an implemented frontend auth callback.

## JWT contract

| Field | Simulator value / requirement |
| --- | --- |
| Header `alg` | `RS256`; RSA at least 2048 bits |
| Header `kid` | `JWT_KEY_ID`, also present in public JWKS |
| `iss` | `JWT_ISSUER`, byte-for-byte match with registered issuer |
| `aud` | `JWT_AUDIENCE`, matching registered audience |
| `sub` | Stable configured demo user ID, not an email or request body value |
| `merchant_code` | `MERCHANT_CODE`, matching the API merchant path |
| `iat`, `exp` | Epoch seconds; TTL 300 seconds |
| `name` | Optional display profile; never authorization input |

The inspected service permits RS256/ES256/EdDSA and maximum TTL 900 seconds with 30 seconds clock leeway; this simulator deliberately issues only RS256/300-second tokens. Use NTP. Stable subject is the ownership key: changing it creates a separate identity/history. There is no refresh token; request another token through the active merchant session.

## BFF forwarding guidelines

Accept bearer JWT from the FE and forward it unchanged to a **fixed configured** service base URL and merchant prefix. If the BFF itself makes identity-based decisions, verify signature, issuer, audience, expiry, algorithm and merchant first. Decoding JWT claims alone is insufficient.

Use a route/method allowlist, bounded timeouts, validated inputs, and server-side configured destinations. Never accept an arbitrary proxy URL, JWKS URL, merchant identity or upstream authorization from a request body. Do not forward merchant cookies, hop-by-hop headers, or internal credentials to the service. Preserve the service's status/envelope, request ID, and checkout `Idempotency-Key`.

The BFF is implemented by the receiving team; no BFF endpoints are included in the simulator. The current client routes are:

| Method | Service path suffix |
| --- | --- |
| GET | `/products`, `/products/{product_code}` |
| POST | `/inquiry`, `/checkout` |
| GET | `/transactions`, `/transactions/{transaction_id}` |

Always call inquiry before checkout; the product list does not expose inquiry requirement. Do not retry a checkout using a new idempotency key after a timeout. Use the same key and intent to recover the stored outcome. Prices, payment options, purchase schemas and fulfillment statuses must follow the service contract; the merchant simulator does not define them.

## JWKS operations

Publish public JWKS without cookies, redirect, IP restriction or Vercel deployment protection. The service must reach it within 3 seconds. The inspected service caches keys for five minutes, throttles refresh to 30 seconds, and can retain known keys up to one hour on fetch failures.

This release publishes one signing key. To rotate without interruption, first extend publishing to include both old and new public keys, publish the new public key, wait at least 5–10 minutes, switch signer, then retain the old public key for at least 15 minutes after its last use. Do not simply replace the single key during active testing. Multi-key rotation is not implemented in this release.

## Integration validation

1. Verify public JWKS from the service network (HTTP 200 JSON; no redirects/private fields).
2. Register matching merchant identity and auth values through the administrator.
3. Login merchant, mint token, and call `GET /api/v1/mini-app/{merchant_code}/transactions?limit=1` server-to-server.
4. Expect 200 for a valid token even when merchant is disabled; unknown merchant/invalid token returns 401. New business with disabled merchant returns 403 after valid authentication.
5. Test expiry, wrong audience/issuer, and isolation between two stable subjects. Separate auth success from purchase readiness.

Use `tools/smoke_auth.py` with `SMOKE_USERNAME` and `SMOKE_PASSWORD` supplied privately in the environment. Set `MERCHANT_PUBLIC_URL`, `MERCHANT_CODE` and `MINIAPP_API_BASE_URL`. The script does not create/enable merchants or print tokens. A 200 validates authenticated history access, not downstream payments or authorization of proposed contracts.
