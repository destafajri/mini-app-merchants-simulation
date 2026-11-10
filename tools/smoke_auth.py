"""Validate real service authentication without printing credentials or tokens."""
import os
import sys
import httpx
from dotenv import load_dotenv
load_dotenv()
try:
    base = os.environ['MERCHANT_PUBLIC_URL'].rstrip('/')
    with httpx.Client(timeout=10, follow_redirects=False) as client:
        login = client.post(base + '/api/auth/login', headers={'Origin':base}, json={'username':os.environ['SMOKE_USERNAME'],'password':os.environ['SMOKE_PASSWORD']})
        login.raise_for_status()
        issued = client.post(base + '/api/miniapp/token', headers={'Origin':base})
        issued.raise_for_status()
        upstream = os.environ['MINIAPP_API_BASE_URL'].rstrip('/')
        result = client.get(upstream + '/api/v1/mini-app/' + os.environ['MERCHANT_CODE'] + '/transactions', params={'limit':1}, headers={'Authorization':'Bearer ' + issued.json()['access_token']})
        print('Authenticated history check:', result.status_code)
        sys.exit(0 if result.status_code == 200 else 1)
except (KeyError, httpx.HTTPError):
    print('Auth check failed: verify environment, credentials, connectivity and server status. No sensitive response printed.')
    sys.exit(1)
