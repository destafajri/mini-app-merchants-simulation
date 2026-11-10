"""Stateless demo merchant identity provider and browser container."""
import hashlib
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
from fastapi.responses import FileResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel, Field

load_dotenv()
ROOT = Path(__file__).parent
app = FastAPI(title="Merchant Simulator", version="1.0.0")
COOKIE = "merchant_session"
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


def signer():
    """Use a stable secret across serverless instances."""
    return URLSafeTimedSerializer(setting("SESSION_SECRET"), salt="merchant-session-v1")


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


def password_matches(password, encoded):
    """Compare scrypt password hashes without keeping plaintext credentials."""
    try:
        algorithm, salt, expected = encoded.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


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
    for user in users():
        if hmac.compare_digest(user["username"].encode(), body.username.encode()) and password_matches(body.password, user["password_hash"]):
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
