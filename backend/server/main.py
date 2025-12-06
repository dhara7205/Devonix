# server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
import asyncio
import logging
import asyncpg
from urllib.parse import urlparse, urlunparse

from server.routes import router
from server.auth import router as auth_router
from server.sso_oidc import router as sso_router

logger = logging.getLogger("devonix")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Devonix RAG API")

SESSION_SECRET = os.getenv("SESSION_SECRET", "dev_session_secret_change_me")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, https_only=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB DSN example: postgresql://devuser:devpass@dev-postgres:5432/devdb
DATABASE_DSN = os.getenv("DATABASE_URL", "postgresql://devuser:devpass@dev-postgres:5432/devdb")
# store pool on app.state
app.state.db_pool = None
app.state.app_base = os.getenv("APP_BASE", "http://localhost:8000")


async def _try_create_pool(dsn: str):
    """Attempt to create an asyncpg pool for the given dsn."""
    return await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)


def _dsn_replace_host_with_127(dsn: str) -> str:
    """Return a new DSN identical to `dsn` but with hostname replaced by 127.0.0.1."""
    parsed = urlparse(dsn)
    if not parsed.hostname:
        return dsn
    # preserve username:password if present
    userinfo = ""
    if parsed.username:
        userinfo = parsed.username
        if parsed.password:
            userinfo += ":" + parsed.password
        userinfo += "@"
    port = f":{parsed.port}" if parsed.port else ""
    new_netloc = f"{userinfo}127.0.0.1{port}"
    new_parsed = parsed._replace(netloc=new_netloc)
    return urlunparse(new_parsed)


async def create_db_pool_with_retries(dsn: str, retries: int = 3, backoff_sec: float = 1.0):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            logger.info("Attempting to create DB pool (attempt %d): %s", attempt, dsn)
            pool = await _try_create_pool(dsn)
            logger.info("DB pool created successfully")
            return pool
        except Exception as e:
            last_exc = e
            logger.warning("DB pool creation attempt %d failed: %s", attempt, e)
            # If it looks like a name resolution error, try fallback to 127.0.0.1
            if "getaddrinfo" in str(e) or isinstance(e, OSError) or "Name or service not known" in str(e):
                try:
                    fallback = _dsn_replace_host_with_127(dsn)
                    if fallback != dsn:
                        logger.info("Retrying using 127.0.0.1 instead of hostname: %s", fallback)
                        pool = await _try_create_pool(fallback)
                        logger.info("DB pool created successfully with 127.0.0.1")
                        return pool
                except Exception as e2:
                    logger.warning("Fallback to 127.0.0.1 failed: %s", e2)
            # exponential backoff before next attempt
            await asyncio.sleep(backoff_sec * attempt)
    logger.error("Failed to create DB pool after %d attempts. Last error: %s", retries, last_exc)
    raise last_exc


@app.on_event("startup")
async def startup():
    # create a reusable asyncpg pool with retries and fallback
    try:
        app.state.db_pool = await create_db_pool_with_retries(DATABASE_DSN, retries=3, backoff_sec=1.0)
    except Exception:
        # Allow app to start even if DB is unavailable during dev.
        app.state.db_pool = None
        logger.exception(
            "Could not create DB pool at startup. app.state.db_pool set to None. "
            "Fix DB config/start the DB and restart the server for full functionality."
        )


@app.on_event("shutdown")
async def shutdown():
    if app.state.db_pool:
        await app.state.db_pool.close()


app.include_router(router)
app.include_router(auth_router)
app.include_router(sso_router)
