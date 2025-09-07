// src/pages/Profile.jsx
import React, { useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { AuthContext } from "../auth/AuthContext";

export default function Profile() {
  const { user, setUser, refresh, loading } = useContext(AuthContext);
  const navigate = useNavigate();

  // Ensure we have freshest user on mount (AuthProvider already refreshes,
  // but calling refresh() here is harmless and keeps state up-to-date).
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLogout = async () => {
    try {
      await axios.post(
        "http://localhost:8000/auth/logout",
        {},
        { withCredentials: true }
      );
    } catch (e) {
      // ignore errors
    }
    // update shared auth state so Header updates immediately
    setUser(null);
    // optionally refresh to confirm server state
    // await refresh();
    navigate("/login", { replace: true });
  };

  return (
    <main className="main">
      <div
        className="container"
        style={{ maxWidth: 800, padding: "32px 16px" }}
      >
        <h2 style={{ margin: "0 0 18px" }}>
          Hello there!! Thanks for choosing us.
        </h2>

        <div className="card" style={{ padding: 20 }}>
          {loading ? (
            <div>Loading profile…</div>
          ) : user ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt="avatar"
                    style={{
                      width: 64,
                      height: 64,
                      borderRadius: 8,
                      objectFit: "cover",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: 64,
                      height: 64,
                      borderRadius: 8,
                      background: "rgba(255,255,255,0.04)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "var(--muted)",
                      fontSize: 20,
                    }}
                  >
                    {user.display_name
                      ? user.display_name[0]?.toUpperCase()
                      : "U"}
                  </div>
                )}
                <div>
                  <div style={{ fontSize: 18, fontWeight: 600 }}>
                    {user.display_name || user.email}
                  </div>
                  <div style={{ color: "var(--muted)", fontSize: 13 }}>
                    {user.email}
                  </div>
                </div>
              </div>

              {/* Always show logout at the bottom */}
              <div
                style={{
                  marginTop: 24,
                  display: "flex",
                  justifyContent: "flex-end",
                }}
              >
                <button className="btn-primary" onClick={handleLogout}>
                  Log out
                </button>
              </div>
            </>
          ) : (
            <div>
              <p style={{ marginTop: 0 }}>You are not logged in.</p>
              <button
                className="btn-primary"
                onClick={() => navigate("/login")}
              >
                Sign in
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
