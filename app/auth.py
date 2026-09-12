from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

bearer_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False

def create_token(sub: str, kind: str, role: Optional[str] = None, full_name: Optional[str] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(sub), "kind": kind, "role": role, "full_name": full_name, "iat": now, "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token.")

def get_principal(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    return decode_token(creds.credentials)

def get_optional_principal(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> Optional[dict]:
    if creds is None: return None
    try: return decode_token(creds.credentials)
    except HTTPException: return None

def require_admin(principal: dict = Depends(get_principal)) -> dict:
    if principal.get("kind") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return principal