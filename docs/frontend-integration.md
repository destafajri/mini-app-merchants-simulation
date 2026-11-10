# Frontend integration guidelines

## Prerequisites

Obtain these values from the merchant operator:

- Stable merchant origin, for example `https://merchant.example`.
- Bridge SDK URL: `https://merchant.example/merchant-bridge.js`.
- VIA BFF URL agreed with the backend team.

Give the merchant operator the final FE entrypoint URL. They configure `MINIAPP_FRONTEND_URL`. Configure your response headers to allow this merchant origin with `Content-Security-Policy: frame-ancestors https://merchant.example`. An incompatible `X-Frame-Options: DENY` or `SAMEORIGIN` prevents cross-origin embedding. Never loosen framing for arbitrary origins.

The container supplies `sandbox="allow-scripts allow-same-origin allow-forms"`. Popups, top navigation, native payment launches and downloads are not enabled. Discuss any additional capability before depending on it. This release supports an HTTP(S) web entrypoint, not custom native URL schemes.

## Quick start

Copy the versioned SDK source into your FE build or import it from the merchant deployment. When loading cross-origin, bundle the copy locally: the simulator does not expose cross-origin module CORS headers.

```javascript
import { createMerchantBridge } from './merchant-bridge.js';

const bridge = createMerchantBridge({
  merchantOrigin: import.meta.env.VITE_MERCHANT_ORIGIN
});
let auth; // Memory only; clear when leaving the Mini App.

async function getToken() {
  if (!auth || Date.now() >= auth.refreshAt) {
    const result = await bridge.getAccessToken();
    auth = { token: result.access_token,
             refreshAt: Date.now() + (result.expires_in - 30) * 1000 };
  }
  return auth.token;
}

async function loadHistory() {
  const token = await getToken();
  return fetch('/api/miniapp/transactions?limit=20', {
    headers: { Authorization: `Bearer ${token}` }
  }); // Example BFF route; the FE/BE team implements it.
}
```

The `VITE_` variable is an example for Vite; use your framework's equivalent public configuration. The merchant origin is public, not a secret. No signing key, account hash, session secret or backend credential belongs in FE environment variables.

`createMerchantBridge({ merchantOrigin })` requires an exact origin without trailing slash, path, query or fragment. `getAccessToken()` returns a Promise and rejects after 10 seconds. Request a token after mounting inside the container. No second login form is needed.

## Bridge v1 wire contract

Request from iframe to parent:

```json
{"type":"miniapp.auth.request","request_id":"<random UUID>"}
```

Success response from parent to iframe:

```json
{
  "type":"miniapp.auth.response",
  "request_id":"<same UUID>",
  "data": {
    "access_token":"<JWT>",
    "token_type":"Bearer",
    "expires_in":300,
    "merchant_code":"murid_wukong_demo"
  }
}
```

Failure response:

```json
{"type":"miniapp.auth.response","request_id":"<same UUID>","error":{"code":"UNAUTHENTICATED"}}
```

Parent validates exact configured FE origin, `event.source === iframe.contentWindow`, request type and bounded request ID. SDK validates exact merchant origin, parent window, response type, matching request ID and response fields. Other messages are ignored. Only one token request is processed by the parent at a time; serialize requests in the FE, including refreshes. Pending requests can time out if the container closes or navigates.

## Token and failure handling

| Error | FE action |
| --- | --- |
| `CONTAINER_REQUIRED` | Open through merchant launcher; standalone FE has no merchant session bridge. |
| `BRIDGE_TIMEOUT` | Verify parent origin, URL, framing policy and SDK installation. Offer retry. |
| `UNAUTHENTICATED` | Ask user to return to merchant and login again. |
| `TOKEN_UNAVAILABLE` | Show temporary failure, offer explicit retry; operator checks configuration. |
| Mini App API `401` | Discard token, obtain a fresh one; retry a read once. Escalate repeated failure. |
| Mini App API `403` | Do not loop token refresh: merchant may be disabled. Show API code. |
| Mini App API `503` | Distinguish JWKS failure from other dependencies using the actual API code. |

Keep JWTs in memory, never in URL, console, analytics or persistent browser storage. Receiving/decoding a JWT is not signature verification. The service verifies it. An old response must not overwrite a newer auth state.

The current Go API has no CORS handling. Call your own BFF; it forwards the token server-to-server. Direct cross-origin browser requests are not established by this simulator. The bridge only supplies authentication and does not transport purchase requests.

## Acceptance checklist

- [ ] FE embeds from the exact configured URL and allows the merchant origin.
- [ ] Auth succeeds without another login form; two demo users receive different stable subjects.
- [ ] Wrong origin/source/request ID cannot resolve a pending request.
- [ ] Expiry refresh, session expiry, container close and timeout have usable UX.
- [ ] BFF forwards bearer token; 401/403/503 remain distinguishable.
- [ ] Tokens and credentials are absent from URLs, logs, analytics and persistent storage.
