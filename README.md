# Murid Wukong Merchant Mini App Simulator

A Python/FastAPI merchant application with demo-user login, a browser Mini App container, an asymmetric JWT issuer, and a public JWKS endpoint. This is a simulator, not a GoPay integration or a PPOB frontend.

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
| Password for all ten accounts | **`MuridWukongDemo123!`** |
| Account fixture | [`fixtures/demo_users.json`](fixtures/demo_users.json) — synthetic profiles, stable IDs, and password hashes |

These are intentionally public simulator credentials, identical locally and on Vercel. No registration or user environment variable is needed. Do not use them for real accounts or sensitive data. The setup helper generates private signing configuration only; it no longer prompts for a password. Existing `DEMO_USERS_JSON` environment values are ignored and can be removed. Previous workstation-generated login passwords are no longer used.

After login, click **Uji bridge dengan receiver demo** to test authentication before the PPOB frontend is available.

Only three environment variables are required: `MERCHANT_PUBLIC_URL`, `JWT_PRIVATE_KEY_PEM` and `SESSION_SECRET`. Generate the local key/secret with the setup helper; for Vercel enter these values in the project environment and change the merchant URL to its stable HTTPS domain.

Set `MINIAPP_FRONTEND_URL` to the frontend entrypoint when it is ready. The receiving frontend must implement the bridge and allow framing by the merchant origin. Restart the local server after changing environment configuration.

```sh
.venv/bin/python -m pytest -q
```

No database, background workers, downstream admin credentials, or production payments are part of this application. All account data, signing keys and sessions are independent of MyVIA. No source changes in `bevia-miniapp-service` are required.

UI preview: [mobile screenshot](docs/merchant-mobile.png). Actual checks and pending external integration: [verification record](docs/verification.md).
