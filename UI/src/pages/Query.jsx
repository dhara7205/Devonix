// src/pages/Query.jsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ChunkViewer from "../components/ChunkViewer";

export default function Query() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null); // { question, answer, prompt, chunks }
  const [chunks, setChunks] = useState([]);
  const [showChunksModal, setShowChunksModal] = useState(false);
  const [feedbackSending, setFeedbackSending] = useState(false);

  // showSaved: shows the tick after successful saving of QA pair
  const [showSaved, setShowSaved] = useState(false);
  const savedTimerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (savedTimerRef.current) {
        clearTimeout(savedTimerRef.current);
      }
    };
  }, []);

  const handleAsk = async (e) => {
    e && e.preventDefault();
    const q = question.trim();
    if (!q) return;

    setLoading(true);
    setResponse(null);
    setChunks([]);

    try {
      const res = await axios.post("http://localhost:8000/ask", { question: q }, { timeout: 600000 });
      const data = res.data || {};

      const resp = {
        question: data.question ?? q,
        answer: data.answer ?? data.text ?? "No answer returned.",
        prompt: data.prompt ?? null,
        chunks: Array.isArray(data.chunks) ? data.chunks : (Array.isArray(data.top_chunks) ? data.top_chunks : []),
      };

      setResponse(resp);
      setChunks(resp.chunks || []);
    } catch (err) {
      console.error("Query error:", err);
      setResponse({ question: q, answer: "Query failed. See console for details.", prompt: null, chunks: [] });
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (type) => {
    if (!response) return;
    // prevent double-clicking while feedback in progress or tick visible
    if (feedbackSending || showSaved) return;
    setFeedbackSending(true);

    try {
      // If thumbs-up, store the QA pair to the QA store endpoint
      if (type === "up") {
        try {
          const qaRes = await axios.post("http://localhost:8000/qa/store", {
            question: response.question,
            answer: response.answer
            // no store_dir provided -> backend will use cwd by default
          }, { timeout: 15000 });

          // show tick only if store returned 2xx (server previously returned 201)
          if (qaRes && qaRes.status >= 200 && qaRes.status < 300) {
            // show the saved tick for 2 seconds
            setShowSaved(true);
            // clear any previous timer
            if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
            savedTimerRef.current = setTimeout(() => {
              setShowSaved(false);
              savedTimerRef.current = null;
            }, 2000);
          }
        } catch (err) {
          // If saving fails, still continue to send feedback; log error
          console.error("QA store error:", err);
        }
      }

      // Also send feedback record (keeps existing behavior)
      try {
        await axios.post("http://localhost:8000/feedback", {
          question: response.question,
          answer: response.answer,
          prompt: response.prompt ?? undefined,
          feedback: type,
        }, { timeout: 10000 });
      } catch (err) {
        console.error("Feedback error:", err);
      }
    } finally {
      setFeedbackSending(false);
    }
  };

  // Simple inline check SVG — replace this with your provided SVG if you want.
  const CheckSVG = (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check-icon lucide-check"><path d="M20 6 9 17l-5-5"/></svg>
  );

  return (
    <main className="main">
      <div className="container" style={{ maxWidth: 900 }}>
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <h2 style={{ margin: 0 }}>Ask a question</h2>

          <form onSubmit={handleAsk} style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <input
              type="text"
              placeholder="e.g. What does generator file do?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              style={{
                flex: "1 1 420px",
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid rgba(255,255,255,0.06)",
                background: "transparent",
                color: "var(--offwhite)",
                outline: "none",
              }}
              disabled={loading}
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Thinking…" : "Ask"}
            </button>
            <button
              type="button"
              className="nav-btn"
              onClick={() => { setQuestion(""); setResponse(null); setChunks([]); }}
              disabled={loading}
            >
              Clear
            </button>
          </form>

          {/* Answer area */}
          <div style={{ marginTop: 8 }}>
            {!response && !loading && (
              <div style={{ color: "var(--muted)" }}>No answer yet. Ask a question to get started.</div>
            )}

            {response && (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div style={{ background: "rgba(255,255,255,0.02)", padding: 16, borderRadius: 10 }}>
                  <div style={{ color: "var(--muted)", marginBottom: 8 }}>
                    <strong>Question:</strong> {response.question}
                  </div>

                  <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{response.answer}</div>
                </div>

                {/* Feedback buttons */}
                <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <div style={{ position: "relative", display: "inline-flex", alignItems: "center" }}>
                    <button
                      className="feedback-btn"
                      title="This answer was helpful"
                      onClick={() => sendFeedback("up")}
                      disabled={feedbackSending || showSaved}
                      style={{ display: "inline-flex", alignItems: "center", justifyContent: "center" }}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-thumbs-up-icon lucide-thumbs-up" aria-hidden="true" focusable="false">
                        <path d="M7 10v12" />
                        <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z" />
                      </svg>
                    </button>

                    {/* tick overlay, positioned to the top-right of the thumbs-up */}
                    {showSaved && (
                      <div
                        aria-hidden="true"
                        style={{
                          position: "absolute",
                          right: -6,
                          top: -6,
                          width: 22,
                          height: 22,
                          borderRadius: 12,
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                          background: "rgba(0,0,0,0.6)",
                          color: "limegreen",
                          boxShadow: "0 2px 6px rgba(0,0,0,0.4)",
                          transform: "scale(1)",
                          transition: "transform 120ms ease-out, opacity 120ms ease-out",
                          opacity: 1,
                          zIndex: 5
                        }}
                      >
                        {CheckSVG}
                      </div>
                    )}
                  </div>

                  <button
                    className="feedback-btn"
                    title="This answer was not helpful"
                    onClick={() => sendFeedback("down")}
                    disabled={feedbackSending}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-thumbs-down-icon lucide-thumbs-down" aria-hidden="true" focusable="false">
                      <path d="M17 14V2" />
                      <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z" />
                    </svg>
                  </button>

                  <div style={{ color: "var(--muted)", marginLeft: 6 }}>
                    Was this answer helpful?
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Floating View Chunks button */}
      <button
        className="view-chunks-btn"
        onClick={() => setShowChunksModal(true)}
        title="View chunks"
        disabled={chunks.length === 0}
      >
        View Chunks
      </button>

      {/* Chunks modal */}
      {showChunksModal && (
        <div className="modal-backdrop" role="dialog" aria-modal="true" onClick={() => setShowChunksModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>Chunks ({chunks.length})</h3>
            <div style={{ height: 320, overflow: "auto", marginTop: 8 }}>
              <ChunkViewer chunks={chunks} />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12 }}>
              <button className="nav-btn" onClick={() => setShowChunksModal(false)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* Blinking logo overlay while loading */}
      {loading && (
        <div className="processing-overlay" role="status" aria-live="polite">
          <div className="processing-inner">
            <img src="/assets/logo-dark.svg" alt="thinking" className="processing-logo" />
            <div style={{ marginTop: 12, fontWeight: 600 }}>Thinking…</div>
          </div>
        </div>
      )}
    </main>
  );
}
