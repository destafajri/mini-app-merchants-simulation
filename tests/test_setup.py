"""Exercise actual first-run setup, privacy permissions and overwrite protection."""
import os
from pathlib import Path
import secrets
import subprocess
import sys
from dotenv import dotenv_values
from app import password_matches


def test_setup_creates_private_usable_env_and_preserves_existing(tmp_path):
    script = Path(__file__).resolve().parents[1] / 'tools/setup_local.py'
    password = secrets.token_urlsafe(18)
    result = subprocess.run([sys.executable, str(script)], input=password+'\n', text=True, capture_output=True, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    path = tmp_path / '.env'
    original = path.read_bytes()
    assert os.stat(path).st_mode & 0o777 == 0o600
    values = dotenv_values(path)
    import json
    user = json.loads(values['DEMO_USERS_JSON'])[0]
    assert user['username'] == 'demo'
    assert password_matches(password, user['password_hash'])
    assert password not in original.decode()
    assert password not in result.stdout + result.stderr
    again = subprocess.run([sys.executable, str(script)], text=True, capture_output=True, cwd=tmp_path)
    assert again.returncode != 0
    assert path.read_bytes() == original
