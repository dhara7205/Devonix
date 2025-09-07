// src/pages/LoginSelection.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

export default function LoginSelection() {
  const navigate = useNavigate();

  return (
    <div className="page container">
      <h1>Sign in</h1>
      <p>Choose how you want to sign in</p>

      <div style={{ display: "flex", gap: 16, marginTop: 24 }}>
        <div
          className="card"
          style={{ padding: 24, flex: 1, cursor: "pointer" }}
          onClick={() => navigate("/login/personal")}
        >
          <h3>Personal</h3>
          <p>Sign in with your personal Google account.</p>
        </div>

        <div
          className="card"
          style={{ padding: 24, flex: 1, cursor: "pointer", opacity: 0.6 }}
          onClick={() => navigate("/login/enterprise")}
        >
          <h3>Enterprise</h3>
          <p>Sign in using your organization SSO (coming soon).</p>
        </div>
      </div>
    </div>
  );
}
