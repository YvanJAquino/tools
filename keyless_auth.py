import time
import json
import base64
from urllib.parse import urlencode
import httpx
import google.auth
from google.cloud import iam_credentials


class GoogleIAMSigner:
    
    AUDIENCE = 'https://oauth2.googleapis.com/token'
    GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
    URLENCODED_FORM = 'application/x-www-form-urlencoded'

    def prepare_claims(self):
        self.iat = int(time.time())
        self.exp = self.iat + 3600

        self.claims = dict(
            iss=self.iss,
            sub=self.sub,
            scope=self.scope,
            aud=self.aud,
            iat=self.iat,
            exp=self.exp
        )

    def __init__(self, iss: str, sub: str, scopes: list):
        self.iss = iss
        self.sub = sub
        self.scopes = scopes
        self.scope = ' '.join(scopes)
        self.aud = self.AUDIENCE
        self.iat = None
        self.exp = None
        self.name = f'projects/-/serviceAccounts/{iss}'
        self.claims = None
        self.prepare_claims()
        self.key_id = None
        self.signed_jwt = None

    def sign_with_iam(self):
        credentials, _ = google.auth.default()
        payload = json.dumps(self.claims)
        iam = iam_credentials.IAMCredentialsClient(credentials=credentials)
        result = iam.sign_jwt(name=self.name, payload=payload)
        self.key_id = result.key_id
        self.signed_jwt = result.signed_jwt
        return self

    def get_token(self):
        if not self.key_id and not self.signed_jwt:
            self.sign_with_iam()
        data = dict(
            grant_type=self.GRANT_TYPE,
            assertion=self.signed_jwt
        )
        headers = {'Content-Type': self.URLENCODED_FORM}
        response = httpx.post(self.AUDIENCE, data=urlencode(data), headers=headers).json()
        return response.get('access_token')

    def httpx_authorizer(self):
        signer_params = dict(iss=self.iss, sub=self.sub, scopes=self.scopes)
        return HTTPXAuthorizer(signer_params=signer_params)


class HTTPXAuthorizer(httpx.Auth):
    
    def __init__(self, token: str = 'None', signer_params: dict = None):
        self.token = token
        self.signer = GoogleIAMSigner
        self.signer_params: dict = signer_params

    def auth_flow(self, request):
        request.headers['Authorization'] = 'Bearer ' + self.token
        response = yield request
        if response.status_code in (401, 403):
            self.token = self.signer(**self.signer_params).get_token()
            request.headers['Authorization'] = 'Bearer ' + self.token
            yield request # Redoes the denied request.
