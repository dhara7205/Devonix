// src/pages/NotFound.jsx
import React from "react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div
      style={{
        minHeight: "70vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      <h1 style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>404</h1>
      <p style={{ fontSize: "1.25rem", color: "#555" }}>
        Oops! The page you’re looking for doesn’t exist.
      </p>
      <Link
        to="/"
        style={{
          marginTop: "1rem",
          padding: "0.75rem 1.5rem",
          borderRadius: "8px",
          background: "rgba(16,185,129)",
          color: "white",
          fontWeight: 600,
          textDecoration: "none",
        }}
      >
        Go back home
      </Link>
    </div>
  );
}
