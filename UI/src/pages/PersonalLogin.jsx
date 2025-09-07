// src/components/PersonalLogin.jsx
import React from "react";

export default function PersonalLogin() {
  const backendAuthUrl = "http://localhost:8000/auth/google";

  return (
    <div className="page container">
      <h1>Personal sign-in</h1>
      <p>Use your personal Google account to sign in.</p>

      <div style={{ marginTop: 20 }}>
        <a
          href={backendAuthUrl}
          style={{
            display: "inline-block",
            padding: "12px 20px",
            borderRadius: 8,
            background: "rgba(16,185,129)",
            color: "white",
            textDecoration: "none",
            fontWeight: 600
          }}
        >
          Continue with Google
        </a>
      </div>
    </div>
  );
}
