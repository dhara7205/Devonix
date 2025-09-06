// src/components/ChunkViewer.jsx
import React, { useState } from "react";

/**
 * ChunkViewer - simple scrollable list of chunks.
 * Each chunk is expected to be an object or string. We show snippet + metadata if present.
 *
 * Props:
 *  - chunks: Array of { id?, text, source? } OR strings
 */

export default function ChunkViewer({ chunks = [] }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  if (!Array.isArray(chunks) || chunks.length === 0) {
    return <div style={{ color: "var(--muted)" }}>No chunks to show.</div>;
  }

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 1200);
    } catch {
      // ignore clipboard failures silently
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 1200);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {chunks.map((c, i) => {
        const text = typeof c === "string" ? c : c.text || c.content || JSON.stringify(c);
        const src = typeof c === "object" && (c.source || c.filename || c.meta?.source);

        // base inline style (solid jet black)
        const baseStyle = {
          padding: 12,
          borderRadius: 8,
          background: "#000000",         
          border: "1px solid rgba(255,255,255,0.06)",
          transition: "border-color 0.18s, box-shadow 0.18s",
        };

        return (
          <div key={i} className="chunk-card">
            <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 8 }}>
                {src ? <span>Source: {src}</span> : <span>Chunk #{i + 1}</span>}
            </div>

         <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{text}</div>

         <div style={{ display: "flex", gap: 8, marginTop: 8, justifyContent: "flex-end" }}>
            <button
                type="button"
                onClick={() => handleCopy(text, i)}
                className="copy-btn"
            >
            {copiedIndex === i ? "Copied!" : "Copy"}
            </button>
         </div>
        </div>

        );
      })}
    </div>
  );
}
