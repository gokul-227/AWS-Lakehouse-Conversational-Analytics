import os
import requests
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

security = HTTPBearer()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")

def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)):
    token = auth.credentials
    try:
        # In a production environment, you should cache the JWKS
        jwks_url = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        
        # Verify JWT (simplification for this example)
        header = jwt.get_unverified_header(token)
        key = [k for k in jwks['keys'] if k['kid'] == header['kid']][0]
        
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=CLIENT_ID,
            options={"verify_at_hash": False}
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
