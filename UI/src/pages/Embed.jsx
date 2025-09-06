// src/pages/Embed.jsx
import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; 

function DonePopup({ success, message, onClose, onGotoQuery }) {
  return (
    <div className="popup-backdrop" role="dialog" aria-modal="true">
      <div className="popup">
        <h3>{success ? "Embedding completed" : "Embedding failed"}</h3>
        <p style={{ color: "var(--muted)" }}>{message}</p>

        <div className="footer">
          <button className="nav-btn" onClick={onClose}>Close</button>
          {success && (
            <button
              className="btn-primary"
              onClick={() => {
                if (typeof onGotoQuery === "function") onGotoQuery();
                onClose();
              }}
            >
              Go to Query
            </button>
          )}
        </div>
      </div>
    </div>
  );
}


export default function Embed({ onDone = null }) {
  const navigate = useNavigate(); 
  const [path, setPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState({ open: false, success: false, message: "" });

  const handleSubmit = async (e) => {
    e && e.preventDefault();
    if (!path.trim()) {
      alert("Please enter a folder path.");
      return;
    }

    setLoading(true);
    setResult({ open: false, success: false, message: "" });

    try {
      const resp = await axios.post(
        "http://localhost:8000/embed",
        { folder_path: path },
        { timeout: 600000 } // 10m, adjust to your backend
      );

      // use backend message if provided
      const msg = resp?.data?.message || "Embedding done — now go to Query to ask questions.";

      setLoading(false);
      setResult({ open: true, success: true, message: msg });
      setPath(""); // clear input on success
    } catch (err) {
      console.error("Embedding error:", err);

      let errMsg = "Embedding failed. Please try again.";
      if (err.response && err.response.data) {
        if (typeof err.response.data === "string") errMsg = err.response.data;
        else if (err.response.data.message) errMsg = err.response.data.message;
        else errMsg = JSON.stringify(err.response.data);
      } else if (err.message) {
        errMsg = err.message;
      }

      setLoading(false);
      setResult({ open: true, success: false, message: errMsg });
    }
  };

  return (
    <main className="main">
      <div className="container">
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <h2 style={{ margin: 0 }}>Embed</h2>
          <p style={{ color: "var(--muted)", marginTop: 0 }}>
            Provide the folder path to index and embed your files.
          </p>

          <form
            onSubmit={handleSubmit}
            style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}
          >
            <input
              type="text"
              placeholder="e.g. C:\\Users\\dhara\\Documents\\project-files"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              style={{
                flex: "1 1 420px",
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid rgba(255,255,255,0.06)",
                background: "transparent",
                color: "var(--offwhite)",
              }}
              disabled={loading}
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Embedding…" : "Start Embedding"}
            </button>
            <button
              type="button"
              className="nav-btn"
              onClick={() => setPath("")}
              disabled={loading}
            >
              Clear
            </button>
          </form>

          {/* Loading area: blinking logo + status */}
          <div style={{ minHeight: 120, display: "flex", alignItems: "center", gap: 20 }}>
            {loading && (
              <>
                <img
                  src="/assets/logo-dark.svg"
                  alt="loading"
                  className="blink processing-logo"
                  style={{ height: 72 }}
                />
                <div>
                  <div style={{ fontWeight: 600 }}>Embedding…</div>
                  <div style={{ color: "var(--muted)" }}>Processing folder: {path}</div>
                </div>
              </>
            )}

            {!loading && !result.open && (
              <div style={{ color: "var(--muted)" }}>No embedding in progress.</div>
            )}

            {!loading && result.open && result.success && (
              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <img src="/assets/logo-dark.svg" alt="done" style={{ height: 64, opacity: 0.95 }} />
                <div>
                  <div style={{ fontWeight: 700 }}>Embedding finished</div>
                  <div style={{ color: "var(--muted)" }}>You can now go to Query to ask questions.</div>
                </div>
              </div>
            )}

            {!loading && result.open && !result.success && (
              <div style={{ color: "var(--muted)" }}>
                <strong style={{ color: "var(--offwhite)" }}>Error:</strong> {result.message}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Popup when done or failed */}
      {result.open && (
        <DonePopup
          success={result.success}
          message={result.message}
          onClose={() => setResult({ open: false, success: false, message: "" })}
          onGotoQuery={() => navigate("/query")}
        />
      )}
    </main>
  );
}
