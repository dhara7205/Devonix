// src/components/ProtectedRoute.jsx
import React from "react";
import { Navigate, Outlet } from "react-router-dom";

/**
 * Usage:
 * <Route element={<ProtectedRoute />}>
 *   <Route path="/embed" element={<EmbedPage />} />
 * </Route>
 *
 * This component expects that the app has an auth state available (e.g. window.__USER__ or context).
 * We'll implement a small fetch-based check here to keep it self-contained.
 */

export default function ProtectedRoute() {
  const [loading, setLoading] = React.useState(true);
  const [authed, setAuthed] = React.useState(false);

  React.useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          credentials: "include",
        });
        if (!mounted) return;
        if (res.ok) {
          setAuthed(true);
        } else {
          setAuthed(false);
        }
      } catch (err) {
        setAuthed(false);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  if (loading) {
    // tiny loading placeholder — replace with spinner if you like
    return <div style={{ padding: 40 }}>Checking authentication…</div>;
  }

  if (!authed) {
    // not authenticated -> send to /login
    return <Navigate to="/login" replace />;
  }

  // authenticated -> render child routes
  return <Outlet />;
}
