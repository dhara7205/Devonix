# server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# add this:
from starlette.middleware.sessions import SessionMiddleware
import os

from server.routes import router
from server.auth import router as auth_router

app = FastAPI(title="Devonix RAG API")

# Session secret used by Authlib to store authorize state (keep secret in prod)
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev_session_secret_change_me")

# Install SessionMiddleware (must come before endpoints that use request.session)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, https_only=False)

# CORS as before
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
