-- enable uuid generator (Postgres)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- users table (SSO-first)
CREATE TABLE IF NOT EXISTS users (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email          TEXT NOT NULL UNIQUE,
  role           TEXT NOT NULL DEFAULT 'user',
  provider       TEXT NOT NULL,
  provider_id    TEXT NOT NULL,
  display_name   TEXT,
  avatar_url     TEXT,
  email_verified BOOLEAN DEFAULT false,
  login_type     TEXT NOT NULL DEFAULT 'sso',
  created_at     TIMESTAMPTZ DEFAULT now(),
  last_login_at  TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_provider_providerid ON users(provider, provider_id);

-- refresh_tokens table (server-side storage for revocation)
-- NOTE: in production consider storing a hash of the token instead of raw token.
CREATE TABLE IF NOT EXISTS refresh_tokens (
  token       TEXT PRIMARY KEY,
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL,
  revoked     BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_refresh_user ON refresh_tokens(user_id);
