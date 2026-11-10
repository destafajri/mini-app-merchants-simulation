# Troubleshooting

| Symptom | Checks |
| --- | --- |
| Login fails | Use demo or demo2 through demo10 with the value of DEMO_USER_PASSWORD in this deployment. Profiles come from fixtures/demo_users.json. Missing/empty password configuration returns 503. Restart/redeploy after changes; check session secret and merchant origin. |
| 403 ORIGIN_REJECTED | Browser address origin must match MERCHANT_PUBLIC_URL exactly. localhost and 127.0.0.1 differ; preview domain and stable domain differ. |
| VIA disabled | MINIAPP_FRONTEND_URL is blank. Use receiver demo until FE is available. |
| Blank/refused iframe | Inspect FE CSP frame-ancestors and X-Frame-Options. Confirm HTTPS, route and external deployment protection. |
| Handshake timeout | FE must call SDK inside iframe. Confirm exact merchantOrigin and configured frontend origin. Use receiver demo to isolate parent/backend from external FE. |
| Cross-origin SDK import blocked | Bundle a copy of merchant-bridge.js with the FE; cross-origin module serving is not enabled. |
| Token unavailable | Check server-only RSA key, key ID, issuer/audience, user configuration and session. Never paste keys/tokens into a ticket. |
| Mini App 401 | Verify merchant exists, code, issuer, audience, kid, JWKS and clocks. Token mint success alone does not establish service acceptance. |
| Mini App AUTH_UNAVAILABLE | Fetch public JWKS from service network; check DNS, timeout, redirects and deployment protection. |
| Mini App 403 | A valid token may belong to a disabled merchant; distinguish this from auth failure. |
| Browser API CORS error | Implement/use FE's BFF; bridge does not add CORS to the Go API. |
| Vercel cannot reach backend | Laptop localhost is not reachable; use a configured HTTPS tunnel. |
| Auth works but purchase fails | Check merchant enablement, Product/Order identity, enabled payment option, PG and downstream integration separately. |

When reporting a fault, include route, sanitized error code, timestamp and upstream request ID where available. Do not include passwords, JWTs, cookies, account hashes, private keys or raw headers. A successful receiver test proves the simulator bridge path only. A successful authenticated history read proves service auth access only, not payment integration.
