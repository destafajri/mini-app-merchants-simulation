# Configuration and deployment

## Local setup

Follow root README. `tools/setup_local.py` asks for a password (minimum 12 characters), generates a private RSA key and session secret, and writes an ignored `.env` with owner-only permissions. It refuses to overwrite an existing file. Run it from the repository root. It creates username `demo`, subject `demo-user-001` and a scrypt password hash. Do not commit `.env` or print it into logs.

## Environment reference

| Name | Purpose |
| --- | --- |
| `MERCHANT_PUBLIC_URL` | Canonical merchant URL; exact browser origin for mutation checks. Local default from setup is `http://localhost:8000`. |
| `MERCHANT_CODE` | Stable merchant code registered in the Mini App service. |
| `MINIAPP_FRONTEND_URL` | Full FE entrypoint URL; blank means external launcher disabled. |
| `JWT_ISSUER` | Stable exact issuer registered with the service; independent from preview deployment hostnames. |
| `JWT_AUDIENCE` | Exact registered audience, normally `bevia-miniapp`. |
| `JWT_KEY_ID` | Public `kid` identifying the configured signer. |
| `JWT_PRIVATE_KEY_PEM` | Server-only unencrypted RSA PEM; actual newlines or literal `\n` accepted. |
| `SESSION_SECRET` | Server-only cryptographically random value (use 32+ random bytes); stable across instances. |
| `DEMO_USERS_JSON` | Server-only JSON array of accounts containing `id`, `name`, `username`, `password_hash`. |
| `MINIAPP_API_BASE_URL` | Smoke-check service origin, e.g. an HTTPS tunnel URL. Not used to proxy frontend requests. |

Demo account shape:

```json
[{"id":"demo-user-001","name":"Demo User","username":"demo","password_hash":"scrypt$<salt hex>$<derived hash hex>"}]
```

Hash algorithm: Python `hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)` encoded as hex. Keep IDs unique and stable; usernames unique. Use the setup helper to produce correctly shaped local config. Changing a user's password does not revoke an existing signed session; rotate the session secret if revocation is required (all users sign in again).

## Vercel

1. Import this component repository into Vercel. Select `main` as the production branch.
2. Use FastAPI framework detection, root directory `.`, entrypoint `app.py`, dependencies from `requirements.txt`. No database or persistent filesystem is required. [Official FastAPI deployment guide](https://vercel.com/docs/frameworks/backend/fastapi)
3. Configure environment variables privately in Vercel, including a stable merchant domain, signing key, session secret and demo account hashes. `.env.example` contains placeholders only. Preview and production must use their own consistent URL/configuration.
4. Configure `MINIAPP_FRONTEND_URL` when the FE team provides it. Redeploy after environment changes.
5. Ensure the registered JWKS URL is publicly reachable without deployment protection or redirects. Coordinate the project's protection settings with its owner; never expose credentials to bypass protection.
6. Check `/api/health`, public JWKS, login, test receiver and external FE container. Register the merchant separately in the Mini App service.

The repository is deployment-ready source, not proof of a deployed Vercel application. No Vercel deployment is performed automatically.

## Local backend and tunnel

A deployed server cannot reach the laptop's `localhost`. Expose the local Mini App HTTP service through an operator-managed HTTPS tunnel, then configure that URL in the receiving BFF or smoke check. Keep admin routes and operational endpoints protected at the tunnel/reverse proxy. Do not disable service authentication to make a test pass.

The reverse direction also matters: the local Go service fetches the simulator's public JWKS URL. If running the merchant locally without Vercel, use a reachable merchant tunnel or configure the local service's development HTTP allowance deliberately. Do not substitute a laptop loopback URL for a reachable address inside Docker.

## Operating limits and rollback

This is a developer sandbox. No account lockout, distributed rate limiter, session revocation store or password reset is implemented. Before public exposure configure rate limiting at the edge and use non-production identities. No real funds should depend on this simulator. Hostile scripts on a trusted FE origin can request JWTs, so treat the configured FE origin as trusted code.

Changing configuration or redeploying the prior commit rolls back the simulator. Changing issuer, merchant code, or keys can break verification and ownership; coordinate with service administrators. Do not regenerate signing keys on startup. See backend guidelines for the unimplemented multi-key rotation requirement.
