import json

import os

import datetime

from fastapi import HTTPException, Header

from urllib.request import urlopen

from jose import jwt

from jose import exceptions as JoseExceptions

from utils import logger

AUTH0_DOMAIN = os.environ.get(
    'AUTH0_DOMAIN', 'https://<domain>/<tenant-id>/')

AUTH0_ISSUER = os.environ.get(
    'AUTO0_ISSUER', 'https://sts.windows.net/<tenant>/')

AUTH0_API_AUDIENCE = os.environ.get(
    'AUTH0_API_AUDIENCE', '<audience url>')

AZURE_OPENID_CONFIG = os.environ.get(
    'AZURE_OPENID_CONFIG', 'https://login.microsoftonline.com/common/.well-known/openid-configuration')


def get_token_auth_header(authorization):
    parts = authorization.split()

    if parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, 
            detail='Authorization header must start with Bearer')
    elif len(parts) == 1:
        raise HTTPException(
            status_code=401, 
            detail='Authorization token not found')
    elif len(parts) > 2:
        raise HTTPException(
            status_code=401, 
            detail='Authorization header be Bearer token')
    
    token = parts[1]
    return token


def get_payload(unverified_header, token, jwks_properties):
    try:
        payload = jwt.decode(
            token,
            key=jwks_properties["jwks"],
            algorithms=jwks_properties["algorithms"],  # ["RS256"] typically
            audience=AUTH0_API_AUDIENCE,
            issuer=AUTH0_ISSUER
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail='Authorization token expired')
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=401, 
            detail='Incorrect claims, check the audience and issuer.')
    except Exception:
        raise HTTPException(
            status_code=401, 
            detail='Unable to parse authentication token')

    return payload


class AzureJWKS:
    def __init__(self, openid_config: str=AZURE_OPENID_CONFIG):
        self.openid_url = openid_config
        self._jwks = None
        self._signing_algorithms = []
        self._last_updated = datetime.datetime(2000, 1, 1, 12, 0, 0)
    
    def _refresh_cache(self):
        openid_reader = urlopen(self.openid_url)
        azure_config = json.loads(openid_reader.read())
        self._signing_algorithms = azure_config["id_token_signing_alg_values_supported"]
        jwks_url = azure_config["jwks_uri"]

        jwks_reader = urlopen(jwks_url)
        self._jwks = json.loads(jwks_reader.read())

        logger.info(f"Refreshed jwks config from {jwks_url}.")
        logger.info("Supported token signing algorithms: {}".format(str(self._signing_algorithms)))
        self._last_updated = datetime.datetime.now()

    def get_jwks(self, cache_hours: int=24):
        
        logger.info("jwks config is out of date (last updated at {})".format(str(self._last_updated)))
        self._refresh_cache()
        return {'jwks': self._jwks, 'algorithms': self._signing_algorithms}

jwks_config = AzureJWKS()


async def require_auth(token: str = Header(...)):
    token = get_token_auth_header(token)
   

    try:
        unverified_header = jwt.get_unverified_header(token)
    except JoseExceptions.JWTError:
        raise HTTPException(
                    status_code=401, 
                    detail='Unable to decode authorization token headers')

    payload = get_payload(unverified_header, token, jwks_config.get_jwks())
    if not payload:
        raise HTTPException(
                    status_code=401, 
                    detail='Invalid authorization token')

    return payload
# I hope the community gets benefite