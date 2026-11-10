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

```sh
.venv/bin/python -m pytest -q
```

No database, background workers, downstream admin credentials, or production payments are part of this application. All account data, signing keys and sessions are independent of MyVIA. No source changes in `bevia-miniapp-service` are required.

UI preview: [mobile screenshot](docs/merchant-mobile.png) and [login/home/container gallery](docs/ui-preview.md). Actual checks and pending external integration: [verification record](docs/verification.md).
