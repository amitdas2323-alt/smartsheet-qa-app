"""
Helper for using JLL GPT token as OPENAI_API_KEY when the token expires (~59 min).
- Decodes JWT to check expiry; if expired or expiring soon, tries refresh (if configured).
- See JLL GPT developer sandbox for refresh setup: https://ai-uat.jll.com/developer-sandbox
  ("Long-running code with token refresh" section).
"""

import base64
import json
import os
import time
from typing import Optional

# Optional: cache the refreshed token in memory to avoid refreshing on every request
_cached_token: Optional[str] = None
_cached_token_exp: float = 0


def _decode_jwt_exp(token: str) -> Optional[int]:
    """Read exp (expiry time) from JWT payload. Returns None if not a JWT or no exp."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # base64url: add padding if needed
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload = json.loads(base64.b64decode(payload_b64, altchars=b"-_"))
        return payload.get("exp")
    except Exception:
        return None


def _is_token_expired_soon(token: str, buffer_seconds: int = 300) -> bool:
    """True if token is expired or expires within buffer_seconds (default 5 min)."""
    exp = _decode_jwt_exp(token)
    if exp is None:
        return False  # not a JWT or no exp -> treat as valid (e.g. static API key)
    return time.time() >= (exp - buffer_seconds)


def _try_refresh_token() -> Optional[str]:
    """
    Try to get a new token using env-configured refresh.
    Set these in .env or Streamlit Secrets (from JLL developer sandbox docs):
    - JLL_GPT_TOKEN_URL: token/refresh endpoint URL
    - Either:
      - JLL_GPT_CLIENT_ID + JLL_GPT_CLIENT_SECRET (client_credentials), or
      - JLL_GPT_REFRESH_TOKEN (refresh_token grant)
    Returns new access token (JWT) or None.
    """
    url = os.environ.get("JLL_GPT_TOKEN_URL", "").strip()
    if not url:
        return None

    client_id = os.environ.get("JLL_GPT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("JLL_GPT_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("JLL_GPT_REFRESH_TOKEN", "").strip()

    try:
        import requests
    except ImportError:
        return None

    # Prefer refresh_token grant; fallback to client_credentials
    if refresh_token:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        auth = None
    elif client_id and client_secret:
        data = {"grant_type": "client_credentials"}
        auth = (client_id, client_secret)
    else:
        return None

    try:
        r = requests.post(url, data=data, auth=auth, timeout=30)
        r.raise_for_status()
        out = r.json()
        # Common keys for access token in OAuth2 response
        access = out.get("access_token") or out.get("accessToken") or out.get("token")
        if access:
            return access
    except Exception:
        pass
    return None


def get_effective_openai_key() -> Optional[str]:
    """
    Returns a valid key for OpenAI-compatible API (e.g. JLL GPT or OpenAI).
    - If OPENAI_API_KEY is a JWT that is expired/expiring soon, tries refresh (if configured).
    - If refresh not configured or fails, returns None so caller can fall back to keyword search.
    """
    global _cached_token, _cached_token_exp

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None

    # If it's a JWT and still valid, use it
    if not _is_token_expired_soon(key):
        _cached_token = key
        _cached_token_exp = _decode_jwt_exp(key) or 0
        return key

    # Try refresh
    new_token = _try_refresh_token()
    if new_token:
        _cached_token = new_token
        _cached_token_exp = _decode_jwt_exp(new_token) or 0
        return new_token

    # Not a JWT, or no refresh configured/failed -> use as-is (e.g. static OpenAI key)
    # If we already determined it's expired above, we'd have tried refresh; so only here if not a JWT
    if _decode_jwt_exp(key) is not None:
        return None  # was a JWT but refresh failed or not configured
    return key
