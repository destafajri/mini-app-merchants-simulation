# Murid Wukong Merchant Mini App Simulator

A Python/FastAPI merchant application with demo-user login, a browser Mini App container, an asymmetric JWT issuer, and a public JWKS endpoint. This is a simulator, not a GoPay integration or a PPOB frontend. It offers two authentication modes: the original JWT/JWKS mode and an additional GoPay-like `auth_code` exchange mode.

Start with the [integration documentation](docs/README.md), including separate [frontend](docs/frontend-integration.md) and [backend](docs/backend-integration.md) guidelines.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/setup_local.py
.venv/bin/uvicorn app:app --reload --port 8000
```

## Login credentials

| Setting | Value |
| --- | --- |
| Local URL | **http://localhost:8000** |
| Usernames | **`demo`, `demo2`, `demo3`, `demo4`, `demo5`, `demo6`, `demo7`, `demo8`, `demo9`, `demo10`** |
| Password for all ten accounts | Value of **`DEMO_USER_PASSWORD`** in `.env` / Vercel environment. Setup initially writes `MuridWukongDemo123!`; edit it to choose your password. |
| Account fixture | [`fixtures/demo_users.json`](fixtures/demo_users.json) — synthetic profiles and stable IDs; no passwords or password hashes |

Profiles and IDs are bundled with the repository. All ten users share the password configured on each deployment; local and Vercel passwords can differ. Set it in the ignored `.env` file:

```dotenv
DEMO_USER_PASSWORD=your-chosen-demo-password
```

Restart the local server after changing it. On Vercel, add the same variable in Project Settings → Environment Variables and redeploy. There is no hardcoded password fallback: missing/empty password configuration refuses login with 503. The setup helper is non-interactive and writes an initial example password to `.env`; change it before sharing the deployment. Existing `DEMO_USERS_JSON` values are ignored and can be removed. These are synthetic test accounts, not real user registration.

After login, click **Uji bridge dengan receiver demo** to test authentication before the PPOB frontend is available.

Four environment variables are required for the full demo: `MERCHANT_PUBLIC_URL`, `JWT_PRIVATE_KEY_PEM`, `SESSION_SECRET` and `DEMO_USER_PASSWORD`. Generate the local key/secret with the setup helper; for Vercel enter these values in the project environment and change the merchant URL to its stable HTTPS domain.

Set `MINIAPP_FRONTEND_URL` to the frontend entrypoint when it is ready. The receiving frontend must implement the bridge and allow framing by the merchant origin. Restart the local server after changing environment configuration.

## GoPay-like auth_code mode

In addition to the JWT mode, the simulator mimics the shape of the GoPay/Midtrans "User Authentication" flow: the browser asks the host for a short-lived `auth_code`, and a **server** exchanges it with the host's token endpoint.

1. The Mini App frontend calls `getAuthCode()` from `merchant-bridge.js` (message pair `miniapp.authcode.request` / `miniapp.authcode.response`); the container calls `POST /api/gopay/auth-code` with the login session and returns `{authCode, expiresIn: 300}`.
2. The Mini App server calls `POST /v1/mini-apps/authorizations/token` with `Authorization: Basic <GOPAY_SIM_BASIC_CREDENTIAL>` and `{"auth_code": "..."}` and receives `{"success": true, "data": {"auth_token": "...", "gopay_account_id": "demo-user-001"}}`.

Set `GOPAY_SIM_BASIC_CREDENTIAL` (secret; see `.env.example`) to enable the exchange; without it the endpoint answers 503. The code is a stateless signed value valid for 300 seconds and is **not single-use** (serverless keeps no state). The existing JWT endpoints are unchanged. Details: [API reference](docs/api-reference.md#gopay-like-auth_code-mode), [backend guide](docs/backend-integration.md#gopay-like-auth_code-exchange). The real GoPay behavior was not verified.

```sh
.venv/bin/python -m pytest -q
node tests/test_bridge.mjs && node tests/test_bridge_authcode.mjs && node tests/test_preferences.mjs
```

No database, background workers, downstream admin credentials, or production payments are part of this application. All account data, signing keys and sessions are independent of MyVIA. No source changes in `bevia-miniapp-service` are required.

UI preview: [mobile screenshot](docs/merchant-mobile.png) and [login/home/container gallery](docs/ui-preview.md). Actual checks and pending external integration: [verification record](docs/verification.md).

Appearance and language: use the header toggles for **Light / Dark** and **ID / EN**. Preferences persist in this browser. The initial theme follows the system appearance; language defaults to Indonesian. The built-in receiver follows these preferences; an external VIA frontend manages its own theme/language.
