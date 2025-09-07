INSERT INTO users (email, role, provider, provider_id, display_name, avatar_url, email_verified)
VALUES (
  'testuser@example.com',
  'user',
  'google',
  'google-sub-123',
  'Test User',
  'https://example.com/avatar.png',
  true
);

SELECT * FROM users;
