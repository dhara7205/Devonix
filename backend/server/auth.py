# server/auth.py
import os
import time
import json
import hashlib
from typing import Optional
from urllib.parse import urljoin

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import asyncpg
import jwt
from dotenv import load_dotenv

load_dotenv()  # loads .env in server/ if present

# env
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", f"{BASE_URL}/auth/google/callback")

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
JWT_ACCESS_EXPIRES_SECONDS = int(os.getenv("JWT_ACCESS_EXPIRES_SECONDS", "900"))
JWT_REFRESH_EXPIRES_SECONDS = int(os.getenv("JWT_REFRESH_EXPIRES_SECONDS", "2592000"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
    print("WARNING: Google credentials not set; /auth/google will fail until configured.")

# Setup OAuth (Authlib) for Google
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

router = APIRouter(prefix="/auth")

# DB helper: use a pool
async def get_db_pool():
    # reuse a single pool stored on module
    if not hasattr(router, "_pg_pool") or router._pg_pool is None:
        router._pg_pool = await asyncpg.create_pool(DATABASE_URL)
    return router._pg_pool

# Helper: issue JWTs
def issue_access_token(user_id: str, role: str):
    now = int(time.time())
    payload = {"user_id": user_id, "role": role, "iat": now, "exp": now + JWT_ACCESS_EXPIRES_SECONDS}
    return jwt.encode(payload, JWT_ACCESS_SECRET, algorithm="HS256")

def issue_refresh_token(user_id: str):
    now = int(time.time())
    token_id = os.urandom(16).hex()
    payload = {"user_id": user_id, "token_id": token_id, "iat": now, "exp": now + JWT_REFRESH_EXPIRES_SECONDS}
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")

# Utility: set cookies on Response
def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    cookie_opts = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        # path default '/'
    }
    # access token short lived (browser-visible not required)
    response.set_cookie("access_token", access_token, max_age=JWT_ACCESS_EXPIRES_SECONDS, **cookie_opts)
    response.set_cookie("refresh_token", refresh_token, max_age=JWT_REFRESH_EXPIRES_SECONDS, **cookie_opts)

# Utility: persist refresh token (store raw token for dev; in production store hash)
async def persist_refresh_token(pool, token: str, user_id: str, expires_at: int):
    # store token as-is for now; production: store secure hash instead
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO refresh_tokens(token, user_id, issued_at, expires_at, revoked) VALUES($1,$2,to_timestamp($3),to_timestamp($4), false)",
            token, user_id, int(time.time()), expires_at
        )

# Route: /auth/google -> redirect to Google OIDC
@router.get("/google")
async def auth_google(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Route: /auth/google/callback -> handle callback, provision user, issue tokens
@router.get("/google/callback")
async def auth_google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as err:
        raise HTTPException(status_code=400, detail=f"OAuth error: {err}")

    # token contains id_token and access_token
    userinfo = token.get("userinfo")
    # authlib may not fetch userinfo; fallback to id_token claims
    if not userinfo:
        id_token = token.get("id_token")
        if id_token:
            try:
                # decode without verifying signature here; authlib validated during exchange
                userinfo = jwt.decode(id_token, options={"verify_signature": False})
            except Exception:
                userinfo = None

    if not userinfo:
        raise HTTPException(status_code=400, detail="Failed to obtain user info from provider")

    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified", False)
    sub = userinfo.get("sub")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    if not email or not email_verified:
        raise HTTPException(status_code=403, detail="Email not present or not verified by provider")

    provider = "google"
    provider_id = sub

    pool = await get_db_pool()

    # Find user by provider+provider_id
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE provider=$1 AND provider_id=$2", provider, provider_id)
        if not user:
            # if email exists, link carefully (this simple flow updates provider if existing user has no local password)
            existing = await conn.fetchrow("SELECT * FROM users WHERE email=$1", email)
            if existing:
                # Link provider to existing user (day-1 shortcut). In prod, do explicit linking flow.
                await conn.execute("UPDATE users SET provider=$1, provider_id=$2, login_type='sso' WHERE id=$3",
                                   provider, provider_id, existing["id"])
                user = await conn.fetchrow("SELECT * FROM users WHERE id=$1", existing["id"])
            else:
                user = await conn.fetchrow(
                    """INSERT INTO users (email, role, provider, provider_id, display_name, avatar_url, email_verified)
                       VALUES ($1,'user',$2,$3,$4,$5,$6) RETURNING *""",
                    email, provider, provider_id, name, picture, True
                )

        # update last_login_at
        await conn.execute("UPDATE users SET last_login_at = now() WHERE id=$1", user["id"])

    # issue tokens
    access_token = issue_access_token(str(user["id"]), user["role"])
    refresh_token = issue_refresh_token(str(user["id"]))

    # persist refresh token (store raw token for dev); get expiry
    decoded = jwt.decode(refresh_token, JWT_REFRESH_SECRET, algorithms=["HS256"])
    expires_at = decoded.get("exp")
    await persist_refresh_token(pool, refresh_token, str(user["id"]), expires_at)

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173/") 

    # set cookies and redirect
    redirect_to = FRONTEND_URL
    resp = RedirectResponse(url=redirect_to)
    set_auth_cookies(resp, access_token, refresh_token)
    return resp

# Route: /auth/token/refresh
@router.post("/token/refresh")
async def token_refresh(request: Request):
    # read refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    # verify token signature & expiry
    try:
        payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("user_id")
    # confirm token is stored and not revoked
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM refresh_tokens WHERE token=$1 AND revoked=false", refresh_token)
        if not row:
            raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

        # fetch user and issue new access token
        user = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

    access_token = issue_access_token(str(user["id"]), user["role"])
    resp = JSONResponse({"access_expires_in": JWT_ACCESS_EXPIRES_SECONDS})
    # set new access cookie (keep refresh cookie unchanged for now)
    set_auth_cookies(resp, access_token, refresh_token)
    return resp

# Route: /auth/logout
@router.post("/logout")
async def logout(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    pool = await get_db_pool()
    if refresh_token:
        async with pool.acquire() as conn:
            await conn.execute("UPDATE refresh_tokens SET revoked=true WHERE token=$1", refresh_token)

    # Create an empty 204 response and delete cookies
    resp = Response(status_code=204)
    # delete cookies with same flags as set_auth_cookies
    resp.delete_cookie("access_token", path="/")
    resp.delete_cookie("refresh_token", path="/")
    return resp

from fastapi import Depends

@router.get("/me")
async def get_me(request: Request):
    access = request.cookies.get("access_token")
    if not access:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        payload = jwt.decode(access, JWT_ACCESS_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload["user_id"]
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, email, display_name, role FROM users WHERE id=$1", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    return dict(user)


async def get_current_user(request: Request):
    access = request.cookies.get("access_token")
    if not access:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(access, JWT_ACCESS_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid access token")
    user_id = payload.get("user_id")
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id,email,display_name,role FROM users WHERE id=$1", user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/_debug/users")
async def debug_list_users(request: Request):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, provider, provider_id, created_at, last_login_at FROM users ORDER BY created_at DESC LIMIT 200")
        return [dict(r) for r in rows]