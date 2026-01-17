from functools import lru_cache
from typing import List, Dict, Any

import logging
import requests
from fastapi import Depends, HTTPException, status
from jose import jwt, JOSEError
from pydantic import BaseModel

from .config import CERTS_URL, KEYCLOAK_CLIENT_ID, oauth2_scheme

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AuthenticatedUser(BaseModel):
    username: str
    roles: List[str]



@lru_cache()
def load_jwks() -> Dict[str, Any]:
    """
    Fetch and cache JWKS keys from Keycloak.
    Cached to avoid repeated network calls.
    """
    try:
        response = requests.get(CERTS_URL, timeout=5)
        response.raise_for_status()
        logger.info("JWKS loaded successfully from Keycloak")
        return response.json()
    except requests.RequestException as exc:
        logger.exception("Failed to fetch JWKS from Keycloak")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        ) from exc


def _get_signing_key(token: str) -> Dict[str, Any]:
    """
    Extract signing key from JWKS using token KID.
    """
    jwks = load_jwks()
    token_header = jwt.get_unverified_header(token)

    kid = token_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header"
        )

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token signature"
    )



def decode_access_token(token: str) -> AuthenticatedUser:
    """
    Decode and validate JWT token and extract user information.
    """
    try:
        signing_key = _get_signing_key(token)

        payload = jwt.decode(
            token=token,
            key=signing_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            options={
                "verify_aud": False,
                "verify_exp": True
            }
        )

        username = payload.get("preferred_username")
        roles = payload.get("realm_access", {}).get("roles", [])

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        logger.info("Authenticated user: %s", username)

        return AuthenticatedUser(username=username, roles=roles)

    except JOSEError as exc:
        logger.warning("JWT validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc


async def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
) -> AuthenticatedUser:
    """
    FastAPI dependency to retrieve authenticated user.
    """
    return decode_access_token(token)


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control.
    Accepts multiple allowed roles. User needs at least one of them.
    """
    def _role_dependency(
        user: AuthenticatedUser = Depends(get_authenticated_user),
    ) -> AuthenticatedUser:

        if not any(role in user.roles for role in allowed_roles):
            logger.warning(
                "Access denied for user=%s. Required roles: %s, User roles: %s",
                user.username,
                allowed_roles,
                user.roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Requires any of: {allowed_roles}"
            )

        return user

    return _role_dependency


