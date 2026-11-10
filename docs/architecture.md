# Architecture and responsibilities

## Roles

| Component | Responsibility |
| --- | --- |
| Merchant simulator backend | Login its repository fixture demo users, issue signed session cookies, mint short-lived Mini App JWTs, publish public JWKS. |
| Merchant page | Display the launcher, host the configured iframe, validate bridge messages, retrieve JWT using the merchant session. |
| VIA Mini App frontend (separate team) | Render PPOB UI, request JWT through the SDK, keep token in memory, call its own backend/BFF. |
| Mini App BFF (separate team) | Accept bearer token from FE and forward it to the configured Mini App service; never turn unverified claims into trusted identity. |
| bevia-miniapp-service | Verify merchant JWT using registered JWKS, enforce merchant/user ownership, orchestrate Product/Order/PG integrations. |

The simulator does not implement products, inquiry, checkout, payment reconciliation, user registration, balances, or the Mini App BFF. No Go service is modified.

## Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant M as Merchant page
    participant S as Merchant Python backend
    participant F as VIA iframe
    participant B as VIA BFF
    participant A as Mini App API
    U->>M: Login
    M->>S: POST /api/auth/login
    S-->>M: HttpOnly signed session cookie
    U->>M: Click VIA
    M->>F: Load configured frontend URL
    F->>M: miniapp.auth.request via postMessage
    M->>M: Verify exact origin and iframe window
    M->>S: POST /api/miniapp/token + cookie
    S-->>M: RS256 JWT (300 seconds)
    M-->>F: miniapp.auth.response to exact origin
    F->>B: API request + Bearer JWT
    B->>A: Forward Bearer JWT
    A->>S: GET /.well-known/jwks.json (cached)
    A->>A: Verify claims, merchant and user ownership
    A-->>B: Actual API result
    B-->>F: API result
```

## Boundaries

The native GoPay seamless-login SDK is not used. The browser iframe and postMessage interface simulate the container interaction; they are not GoPay protocol compatibility. Real GoPay integration requires onboarding and its own SDK. See official [container](https://docs.midtrans.com/reference/migration-guides) and [seamless login](https://docs.midtrans.com/reference/seamless-login-v2) documentation.

A signed session is stateless and expires after eight hours. Logout removes the browser cookie; it does not revoke copied cookies or previously minted JWTs. JWTs expire after five minutes. There is no central revocation store. The backend configuration and deployed fixture revision must stay identical across instances. Ten public synthetic accounts live in `fixtures/demo_users.json`; no account environment variable is used.
