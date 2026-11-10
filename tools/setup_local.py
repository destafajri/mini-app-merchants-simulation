"""Create ignored local configuration without printing credentials or keys."""
import getpass
import hashlib
import json
import os
import secrets
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

path = Path('.env')
if path.exists():
    raise SystemExit('.env already exists; edit it explicitly instead.')
password = getpass.getpass('Demo password (minimum 12 characters): ')
if len(password) < 12:
    raise SystemExit('Use at least 12 characters.')
salt = secrets.token_bytes(16)
hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1).hex()
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
values = dict(MERCHANT_PUBLIC_URL='http://localhost:8000', MERCHANT_CODE='murid_wukong_demo', MINIAPP_FRONTEND_URL='', JWT_ISSUER='http://localhost:8000', JWT_AUDIENCE='bevia-miniapp', JWT_KEY_ID='murid-wukong-demo-v1', JWT_PRIVATE_KEY_PEM=pem.replace('\n', '\\n'), SESSION_SECRET=secrets.token_urlsafe(48), DEMO_USERS_JSON=json.dumps([dict(id='demo-user-001',name='Demo User',username='demo',password_hash=f'scrypt${salt.hex()}${hashed}')]), MINIAPP_API_BASE_URL='')
with open(path, 'x', opener=lambda p, f: os.open(p, f, 0o600)) as output:
    for name, value in values.items():
        output.write(f"{name}='{value}'\n")
print('Created private .env. Username: demo. Password: the value you entered.')
