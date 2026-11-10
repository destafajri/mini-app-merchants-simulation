"""Exercise actual first-run setup, privacy permissions and overwrite protection."""
import os
from pathlib import Path
import subprocess
import sys
from dotenv import dotenv_values
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def test_setup_creates_private_usable_env_and_preserves_existing(tmp_path):
    script = Path(__file__).resolve().parents[1] / 'tools/setup_local.py'
    result = subprocess.run([sys.executable, str(script)], text=True, capture_output=True, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    path = tmp_path / '.env'
    original = path.read_bytes()
    assert os.stat(path).st_mode & 0o777 == 0o600
    values = dotenv_values(path)
    assert values['DEMO_USER_PASSWORD']=='MuridWukongDemo123!'
    assert values['DEMO_USER_PASSWORD'] not in result.stdout+result.stderr
    assert 'DEMO_USERS_JSON' not in values
    assert 'JWT_ISSUER' not in values
    assert values['MERCHANT_PUBLIC_URL']=='http://localhost:8000'
    assert len(values['SESSION_SECRET'])>=43
    key=serialization.load_pem_private_key(values['JWT_PRIVATE_KEY_PEM'].replace('\\n','\n').encode(),password=None)
    assert isinstance(key,rsa.RSAPrivateKey) and key.key_size>=2048
    assert values['SESSION_SECRET'] not in result.stdout+result.stderr
    assert 'BEGIN PRIVATE KEY' not in result.stdout+result.stderr
    again = subprocess.run([sys.executable, str(script)], text=True, capture_output=True, cwd=tmp_path)
    assert again.returncode != 0
    assert path.read_bytes() == original
