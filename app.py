"""Stateless demo merchant identity provider and browser container."""
import hmac
import json
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from itsdangerous import BadData, BadSignature, SignatureExpired, URLSafeSerializer, URLSafeTimedSerializer
from pydantic import BaseModel, ConfigDict, Field, ValidationError

load_dotenv()
ROOT = Path(__file__).parent
app = FastAPI(title="Merchant Simulator", version="1.0.0")
COOKIE = "merchant_session"
AUTH_CODE_TTL = 300
EXCHANGE_PATH = "/v1/mini-apps/authorizations/token"
DEFAULTS = {
    "MERCHANT_CODE": "murid_wukong_demo",
    "JWT_AUDIENCE": "bevia-miniapp",
    "JWT_KEY_ID": "murid-wukong-demo-v1",
}


def setting(name):
    """Require deployment secrets and URL; use explicit simulator identity defaults."""
    value = os.getenv(name, "") or DEFAULTS.get(name, "")
    if not value and name == "JWT_ISSUER":
        value = setting("MERCHANT_PUBLIC_URL")
    if not value:
        raise HTTPException(503, detail={"code": "CONFIGURATION_REQUIRED", "field": name})
    return value


def origin(url):
    """Return a validated browser origin for configured web URLs."""
    parsed = urlsplit(url)
    if parsed.username or parsed.password or not parsed.hostname or parsed.scheme not in ("http", "https"):
        raise HTTPException(503, detail={"code": "INVALID_URL_CONFIGURATION"})
    if parsed.scheme != "https" and parsed.hostname not in ("localhost", "127.0.0.1"):
        raise HTTPException(503, detail={"code": "HTTPS_REQUIRED"})
    return f"{parsed.scheme}://{parsed.netloc}"


def users():
    """Load repository-owned synthetic accounts, independent of environment variables."""
    return json.loads((ROOT / "fixtures/demo_users.json").read_text())


def signer(salt="merchant-session-v1"):
    """Use a stable secret across serverless instances; each salt is a separate token namespace."""
    return URLSafeTimedSerializer(setting("SESSION_SECRET"), salt=salt)


def code_signer():
    """Short-lived GoPay-like auth codes; never interchangeable with the login cookie."""
    return signer("gopay-auth-code-v1")


def token_signer():
    """Non-expiring GoPay-like auth tokens (no timestamp, own salt)."""
    return URLSafeSerializer(setting("SESSION_SECRET"), salt="gopay-auth-token-v1")


def identity(request):
    """Resolve only configured users from a bounded signed session."""
    try:
        uid = signer().loads(request.cookies.get(COOKIE, ""), max_age=28800)
    except (BadSignature, SignatureExpired):
        raise HTTPException(401, detail={"code": "UNAUTHENTICATED"})
    for user in users():
        if user["id"] == uid:
            return user
    raise HTTPException(401, detail={"code": "UNAUTHENTICATED"})


def csrf(request):
    """Reject cross-origin mutations including requests without an Origin header."""
    if request.headers.get("origin") != origin(setting("MERCHANT_PUBLIC_URL")):
        raise HTTPException(403, detail={"code": "ORIGIN_REJECTED"})


def private_key():
    """Load the configured RSA signing key; reject undersized or wrong key types."""
    key = serialization.load_pem_private_key(setting("JWT_PRIVATE_KEY_PEM").replace("\\n", "\n").encode(), password=None)
    if not isinstance(key, rsa.RSAPrivateKey) or key.key_size < 2048:
        raise HTTPException(503, detail={"code": "INVALID_SIGNING_KEY"})
    return key


class Login(BaseModel):
    """Bound login input size."""
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=256)


class Exchange(BaseModel):
    """Strict, bounded server-to-server exchange input."""
    model_config = ConfigDict(extra="forbid")
    auth_code: str = Field(min_length=1, max_length=2048)


def gopay_error(status, description, request_id=None):
    """Provider-style failure body; descriptions never reveal why a code was rejected."""
    return JSONResponse({"success": False, "error": {"description": description}}, status_code=status, headers={"Request-Id": request_id} if request_id else None)


def header_ok(value):
    """Optional correlation headers must be short printable ASCII."""
    return value is None or (0 < len(value) <= 100 and value.isascii() and value.isprintable())


@app.middleware("http")
async def privacy(request: Request, call_next):
    """Prevent sensitive response caching and deny embedding the merchant itself."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self'" if request.url.path == "/receiver" else "frame-ancestors 'none'"
    return response


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "merchant-simulator"}


@app.post("/api/auth/login")
def login(body: Login, request: Request, response: Response):
    csrf(request)
    expected_password = setting("DEMO_USER_PASSWORD")
    for user in users():
        if hmac.compare_digest(user["username"].encode(), body.username.encode()) and hmac.compare_digest(body.password.encode(), expected_password.encode()):
            response.set_cookie(COOKIE, signer().dumps(user["id"]), httponly=True, secure=origin(setting("MERCHANT_PUBLIC_URL")).startswith("https:"), samesite="lax", max_age=28800)
            return {"id": user["id"], "name": user["name"]}
    raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS"})


@app.get("/api/auth/me")
def me(request: Request):
    user = identity(request)
    return {"id": user["id"], "name": user["name"]}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    csrf(request)
    response.delete_cookie(COOKIE)
    return {"success": True}


@app.post("/api/miniapp/token")
def token(request: Request):
    csrf(request)
    user = identity(request)
    now = int(time.time())
    merchant = setting("MERCHANT_CODE")
    claims = dict(iss=setting("JWT_ISSUER"), aud=setting("JWT_AUDIENCE"), sub=user["id"], merchant_code=merchant, iat=now, exp=now + 300, name=user["name"])
    encoded = jwt.encode(claims, private_key(), algorithm="RS256", headers={"kid": setting("JWT_KEY_ID")})
    return {"access_token": encoded, "token_type": "Bearer", "expires_in": 300, "merchant_code": merchant}


@app.post("/api/gopay/auth-code")
def gopay_auth_code(request: Request):
    """Browser-facing: issue a stateless 300-second auth code for the signed-in user."""
    csrf(request)
    user = identity(request)
    return {"authCode": code_signer().dumps(user["id"]), "expiresIn": AUTH_CODE_TTL}


@app.post(EXCHANGE_PATH)
async def gopay_exchange(request: Request):
    """Server-to-server (not browser-facing, no CORS): exchange an auth code for a non-expiring auth token."""
    expected = setting("GOPAY_SIM_BASIC_CREDENTIAL")
    header = request.headers.get("authorization", "")
    given = header[6:] if header.startswith("Basic ") else ""
    if not (header.startswith("Basic ") and hmac.compare_digest(given.encode(), expected.encode())):
        return gopay_error(401, "Unauthorized")
    request_id = request.headers.get("request-id")
    if not (header_ok(request_id) and header_ok(request.headers.get("debug-id"))):
        return gopay_error(400, "Invalid request headers")
    reply = {"Request-Id": request_id} if request_id else None
    try:
        raw = await request.body()
        if len(raw) > 4096:
            raise ValueError
        uid = code_signer().loads(Exchange.model_validate_json(raw).auth_code, max_age=AUTH_CODE_TTL)
        user = next((u for u in users() if u["id"] == uid), None) if isinstance(uid, str) else None
        if user is None:
            raise ValueError
        auth_token = token_signer().dumps(user["id"])
    except (BadData, ValueError):
        return gopay_error(400, "AuthCode Not Found", request_id)
    except HTTPException:
        raise
    except Exception:
        return gopay_error(500, "Internal Server Error", request_id)
    return JSONResponse({"success": True, "data": {"auth_token": auth_token, "gopay_account_id": user["id"]}}, headers=reply)


@app.get("/.well-known/jwks.json")
def jwks():
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key().public_key()))
    public.update(kid=setting("JWT_KEY_ID"), use="sig", alg="RS256")
    return {"keys": [public]}


@app.get("/api/config")
def config():
    url = os.getenv("MINIAPP_FRONTEND_URL", "")
    return {"frontend_url": url, "frontend_origin": origin(url) if url else None, "merchant_origin": origin(setting("MERCHANT_PUBLIC_URL"))}


@app.get("/")
def home():
    return FileResponse(ROOT / "public/index.html")


@app.get("/receiver")
def receiver():
    return FileResponse(ROOT / "public/receiver.html")


@app.get("/merchant-bridge.js")
def sdk():
    return FileResponse(ROOT / "public/merchant-bridge.js", media_type="text/javascript")


@app.get("/ui-preferences.js")
def ui_preferences():
    """Serve shared simulator appearance and language controls without credentials."""
    return FileResponse(ROOT / "public/ui-preferences.js", media_type="text/javascript")
