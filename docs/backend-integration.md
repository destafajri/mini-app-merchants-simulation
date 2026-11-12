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

## GoPay-like auth_code exchange

An alternative to the JWT contract, for a Mini App server that implements the GoPay/Midtrans-shaped flow. The frontend obtains an `authCode` from the container (see the [frontend guide](frontend-integration.md#gopay-like-auth_code-bridge)) and sends it to the Mini App server, which exchanges it:

```sh
curl -X POST "$MERCHANT_PUBLIC_URL/v1/mini-apps/authorizations/token" \
  -H "Authorization: Basic $GOPAY_SIM_BASIC_CREDENTIAL" \
  -H "Content-Type: application/json" -H "Request-Id: <optional, <= 100 chars>" \
  -d '{"auth_code":"<authCode>"}'
```

Success is 200 `{"success":true,"data":{"auth_token":"...","gopay_account_id":"demo-user-001"}}`. `gopay_account_id` is the stable subject to use as the ownership key (the same IDs as the JWT `sub`). A failed code returns 400 `AuthCode Not Found`; a wrong credential 401 `Unauthorized`; 5xx is the only retriable class. Guidelines:

- Hold `GOPAY_SIM_BASIC_CREDENTIAL` only on the server that exchanges codes; never in the frontend, the BFF response, logs or analytics. Treat the `authCode` and `auth_token` the same way (the code is short-lived but secret while valid).
- Exchange immediately after receiving the code; it expires 300 seconds after issue. Do not assume single use: the simulator cannot prevent replay within that window, while the real provider's replay rule is not verified here.
- The `auth_token` is signed and never expires; the simulator defines no endpoint that consumes it. Persist it only if your design needs it and protect it like a credential.
- Call from a server, with bounded timeouts, to the configured merchant URL only.

This mode needs `SESSION_SECRET` and `GOPAY_SIM_BASIC_CREDENTIAL`; it does not need the RSA key. The JWT mode is unchanged and can be used at the same time.

### Using it with `bevia-miniapp-service`

The Mini App service redeems the code itself (authenticator key `authcode_v1`) and answers with its own short session token, which the frontend then sends as the bearer. Each merchant of this kind has its **own** host and credential: the administrator enters them per merchant through the service's admin API, and the service stores the credential encrypted. Nothing about this simulator is configured in the service's environment. The service's `docs/merchant-integration.md` has the endpoint contract.

For this simulator the merchant code is `wukong_apps`, the host (`base_url`) is the simulator's origin and the credential is the exact value of `GOPAY_SIM_BASIC_CREDENTIAL`, with no base64 re-encoding. A merchant of this kind carries no issuer, audience or JWKS URL, so the administrator registers it with the authenticator key only:

```json
{
  "code": "wukong_apps",
  "name": "Wukong Apps",
  "downstream_merchant_id": "<UUID supplied by Product/Order owners>",
  "auth": { "authenticator_key": "authcode_v1" }
}
```

Then, with the credential typed into a secret variable and never into a note or chat:

```text
PUT /api/v1/admin/mini-app/merchants/{merchant_id}/auth-provider
{ "base_url": "https://<this simulator origin>", "credential": "<GOPAY_SIM_BASIC_CREDENTIAL>" }
```

Both fields are always required. A later `GET` on the same path shows only whether a credential is set. Payment options and `PUT .../enable` follow as for any merchant; enabling is refused until the provider is stored.

The service answers `POST /api/v1/mini-app/{merchant_code}/session` with `{"auth_code":"..."}` and returns `{access_token, token_type: "Bearer", expires_in}`. An unknown merchant, a disabled merchant, a merchant on another authenticator and a rejected code all answer `401`; the host is called only for an enabled `authcode_v1` merchant.

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

Use `tools/smoke_auth.py` with `SMOKE_USERNAME` and `SMOKE_PASSWORD` supplied privately in the environment. Set `MERCHANT_PUBLIC_URL` and `MINIAPP_API_BASE_URL`. `MERCHANT_CODE` defaults to `murid_wukong_demo`; override only for a different registered merchant. Demo usernames are listed in the root README; provide the password from the simulator deployment's `DEMO_USER_PASSWORD` as `SMOKE_PASSWORD`. The script does not create/enable merchants or print tokens. A 200 validates authenticated history access, not downstream payments or authorization of proposed contracts.
