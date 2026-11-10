"""Verify session trust boundaries and the service-facing JWT contract."""
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
    values={'MERCHANT_PUBLIC_URL':'https://merchant.test','MERCHANT_CODE':'test','JWT_ISSUER':'https://merchant.test','JWT_AUDIENCE':'bevia-miniapp','JWT_KEY_ID':'test-key','JWT_PRIVATE_KEY_PEM':pem,'SESSION_SECRET':'test-session-secret','DEMO_USER_PASSWORD':'MuridWukongDemo123!','MINIAPP_FRONTEND_URL':''}
    for k,v in values.items(): monkeypatch.setenv(k,v)
    with TestClient(app,base_url='https://merchant.test') as c: yield c


def sign_in(client, user='demo'):
    return client.post('/api/auth/login',headers={'Origin':'https://merchant.test'},json={'username':user,'password':'MuridWukongDemo123!'})


def test_session_and_logout(client):
    assert client.get('/api/auth/me').status_code==401
    response=sign_in(client)
    assert response.status_code==200
    assert 'HttpOnly' in response.headers['set-cookie'] and 'Secure' in response.headers['set-cookie']
    assert client.get('/api/auth/me').json()['id']=='demo-user-001'
    assert client.post('/api/auth/logout',headers={'Origin':'https://merchant.test'}).status_code==200
    assert client.get('/api/auth/me').status_code==401


def test_credentials_csrf_expiry(client,monkeypatch):
    assert client.post('/api/auth/login',json={'username':'demo','password':'wrong'}).status_code==403
    assert client.post('/api/auth/login',headers={'Origin':'https://evil.test'},json={'username':'demo','password':'wrong'}).status_code==403
    assert client.post('/api/auth/login',headers={'Origin':'https://merchant.test'},json={'username':'demo','password':'wrong'}).status_code==401
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
    assert claims['sub']=='demo-user-001' and claims['merchant_code']=='test'
    assert claims['exp']-claims['iat']==300
    with pytest.raises(jwt.InvalidAudienceError): jwt.decode(token,public,algorithms=['RS256'],audience='wrong')
    assert response.headers['cache-control']=='no-store'
    sign_in(client,'demo2')
    second=client.post('/api/miniapp/token',headers={'Origin':'https://merchant.test'}).json()['access_token']
    assert jwt.decode(second,public,algorithms=['RS256'],audience='bevia-miniapp')['sub']=='demo-user-002'


def test_configuration_and_assets(client,monkeypatch):
    assert client.get('/api/config').json()['frontend_origin'] is None
    monkeypatch.setenv('MINIAPP_FRONTEND_URL','https://frontend.test/entry')
    assert client.get('/api/config').json()['frontend_origin']=='https://frontend.test'
    monkeypatch.setenv('MINIAPP_FRONTEND_URL','http://remote.test')
    assert client.get('/api/config').status_code==503
    monkeypatch.delenv('JWT_PRIVATE_KEY_PEM')
    assert client.get('/.well-known/jwks.json').status_code==503
    for path in ['/','/receiver','/merchant-bridge.js','/api/health']:
        assert client.get(path).status_code==200


def test_all_repository_accounts_and_defaults(client,monkeypatch):
    from app import users
    accounts=users()
    assert len(accounts)==10
    assert len({u['id'] for u in accounts})==10
    assert len({u['username'] for u in accounts})==10
    monkeypatch.setenv('DEMO_USERS_JSON','invalid old value ignored')
    for user in accounts:
        assert sign_in(client,user['username']).status_code==200
        assert client.get('/api/auth/me').json()['id']==user['id']
    for key in ['MERCHANT_CODE','JWT_ISSUER','JWT_AUDIENCE','JWT_KEY_ID']:
        monkeypatch.delenv(key,raising=False)
    result=client.post('/api/miniapp/token',headers={'Origin':'https://merchant.test'})
    public=jwt.PyJWK.from_dict(client.get('/.well-known/jwks.json').json()['keys'][0]).key
    claims=jwt.decode(result.json()['access_token'],public,algorithms=['RS256'],audience='bevia-miniapp',issuer='https://merchant.test')
    assert claims['merchant_code']=='murid_wukong_demo'
    assert claims['sub']=='demo-user-010'
    assert jwt.get_unverified_header(result.json()['access_token'])['kid']=='murid-wukong-demo-v1'


def test_shared_password_is_environment_only(client,monkeypatch):
    from app import users
    assert all(set(user)=={'id','name','username'} for user in users())
    monkeypatch.setenv('DEMO_USER_PASSWORD','New-Test-Password-測試!')
    assert sign_in(client).status_code==401
    for user in users():
        response=client.post('/api/auth/login',headers={'Origin':'https://merchant.test'},json={'username':user['username'],'password':'New-Test-Password-測試!'})
        assert response.status_code==200
        assert response.json()['id']==user['id']
        assert 'password' not in response.text.lower()
    assert client.post('/api/auth/login',headers={'Origin':'https://merchant.test'},json={'username':'unknown','password':'New-Test-Password-測試!'}).status_code==401
    monkeypatch.delenv('DEMO_USER_PASSWORD')
    assert sign_in(client).status_code==503
    monkeypatch.setenv('DEMO_USER_PASSWORD','')
    assert sign_in(client).status_code==503
