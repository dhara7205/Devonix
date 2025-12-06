# server/sso_oidc.py
import os
import json
import secrets
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import asyncpg

router = APIRouter()
oauth = OAuth()

# helper: fetch oidc client config for tenant (oidc_clients table)
async def fetch_oidc_client_config(conn, tenant_id: str):
    row = await conn.fetchrow(
        "SELECT issuer, client_id, client_secret, redirect_uri, scopes, groups_claim FROM oidc_clients WHERE tenant_id = $1",
        tenant_id,
    )
    return row

# helper: dynamic register client in authlib and return client name
def register_oidc_client_dyn(oauth_registry: OAuth, tenant_id: str, issuer: str, client_id: str, client_secret: Optional[str], redirect_uri: str, scopes: str = "openid email profile"):
    name = f"oidc_tenant_{tenant_id}"
    if name in oauth_registry:
        return name
    oauth_registry.register(
        name=name,
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url=issuer.rstrip("/") + "/.well-known/openid-configuration",
        client_kwargs={"scope": scopes},
        redirect_uri=redirect_uri,
    )
    return name

# helper: acquire a connection from the app pool
async def get_conn_from_request(request: Request):
    pool = request.app.state.db_pool
    if not pool:
        raise RuntimeError("DB pool not initialized")
    return await pool.acquire()

@router.get("/sso/{tenant_id}/redirect")
async def sso_redirect(tenant_id: str, request: Request):
    conn = await get_conn_from_request(request)
    try:
        cfg = await fetch_oidc_client_config(conn, tenant_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="Tenant OIDC config not found")
        issuer = cfg["issuer"]
        client_id = cfg["client_id"]
        client_secret = cfg["client_secret"]
        redirect_uri = cfg["redirect_uri"]
        scopes = cfg["scopes"] or "openid email profile"

        client_name = register_oidc_client_dyn(oauth, tenant_id, issuer, client_id, client_secret, redirect_uri, scopes)
        oauth_client = oauth.create_client(client_name)

        # generate state + nonce
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)

        # persist state+nonce server-side (short-lived)
        await conn.execute(
            "INSERT INTO oidc_states (state, tenant_id, nonce) VALUES ($1, $2, $3)",
            state,
            tenant_id,
            nonce,
        )

        # build redirect (Authlib will produce a RedirectResponse)
        redirect_resp = await oauth_client.authorize_redirect(request, redirect_uri, state=state, nonce=nonce)
        return redirect_resp
    finally:
        await request.app.state.db_pool.release(conn)

@router.get("/sso/{tenant_id}/callback")
async def sso_callback(tenant_id: str, request: Request):
    conn = await get_conn_from_request(request)
    try:
        cfg = await fetch_oidc_client_config(conn, tenant_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="Tenant OIDC config not found")
        issuer = cfg["issuer"]
        client_id = cfg["client_id"]
        client_secret = cfg["client_secret"]
        redirect_uri = cfg["redirect_uri"]
        groups_claim = cfg["groups_claim"]

        client_name = register_oidc_client_dyn(oauth, tenant_id, issuer, client_id, client_secret, redirect_uri, cfg["scopes"] or "openid email profile")
        oauth_client = oauth.create_client(client_name)

        # validate presence of state
        params = dict(request.query_params)
        state = params.get("state")
        if not state:
            raise HTTPException(status_code=400, detail="Missing state")

        # load stored nonce for this state
        row = await conn.fetchrow("SELECT nonce FROM oidc_states WHERE state = $1 AND tenant_id = $2", state, tenant_id)
        if not row:
            await conn.execute(
                "INSERT INTO audit_logs (tenant_id, actor_user, event_type, details) VALUES ($1, $2, $3, $4::jsonb)",
                tenant_id, None, "sso_login_failed", json.dumps({"reason":"state_not_found", "state": state})
            )
            raise HTTPException(status_code=400, detail="Invalid or expired state")

        nonce = row["nonce"]

        try:
            token = await oauth_client.authorize_access_token(request)
        except OAuthError as e:
            await conn.execute(
                "INSERT INTO audit_logs (tenant_id, actor_user, event_type, details) VALUES ($1, $2, $3, $4::jsonb)",
                tenant_id, None, "sso_login_failed", json.dumps({"reason":"token_exchange_failed", "error": str(e)})
            )
            raise HTTPException(status_code=400, detail="Token exchange failed")

        id_token = token.get("id_token")
        if not id_token:
            await conn.execute(
                "INSERT INTO audit_logs (tenant_id, actor_user, event_type, details) VALUES ($1, $2, $3, $4::jsonb)",
                tenant_id, None, "sso_login_failed", json.dumps({"reason":"id_token_missing"})
            )
            raise HTTPException(status_code=400, detail="id_token missing in response")

        # parse claims (authlib provides parse_id_token)
        try:
            claims = oauth_client.parse_id_token(token)
        except Exception:
            # fallback: try userinfo
            claims = token.get("userinfo") or token.get("id_token_claims") or {}

        sub = claims.get("sub")
        email = claims.get("email")
        name = claims.get("name")
        issuer_claim = claims.get("iss") or issuer
        sso_sub = f"{issuer_claim}|{sub}" if sub else None
        groups = claims.get(groups_claim) if (groups_claim and claims.get(groups_claim)) else claims.get("groups") or claims.get("roles") or None

        # log success
        await conn.execute(
            "INSERT INTO audit_logs (tenant_id, actor_user, event_type, details) VALUES ($1, $2, $3, $4::jsonb)",
            tenant_id, None, "sso_login_success", json.dumps({"sub": sub, "email": email, "name": name, "sso_sub": sso_sub, "groups": groups})
        )

        # cleanup used state
        await conn.execute("DELETE FROM oidc_states WHERE state = $1", state)

        # Stage 2 behavior: return claims for now
        return JSONResponse({"status": "ok", "claims": claims})
    finally:
        await request.app.state.db_pool.release(conn)
