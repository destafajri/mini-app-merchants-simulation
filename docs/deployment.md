# Configuration and deployment

## Local setup

Follow root README. `tools/setup_local.py` asks for a password (minimum 12 characters), generates a private RSA key and session secret, and writes an ignored `.env` with owner-only permissions. It refuses to overwrite an existing file. Run it from the repository root. It creates username `demo`, subject `demo-user-001` and a scrypt password hash. Do not commit `.env` or print it into logs.

## Environment reference

Required below means needed for the complete login, JWT/JWKS and bridge demo. Settings are read when the corresponding route is called; `/api/health` alone does not prove they are configured.

| Name | Requirement | Purpose and value source |
| --- | --- | --- |
| `MERCHANT_PUBLIC_URL` | Required | URL of this merchant simulator. The browser origin must match it for login/logout/token requests. Use the stable Vercel domain without trailing slash, or `http://localhost:8000` locally. It is not the VIA frontend or Go service URL. |
| `MERCHANT_CODE` | Required for tokens | Stable merchant identity included in JWT `merchant_code`. Use `murid_wukong_demo`, matching the registered Go service merchant and API path. |
| `JWT_ISSUER` | Required for tokens | Identity of the token issuer, included in `iss`. Initially use the stable merchant URL; it must exactly match service registration. Do not derive it from changing preview hosts. |
| `JWT_AUDIENCE` | Required for tokens | Intended token recipient, included in `aud`. Use `bevia-miniapp` unless a different value was agreed and registered in the service. This is a logical identifier, not a URL to call. |
| `JWT_KEY_ID` | Required for tokens and JWKS | Public signing-key identifier, included in JWT header and JWKS as `kid`. Use `murid-wukong-demo-v1`; it is not a private key or password. |
| `JWT_PRIVATE_KEY_PEM` | Required for tokens and JWKS; secret | RSA private key (minimum 2048 bits) used to sign JWTs and derive the public JWKS. Generate with setup helper. Actual newlines or literal `\\n` accepted. Never send this to FE or service administrators. |
| `SESSION_SECRET` | Required for sessions; secret | Random secret used to sign merchant login cookies. Generate with setup helper (32+ random bytes); keep stable across instances. It is separate from the JWT RSA key. Changing it invalidates existing sessions. |
| `DEMO_USERS_JSON` | Required for usable login; server-only | Configured accounts: stable `id`, display `name`, `username`, `password_hash`. Generate using setup helper. Empty `[]` has no accounts and cannot log in. Never put plaintext passwords in this value. |
| `MINIAPP_FRONTEND_URL` | Optional until external FE integration | Full VIA FE URL loaded inside the container. Blank disables external launcher but permits built-in receiver testing. Required to open the real FE; FE must implement bridge and allow merchant framing. |
| `MINIAPP_API_BASE_URL` | Optional for application runtime | Go service origin or HTTPS tunnel used only by `tools/smoke_auth.py`. Required when running that script; not a runtime proxy or iframe destination. |

For **login only**, configure `MERCHANT_PUBLIC_URL`, `SESSION_SECRET` and a non-empty `DEMO_USERS_JSON`. For **receiver demo or external bridge token issuance**, configure all eight required variables above. The public JWKS endpoint needs the RSA key and key ID. No backend URL is necessary for the receiver demo.

To set up Vercel, generate `.env` locally, then enter its values in Project Settings → Environment Variables → Production. Replace the generated localhost merchant URL and issuer with the chosen stable deployment URL. Paste values without `NAME=` or outer dotenv single quotes; preserve JSON double quotes. Save and redeploy. The `.env.example` file is documentation and does not populate Vercel automatically.

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
