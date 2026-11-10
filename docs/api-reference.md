# Merchant HTTP API v1

Base URL: `MERCHANT_PUBLIC_URL`. These are simulator endpoints, not Mini App service endpoints. Interactive schemas: `/docs`; OpenAPI: `/openapi.json`. There is no cross-origin CORS policy: login and token minting are called by the same-origin merchant parent.

## Common behavior

JSON request bodies use `Content-Type: application/json`. Every response carries `Cache-Control: no-store`. Mutating endpoints require `Origin` equal to the configured merchant origin; missing/wrong origin returns 403 with `{"detail":{"code":"ORIGIN_REJECTED"}}`.

Protected routes use the HttpOnly `merchant_session` cookie. Missing, invalid, expired or unknown-user session returns 401 `UNAUTHENTICATED`. Configuration absent returns 503 `CONFIGURATION_REQUIRED` with the missing field name, never its value. Invalid URL configuration returns 503; invalid request schema returns FastAPI 422 `detail` validation entries. Unexpected server errors must be investigated server-side, without exposing secrets to callers.

## POST /api/auth/login

Request:

```json
{"username":"demo","password":"<value of DEMO_USER_PASSWORD>"}
```

Success 200 sets the session cookie (eight-hour lifetime) and returns `{"id":"demo-user-001","name":"Demo User"}`. Username/password length limits are 128/256 characters; minimum length one. Accounts are loaded from `fixtures/demo_users.json` (`demo`, `demo2` through `demo10`, all with the shared password from `DEMO_USER_PASSWORD`). The fixture contains profiles only. Missing/empty `DEMO_USER_PASSWORD` returns 503 `CONFIGURATION_REQUIRED`. Wrong credentials: 401 `INVALID_CREDENTIALS`. Do not automate repeated attempts; configure perimeter rate limiting before public use.

## GET /api/auth/me

Requires session. Success 200 returns `{"id":"demo-user-001","name":"Demo User"}`. Does not return hashes or tokens.

## POST /api/auth/logout

Requires exact Origin; accepts empty body or `{}`. Returns 200 `{"success":true}` and expires the cookie, including if already logged out. Does not revoke bearer tokens or stolen copies of stateless cookies.

## POST /api/miniapp/token

Requires session and exact Origin. No body is needed; identity is resolved exclusively from the session. Supplied user ID fields have no effect. Returns 200:

```json
{"access_token":"<signed JWT>","token_type":"Bearer","expires_in":300,"merchant_code":"murid_wukong_demo"}
```

No refresh token is issued. A new call issues a fresh five-minute token for the same stable subject. This endpoint is consumed by the merchant parent, not directly by the iframe.

## GET /.well-known/jwks.json

Public, no cookie or Origin required. Success 200:

```json
{"keys":[{"kty":"RSA","kid":"murid-wukong-demo-v1","use":"sig","alg":"RS256","n":"<base64url modulus>","e":"AQAB"}]}
```

Requires valid configured signing key and key ID. Never includes private RSA members.

## GET /api/config

Public, returns `frontend_url`, `frontend_origin`, `merchant_origin`. Empty FE URL yields `"frontend_url":"","frontend_origin":null`; merchant origin still requires valid configuration. No secrets are returned.

## GET /api/health

Public liveness: 200 `{"status":"ok","service":"merchant-simulator"}`. Does not test auth configuration, downstream readiness or JWKS reachability.

## Browser assets

`GET /` serves the merchant UI. `GET /receiver` serves the same-origin test receiver. `GET /merchant-bridge.js` serves the ES module SDK. `GET /ui-preferences.js` serves the simulator-only theme/language helper; it contains no credentials and does not modify the bridge protocol. Merchant page disallows framing; receiver permits same-origin framing only. No token is exposed by these asset responses.
