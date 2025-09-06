// src/components/Header.jsx
import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";

export default function Header() {
  const [open, setOpen] = useState(false);

  const navItems = [
    { to: "/embed", label: "Embed" },
    { to: "/query", label: "Query" },
    { to: "/settings", label: "Settings" },
  ];

  // helper to close mobile menu when navigating
  const handleNavClick = () => setOpen(false);

  return (
    <header className="header" role="banner">
      <div className="container header-inner">
        <Link to="/" className="brand" aria-label="Devonix home" onClick={handleNavClick}>
          {/* white-on-transparent logo for dark header */}
          <img src="/assets/logo-dark.svg" alt="Devonix" />
          {/* <span className="title">Devonix</span> */}
        </Link>

        <nav className="nav" aria-label="Main navigation">
          {navItems.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end
              className={({ isActive }) =>
                `nav-btn${isActive ? " nav-btn--active" : ""}`
              }
              onClick={handleNavClick}
            >
              {n.label}
            </NavLink>
          ))}

          <Link to="/login" className="btn-primary login-link" onClick={handleNavClick}>
            Log in
          </Link>
        </nav>

        <button
          className="hamburger"
          aria-expanded={open}
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          ) : (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="mobile-menu" role="menu" aria-label="Mobile navigation">
          <div className="container nav-row">
            {navItems.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `nav-btn${isActive ? " nav-btn--active" : ""}`
                }
                onClick={handleNavClick}
              >
                {n.label}
              </NavLink>
            ))}
            <Link to="/login" className="btn-primary login-link" onClick={handleNavClick}>
              Log in
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
