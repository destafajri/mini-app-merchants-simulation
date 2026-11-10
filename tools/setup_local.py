"""Create ignored local configuration without printing credentials or keys."""
import os
import secrets
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

path = Path('.env')
if path.exists():
    raise SystemExit('.env already exists; edit it explicitly instead.')
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
values = dict(MERCHANT_PUBLIC_URL='http://localhost:8000', JWT_PRIVATE_KEY_PEM=pem.replace('\n', '\\n'), SESSION_SECRET=secrets.token_urlsafe(48), MINIAPP_FRONTEND_URL='', DEMO_USER_PASSWORD='MuridWukongDemo123!')
with open(path, 'x', opener=lambda p, f: os.open(p, f, 0o600)) as output:
    for name, value in values.items():
        output.write(f"{name}='{value}'\n")
print('Created private .env. Demo accounts: demo, demo2 through demo10. Set their shared password using DEMO_USER_PASSWORD in .env.')
