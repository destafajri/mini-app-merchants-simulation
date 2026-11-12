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
    values={'MERCHANT_PUBLIC_URL':'https://merchant.test','MERCHANT_CODE':'test','JWT_ISSUER':'https://merchant.test','JWT_AUDIENCE':'bevia-miniapp','JWT_KEY_ID':'test-key','JWT_PRIVATE_KEY_PEM':pem,'SESSION_SECRET':'test-session-secret','DEMO_USER_PASSWORD':'MuridWukongDemo123!','MINIAPP_FRONTEND_URL':'','GOPAY_SIM_BASIC_CREDENTIAL':'fake-gopay-sim-credential'}
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
    for path in ['/','/receiver','/merchant-bridge.js','/ui-preferences.js','/api/health']:
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


EXCHANGE='/v1/mini-apps/authorizations/token'
BASIC={'Authorization':'Basic fake-gopay-sim-credential'}


def issue_code(client,user='demo'):
    sign_in(client,user)
    return client.post('/api/gopay/auth-code',headers={'Origin':'https://merchant.test'}).json()['authCode']


def exchange(client,code,headers=BASIC):
    return client.post(EXCHANGE,headers=headers,json={'auth_code':code})


NOT_FOUND={'success':False,'error':{'description':'AuthCode Not Found'}}
UNAUTHORIZED={'success':False,'error':{'description':'Unauthorized'}}


def test_auth_code_issuance_and_refusals(client):
    origin={'Origin':'https://merchant.test'}
    assert client.post('/api/gopay/auth-code',headers=origin).status_code==401
    sign_in(client)
    assert client.post('/api/gopay/auth-code').status_code==403
    assert client.post('/api/gopay/auth-code',headers={'Origin':'https://evil.test'}).status_code==403
    response=client.post('/api/gopay/auth-code',headers=origin,json={'sub':'other-user'})
    assert response.status_code==200
    body=response.json()
    assert set(body)=={'authCode','expiresIn'} and body['expiresIn']==300
    assert isinstance(body['authCode'],str) and 0<len(body['authCode'])<=2048
    assert response.headers['cache-control']=='no-store'
    assert 'merchant_session' not in body['authCode']
    client.post('/api/auth/logout',headers=origin)
    assert client.post('/api/gopay/auth-code',headers=origin).status_code==401


def test_exchange_returns_stable_user_and_signed_token(client):
    from app import token_signer
    for user,uid in [('demo','demo-user-001'),('demo2','demo-user-002')]:
        response=exchange(client,issue_code(client,user),{**BASIC,'Request-Id':'req-123','Debug-Id':'dbg-1'})
        assert response.status_code==200
        body=response.json()
        assert body['success'] is True and set(body['data'])=={'auth_token','gopay_account_id'}
        assert body['data']['gopay_account_id']==uid
        assert token_signer().loads(body['data']['auth_token'])==uid
        assert response.headers['request-id']=='req-123' and 'debug-id' not in response.headers
        assert response.headers['cache-control']=='no-store'
        assert 'access-control-allow-origin' not in response.headers
    assert 'request-id' not in exchange(client,issue_code(client)).headers


def test_exchange_credential_failures(client,monkeypatch):
    code=issue_code(client)
    for headers in [{},{'Authorization':'Basic wrong'},{'Authorization':'Basic'},{'Authorization':'Bearer fake-gopay-sim-credential'},{'Authorization':'fake-gopay-sim-credential'},{'Authorization':'Basic fake-gopay-sim-credentiaL'},{'Authorization':'Basic fake-gopay-sim-credential '}]:
        response=exchange(client,code,headers)
        assert response.status_code==401 and response.json()==UNAUTHORIZED
    assert client.post(EXCHANGE,headers={'Authorization':'Basic wrong'},content=b'not json').status_code==401
    monkeypatch.delenv('GOPAY_SIM_BASIC_CREDENTIAL')
    for headers in [BASIC,{'Authorization':'Basic '},{}]:
        response=exchange(client,code,headers)
        assert response.status_code==503 and response.json()['detail']['field']=='GOPAY_SIM_BASIC_CREDENTIAL'
    monkeypatch.setenv('GOPAY_SIM_BASIC_CREDENTIAL','')
    assert exchange(client,code,{'Authorization':'Basic '}).status_code==503


def test_exchange_rejects_bad_codes_uniformly(client,monkeypatch):
    code=issue_code(client)
    tampered=code[:-2]+('AA' if not code.endswith('AA') else 'BB')
    for bad in ['',' ','garbage',tampered,code+'x',code.split('.')[0],'a'*3000]:
        response=exchange(client,bad)
        assert response.status_code==400 and response.json()==NOT_FOUND
        assert bad.strip()=='' or bad not in response.text
    for raw in [b'not json',b'{}',b'{"auth_code":123}',b'{"auth_code":"x","extra":1}',b'[]',b'{"auth_code":"'+b'a'*5000+b'"}']:
        response=client.post(EXCHANGE,headers=BASIC,content=raw)
        assert response.status_code==400 and response.json()==NOT_FOUND
        assert b'aaaa' not in response.content
    assert client.post(EXCHANGE,headers=BASIC).json()==NOT_FOUND
    assert exchange(client,code).status_code==200
    original=TimestampSigner.get_timestamp
    monkeypatch.setattr(TimestampSigner,'get_timestamp',lambda self:original(self)+290)
    assert exchange(client,code).status_code==200
    monkeypatch.setattr(TimestampSigner,'get_timestamp',lambda self:original(self)+301)
    expired=exchange(client,code)
    assert expired.status_code==400 and expired.json()==NOT_FOUND


def test_exchange_validates_correlation_headers(client):
    code=issue_code(client)
    assert exchange(client,code,{**BASIC,'Request-Id':'r'*100}).status_code==200
    for headers in [{'Request-Id':'r'*101},{'Request-Id':'bad\x01id'},{'Request-Id':''},{'Debug-Id':'d'*101}]:
        response=exchange(client,code,{**BASIC,**headers})
        assert response.status_code==400 and 'AuthCode' not in response.text
        assert code not in response.text


def test_code_cookie_and_token_namespaces_are_separate(client):
    from app import COOKIE,code_signer,signer,token_signer
    from itsdangerous import BadSignature
    code=issue_code(client)
    cookie=client.cookies.get(COOKIE)
    assert cookie and cookie!=code
    assert exchange(client,cookie).json()==NOT_FOUND
    client.cookies.clear()
    client.cookies.set(COOKIE,code)
    assert client.get('/api/auth/me').status_code==401
    assert client.post('/api/gopay/auth-code',headers={'Origin':'https://merchant.test'}).status_code==401
    token=exchange(client,code).json()['data']['auth_token']
    assert exchange(client,token).json()==NOT_FOUND
    client.cookies.set(COOKIE,token)
    assert client.get('/api/auth/me').status_code==401
    with pytest.raises(BadSignature): code_signer().loads(token)
    with pytest.raises(BadSignature): token_signer().loads(code)
    with pytest.raises(BadSignature): signer().loads(code)
    with pytest.raises(BadSignature): signer().loads(token)
    with pytest.raises(BadSignature): code_signer().loads(cookie)


def test_exchange_never_echoes_secrets_and_is_not_browser_facing(client):
    code=issue_code(client)
    responses=[exchange(client,code),exchange(client,code,{'Authorization':'Basic wrong'}),exchange(client,'bad'),client.post(EXCHANGE,headers=BASIC,content=b'{"auth_code":1}')]
    for response in responses:
        text=response.text+str(dict(response.headers))
        assert 'fake-gopay-sim-credential' not in text
        assert response.headers['content-security-policy']=="frame-ancestors 'none'"
        assert response.headers['cache-control']=='no-store'
        assert 'access-control-allow-origin' not in response.headers
    assert code not in responses[1].text+responses[2].text+responses[3].text
    preflight=client.options(EXCHANGE,headers={'Origin':'https://evil.test','Access-Control-Request-Method':'POST'})
    assert 'access-control-allow-origin' not in preflight.headers
    assert client.get(EXCHANGE).status_code==405


def test_existing_jwt_mode_unaffected_when_gopay_credential_absent(client,monkeypatch):
    monkeypatch.delenv('GOPAY_SIM_BASIC_CREDENTIAL')
    sign_in(client)
    assert client.post('/api/miniapp/token',headers={'Origin':'https://merchant.test'}).status_code==200
    assert client.post('/api/gopay/auth-code',headers={'Origin':'https://merchant.test'}).status_code==200
    assert client.get('/.well-known/jwks.json').status_code==200
