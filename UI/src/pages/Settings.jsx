// src/pages/Settings.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const LS_KEY = "devonix:settings:v1";

const inputStyle = {
  width: "100%",
  padding: "8px 10px",
  marginTop: 6,
  borderRadius: 8,
  border: "1px solid rgba(255,255,255,0.06)",
  background: "transparent",
  color: "var(--offwhite)",
  outline: "none"
};

export default function Settings() {
  const [loading, setLoading] = useState(false);       // general saving/loading
  const [loadingLoad, setLoadingLoad] = useState(true); // initial load
  const [toast, setToast] = useState(null);
  const [serverCfgExists, setServerCfgExists] = useState(false);

  // authoritative values loaded from server (or null if not present)
  const [serverValues, setServerValues] = useState(null);

  // editable draft (what the form shows)
  const [draft, setDraft] = useState({
    api_endpoint: "",
    api_key: "",
    store_dir: ""
  });

  const [editing, setEditing] = useState(false);
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    // load local cache first
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        setDraft(prev => ({ ...prev, ...parsed }));
      }
    } catch (e) {
      // ignore
    }

    // then attempt to load server config
    (async () => {
      setLoadingLoad(true);
      try {
        const { data } = await axios.get("http://localhost:8000/qa/config", { withCredentials: true },{ timeout: 8000 });
        if (data && typeof data === "object") {
          const vals = {
            api_endpoint: data.api_endpoint ?? "",
            api_key: data.api_key ?? "",
            store_dir: data.store_dir ?? ""
          };
          setServerValues(vals);
          setDraft(vals);
          setServerCfgExists(true);
        } else {
          setServerValues(null);
          setServerCfgExists(false);
        }
      } catch (err) {
        // 404 -> not configured; other errors we log
        if (err.response && err.response.status === 404) {
          setServerValues(null);
          setServerCfgExists(false);
        } else {
          console.info("Could not load server config (ok if first run):", err.message || err);
        }
      } finally {
        setLoadingLoad(false);
      }
    })();
  }, []);

  const showToast = (type, text) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 2600);
  };

  const updateDraft = (patch) => {
    setDraft(d => {
      const next = { ...d, ...patch };
      try { localStorage.setItem(LS_KEY, JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  const enterEdit = () => {
    setEditing(true);
    setShowKey(false);
  };

  const cancelEdit = () => {
    // restore draft to last server values (or leave local cache if none)
    if (serverValues) {
      setDraft({ ...serverValues });
    } else {
      // reload local cache if available
      try {
        const raw = localStorage.getItem(LS_KEY);
        if (raw) setDraft(JSON.parse(raw));
      } catch (e) {}
    }
    setEditing(false);
    setShowKey(false);
  };

  const handleSaveToServer = async () => {
  // basic checks
  const api_key = (draft.api_key || "").trim();
  const api_endpoint = (draft.api_endpoint || "").trim();
  const store_dir = (draft.store_dir || "").trim();

  if (!api_key) return showToast("error", "API key is required.");
  if (!api_endpoint || !(api_endpoint.startsWith("http://") || api_endpoint.startsWith("https://"))) {
    return showToast("error", "API endpoint must start with http:// or https://");
  }
  if (!store_dir) return showToast("error", "Storage directory is required.");

  setLoading(true);
  try {
    const payload = { api_key, api_endpoint, store_dir };

    // correct axios.post signature: (url, data, config)
    const { data } = await axios.post(
      "http://localhost:8000/qa/config",
      payload,
      { timeout: 20000, withCredentials: true }
    );

    if (data && data.status === "success") {
      showToast("success", "Saved on server.");
    } else {
      showToast("success", data?.message || "Saved (server responded).");
    }

    // update local serverValues and end editing
    const newVals = { api_endpoint, api_key, store_dir };
    setServerValues(newVals);
    setDraft(newVals);
    setEditing(false);
    setServerCfgExists(true);
    try { localStorage.setItem(LS_KEY, JSON.stringify(newVals)); } catch (e) {}
  } catch (err) {
    console.error("Save error (full):", err);
    let msg = "Save failed.";
    if (err.response) {
      // server responded with status (likely 422). Show server message if present
      console.error("Server response data:", err.response.data);
      const serverMsg = err.response.data?.detail || err.response.data || err.response.statusText;
      msg = typeof serverMsg === "string" ? serverMsg : JSON.stringify(serverMsg);
    } else if (err.request) {
      msg = "No response from server (check backend).";
    } else {
      msg = err.message;
    }
    showToast("error", msg);
  } finally {
    setLoading(false);
  }
};


  const handleSaveLocalOnly = () => {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(draft));
      showToast("success", "Saved locally.");
      setEditing(false);
    } catch (e) {
      console.error(e);
      showToast("error", "Failed saving locally.");
    }
  };

  return (
    <main className="main">
      <div className="container" style={{ maxWidth: 900 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h2 style={{ margin: 0 }}>Settings</h2>
          <div>
            {!editing ? (
              <button className="btn-primary" onClick={enterEdit} disabled={loadingLoad}>
                {loadingLoad ? "Loading…" : (serverCfgExists ? "Edit" : "Configure")}
              </button>
            ) : (
              <>
                <button className="nav-btn" onClick={cancelEdit} disabled={loading}>Cancel</button>
                <button className="btn-primary" onClick={handleSaveToServer} disabled={loading} style={{ marginLeft: 8 }}>
                  {loading ? "Saving…" : "Save to server"}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {/* LLM API card */}
          <div className="card">
            <h3 style={{ marginTop: 0 }}>LLM API</h3>
            <p style={{ color: "var(--muted)" }}>Server-side LLM configuration (persisted on the server).</p>

            {/* View mode */}
            {!editing && (
              <>
                <div style={{ marginTop: 8 }}>
                  <div style={{ color: "var(--muted)", fontSize: 13 }}>API endpoint</div>
                  <div style={{ marginTop: 6, wordBreak: "break-all" }}>{draft.api_endpoint || <span style={{ color: "var(--muted)" }}>— not set —</span>}</div>

                  <div style={{ marginTop: 12, color: "var(--muted)", fontSize: 13 }}>API key</div>
                  <div style={{ marginTop: 6 }}>
                    {draft.api_key ? (
                      <code style={{ padding: "6px 8px", borderRadius: 6, background: "rgba(255,255,255,0.02)" }}>
                        {"*".repeat(Math.max(8, (draft.api_key || "").length > 0 ? 8 : 0))}
                      </code>
                    ) : (
                      <span style={{ color: "var(--muted)" }}>— not set —</span>
                    )}
                    {" "}
                    <button className="nav-btn" onClick={() => { setShowKey(v => !v); setEditing(true); }} style={{ marginLeft: 8 }}>
                      Show / Edit
                    </button>
                  </div>

                  {showKey && draft.api_key && (
                    <div style={{ marginTop: 8 }}>
                      <div style={{ color: "var(--muted)", fontSize: 13 }}>API key (visible)</div>
                      <div style={{ marginTop: 6 }}>
                        <input value={draft.api_key} onChange={(e)=>updateDraft({ api_key: e.target.value })} style={inputStyle} />
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Edit mode */}
            {editing && (
              <>
                <label style={{ fontSize: 13, color: "var(--muted)", marginTop: 8 }}>API endpoint</label>
                <input value={draft.api_endpoint} onChange={(e)=>updateDraft({ api_endpoint: e.target.value })} placeholder="https://..." style={inputStyle} />

                <label style={{ fontSize: 13, color: "var(--muted)", marginTop: 8 }}>API key</label>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <input value={draft.api_key} onChange={(e)=>updateDraft({ api_key: e.target.value })} placeholder="sk-..." style={{ ...inputStyle, marginTop: 0 }} type={showKey ? "text" : "password"} />
                  <button className="nav-btn" onClick={() => setShowKey(v => !v)} type="button">{showKey ? "Hide" : "Show"}</button>
                </div>
              </>
            )}
          </div>

          {/* Storage card */}
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Storage directory</h3>
            <p style={{ color: "var(--muted)" }}>Directory where qa_store.json and feedback.json will be saved by the server.</p>

            {!editing && (
              <>
                <div style={{ color: "var(--muted)", fontSize: 13 }}>Folder path</div>
                <div style={{ marginTop: 6, wordBreak: "break-all" }}>{draft.store_dir || <span style={{ color: "var(--muted)" }}>— not set —</span>}</div>

                <div style={{ marginTop: 12 }}>
                  <button className="nav-btn" onClick={() => { setEditing(true); }} >Edit</button>
                  <button className="nav-btn" onClick={() => { handleSaveLocalOnly(); }} style={{ marginLeft: 8 }}>Save locally</button>
                </div>
              </>
            )}

            {editing && (
              <>
                <label style={{ fontSize: 13, color: "var(--muted)", marginTop: 8 }}>Folder path</label>
                <input value={draft.store_dir} onChange={(e)=>updateDraft({ store_dir: e.target.value })} placeholder="C:\\path\\to\\dir" style={inputStyle} />
                <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                  <button className="btn-primary" onClick={handleSaveLocalOnly}>Save locally</button>
                  <button className="nav-btn" onClick={() => updateDraft({ store_dir: "" })}>Clear</button>
                </div>
                <div style={{ marginTop: 12, color: "var(--muted)", fontSize: 13 }}>
                  Note: Save to server will validate write permission to this path.
                </div>
              </>
            )}
          </div>
        </div>

        {/* footer actions when editing */}
        {editing && (
          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12 }}>
            <button className="nav-btn" onClick={cancelEdit} disabled={loading}>Cancel</button>
            <button className="btn-primary" onClick={handleSaveToServer} disabled={loading}>{loading ? "Saving…" : "Save to server"}</button>
          </div>
        )}
      </div>

      {/* toast */}
      {toast && (
        <div style={{
          position: "fixed",
          right: 18,
          bottom: 18,
          background: toast.type === "success" ? "rgba(16,185,129,0.12)" : "rgba(255,100,100,0.12)",
          border: `1px solid ${toast.type === "success" ? "rgba(16,185,129,0.3)" : "rgba(255,100,100,0.2)"}`,
          color: "var(--offwhite)",
          padding: "10px 14px",
          borderRadius: 8,
          zIndex: 6000
        }}>{toast.text}</div>
      )}
    </main>
  );
}
