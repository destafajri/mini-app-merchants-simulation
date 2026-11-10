"""Verify session trust boundaries and the service-facing JWT contract."""
import hashlib
import json
import time
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from app import app

@pytest.fixture
def client(monkeypatch):
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    pem=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()).decode()
    salt=b'test-salt-only'
    hashed=hashlib.scrypt(b'test-password',salt=salt,n=16384,r=8,p=1).hex()
    values={'MERCHANT_PUBLIC_URL':'https://merchant.test','MERCHANT_CODE':'test','JWT_ISSUER':'https://merchant.test','JWT_AUDIENCE':'bevia-miniapp','JWT_KEY_ID':'test-key','JWT_PRIVATE_KEY_PEM':pem,'SESSION_SECRET':'test-session-secret','DEMO_USERS_JSON':json.dumps([{'id':f'user-{i}','name':f'User {i}','username':f'demo{i}','password_hash':f'scrypt${salt.hex()}${hashed}'} for i in (1,2)]),'MINIAPP_FRONTEND_URL':''}
    for k,v in values.items(): monkeypatch.setenv(k,v)
    with TestClient(app,base_url='https://merchant.test') as c: yield c


def sign_in(client, user='demo1'):
    return client.post('/api/auth/login',headers={'Origin':'https://merchant.test'},json={'username':user,'password':'test-password'})


def test_session_and_logout(client):
    assert client.get('/api/auth/me').status_code==401
    response=sign_in(client)
    assert response.status_code==200
    assert 'HttpOnly' in response.headers['set-cookie'] and 'Secure' in response.headers['set-cookie']
    assert client.get('/api/auth/me').json()['id']=='user-1'
    assert client.post('/api/auth/logout',headers={'Origin':'https://merchant.test'}).status_code==200
    assert client.get('/api/auth/me').status_code==401


def test_credentials_csrf_expiry(client,monkeypatch):
    assert client.post('/api/auth/login',json={'username':'demo1','password':'wrong'}).status_code==403
    assert client.post('/api/auth/login',headers={'Origin':'https://evil.test'},json={'username':'demo1','password':'wrong'}).status_code==403
    assert client.post('/api/auth/login',headers={'Origin':'https://merchant.test'},json={'username':'demo1','password':'wrong'}).status_code==401
    sign_in(client)
    assert client.post('/api/miniapp/token',headers={'Origin':'https://evil.test'}).status_code==403
    original=TimestampSigner.get_timestamp
    monkeypatch.setattr(TimestampSigner,'get_timestamp',lambda self:original(self)+28801)
    assert client.get('/api/auth/me').status_code==401


def test_jwt_contract_and_public_jwks(client):
    sign_in(client)
    response=client.post('/api/miniapp/token',headers={'Origin':'https://merchant.test'},json={'sub':'other-user'})
    token=response.json()['access_token']
    key=client.get('/.well-known/jwks.json').json()['keys'][0]
    assert not set(key)&{'d','p','q','dp','dq','qi'}
    assert jwt.get_unverified_header(token)['kid']==key['kid']
    public=jwt.PyJWK.from_dict(key).key
    claims=jwt.decode(token,public,algorithms=['RS256'],audience='bevia-miniapp',issuer='https://merchant.test')
    assert claims['sub']=='user-1' and claims['merchant_code']=='test'
    assert claims['exp']-claims['iat']==300
    with pytest.raises(jwt.InvalidAudienceError): jwt.decode(token,public,algorithms=['RS256'],audience='wrong')
    assert response.headers['cache-control']=='no-store'
    sign_in(client,'demo2')
    second=client.post('/api/miniapp/token',headers={'Origin':'https://merchant.test'}).json()['access_token']
    assert jwt.decode(second,public,algorithms=['RS256'],audience='bevia-miniapp')['sub']=='user-2'


def test_configuration_and_assets(client,monkeypatch):
    assert client.get('/api/config').json()['frontend_origin'] is None
    monkeypatch.setenv('MINIAPP_FRONTEND_URL','https://frontend.test/entry')
    assert client.get('/api/config').json()['frontend_origin']=='https://frontend.test'
    monkeypatch.setenv('MINIAPP_FRONTEND_URL','http://remote.test')
    assert client.get('/api/config').status_code==503
    monkeypatch.delenv('JWT_KEY_ID')
    assert client.get('/.well-known/jwks.json').status_code==503
    for path in ['/','/receiver','/merchant-bridge.js','/api/health']:
        assert client.get(path).status_code==200
