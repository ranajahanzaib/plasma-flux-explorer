import {
  Activity,
  BookOpenText,
  BrainCircuit,
  Database,
  GitCompareArrows,
  LayoutDashboard,
  List,
  Magnet,
  Orbit,
  Settings2,
  Shapes,
  Thermometer,
} from "lucide-react";
import Link from "next/link";
import Script from "next/script";

export default function HomePage() {
  return (
    <>
      <div className="app-shell">
        <aside className="sidebar" id="sidebar">
          <Link
            className="brand"
            href="/"
            aria-label="Plasma Flux Explorer home"
          >
            <span className="brand-mark">
              <svg viewBox="0 0 36 36" aria-hidden="true">
                <ellipse cx="18" cy="18" rx="14" ry="6.5" />
                <ellipse cx="18" cy="18" rx="9.5" ry="4.2" />
                <ellipse cx="18" cy="18" rx="4.4" ry="2" />
                <path d="M18 4v28M4 18h28" />
              </svg>
            </span>
            <span className="brand-copy">
              <b>PLASMA FLUX</b>
              <small>
                EXPLORER <i>0.1</i>
              </small>
            </span>
          </Link>
          <div className="sidebar-scroll">
            <div className="nav-group">
              <div className="nav-label">WORKSPACE</div>
              <Link className="nav-item" href="/">
                <span className="nav-icon">
                  <LayoutDashboard size={14} />
                </span>
                Overview
              </Link>
              <a
                className="nav-item active"
                href="/explorer"
                data-route="explorer"
              >
                <span className="nav-icon">
                  <Activity size={14} />
                </span>
                Discharge explorer <kbd>1</kbd>
              </a>
              <a className="nav-item" href="/flux-lab" data-route="flux-lab">
                <span className="nav-icon">
                  <Orbit size={14} />
                </span>
                Flux laboratory
              </a>
              <a className="nav-item" href="/topology" data-route="topology">
                <span className="nav-icon">
                  <Magnet size={14} />
                </span>
                Magnetic topology
              </a>
              <a
                className="nav-item"
                href="/magnetic-geometry"
                data-route="magnetic-geometry"
              >
                <span className="nav-icon">
                  <Magnet size={14} />
                </span>
                3D Magnetic geometry
              </a>
              <a
                className="nav-item"
                href="/plasma-geometry"
                data-route="plasma-geometry"
              >
                <span className="nav-icon">
                  <Shapes size={14} />
                </span>
                Plasma geometry
              </a>
              <a
                className="nav-item"
                href="/diagnostics"
                data-route="diagnostics"
              >
                <span className="nav-icon">
                  <Thermometer size={14} />
                </span>
                Diagnostic signals
              </a>
              <a className="nav-item" href="/compare" data-route="compare">
                <span className="nav-icon">
                  <GitCompareArrows size={14} />
                </span>
                Machine comparison
              </a>
              <a
                className="nav-item"
                href="/predictions"
                data-route="predictions"
              >
                <span className="nav-icon">
                  <BrainCircuit size={14} />
                </span>
                Prediction laboratory
              </a>
            </div>
            <div className="nav-group">
              <div className="nav-label">DATA</div>
              <a className="nav-item" href="/catalog" data-route="catalog">
                <span className="nav-icon">
                  <List size={14} />
                </span>
                Discharge catalog
              </a>
              <a className="nav-item" href="/sources" data-route="sources">
                <span className="nav-icon">
                  <Database size={14} />
                </span>
                Data sources
              </a>
              <a
                className="nav-item"
                href="/methodology"
                data-route="methodology"
              >
                <span className="nav-icon">
                  <BookOpenText size={14} />
                </span>
                Scientific methodology
              </a>
            </div>
          </div>
          <div className="sidebar-bottom">
            <div className="source-status">
              <span className="status-dot" id="health-dot"></span>
              <div>
                <b id="health-label">LOCAL WORKSPACE</b>
                <small id="health-detail">Checking data catalog…</small>
              </div>
              <button
                className="icon-button"
                id="refresh-data"
                aria-label="Refresh data catalog"
                title="Refresh catalog"
              >
                ↻
              </button>
            </div>
            <a className="sidebar-link" href="/settings" data-route="settings">
              <span className="nav-icon">
                <Settings2 size={14} />
              </span>
              Workspace settings
            </a>
            <div className="user-chip">
              <div className="avatar">PF</div>
              <div>
                <b>Research workspace</b>
                <small>Local session</small>
              </div>
              <span className="more">···</span>
            </div>
          </div>
        </aside>
        <main className="main-area">
          <header className="topbar">
            <button
              className="icon-button mobile-menu"
              id="menu-toggle"
              aria-label="Toggle navigation"
            >
              ☰
            </button>
            <div className="breadcrumbs">
              <span className="crumb-root">RESEARCH</span>
              <span className="crumb-slash">/</span>
              <span id="crumb-current">OVERVIEW</span>
            </div>
            <div className="topbar-right">
              <div className="dataset-rev">
                <span className="status-dot"></span>DATASET{" "}
                <b id="revision-label">NOT CONNECTED</b>
              </div>
              <button
                className="icon-button"
                id="theme-toggle"
                aria-label="Toggle theme"
                title="Toggle theme"
              >
                ◐
              </button>
              <button className="export-button" id="export-button">
                <span>⇩</span> Export <span className="chevron">⌄</span>
              </button>
            </div>
          </header>
          <div className="page-content" id="page-content"></div>
          <footer className="timeline-bar" id="timeline-bar">
            <div className="timeline-head">
              <div className="time-title">
                <span className="live-indicator"></span>
                <b>DISCHARGE TIMELINE</b>
                <span id="frame-count">NO FRAME DATA</span>
              </div>
              <div className="timeline-actions">
                <button id="step-back" aria-label="Previous frame">
                  ‹
                </button>
                <button id="play-button" aria-label="Play timeline">
                  ▶
                </button>
                <button id="step-forward" aria-label="Next frame">
                  ›
                </button>
                <span className="divider-v"></span>
                <label>
                  RATE{" "}
                  <select id="play-rate">
                    <option value="1">1×</option>
                    <option value="2">2×</option>
                    <option value="0.5">0.5×</option>
                  </select>
                </label>
                <button
                  className="icon-button timeline-expand"
                  id="timeline-expand"
                  aria-label="Expand timeline"
                >
                  ⌃
                </button>
              </div>
            </div>
            <div className="timeline-track-wrap">
              <span className="time-edge" id="time-start">
                —
              </span>
              <input
                type="range"
                min="0"
                max="0"
                defaultValue="0"
                id="time-slider"
                aria-label="Equilibrium frame"
              />
              <span className="time-edge" id="time-end">
                —
              </span>
            </div>
            <div className="frame-ticks" id="frame-ticks"></div>
          </footer>
        </main>
      </div>
      <div className="toast" id="toast" role="status" aria-live="polite"></div>
      <Script src="/app.js" strategy="afterInteractive" />
    </>
  );
}
