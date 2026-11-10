# Murid Wukong Merchant Mini App Simulator

A Python/FastAPI merchant application with demo-user login, a browser Mini App container, an asymmetric JWT issuer, and a public JWKS endpoint. This is a simulator, not a GoPay integration or a PPOB frontend.

Start with the [integration documentation](docs/README.md), including separate [frontend](docs/frontend-integration.md) and [backend](docs/backend-integration.md) guidelines.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/setup_local.py
.venv/bin/uvicorn app:app --reload --port 8000
```

Open **http://localhost:8000** (use the exact host configured in `.env`). Login as `demo` using the password entered during setup. Until the PPOB frontend is available, click **Uji bridge dengan receiver demo**.

Set `MINIAPP_FRONTEND_URL` to the frontend entrypoint when it is ready. The receiving frontend must implement the bridge and allow framing by the merchant origin. Restart the local server after changing environment configuration.

```sh
.venv/bin/python -m pytest -q
```

No database, background workers, downstream admin credentials, or production payments are part of this application. All account data, signing keys and sessions are independent of MyVIA. No source changes in `bevia-miniapp-service` are required.

UI preview: [mobile screenshot](docs/merchant-mobile.png). Actual checks and pending external integration: [verification record](docs/verification.md).
