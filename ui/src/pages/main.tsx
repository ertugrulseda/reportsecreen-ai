import { useState } from "react";
import ReportScreenGenerator from "../components/ReportScreenGenerator";
import ReleaseManager from "../components/ReleaseManager";
import VersionComparator from "../components/VersionComparator";
import "./main.css";

type Page = "home" | "report" | "release" | "version";

interface MenuItem {
  id: Page;
  label: string;
  icon: string;
  description: string;
}

const MENU_ITEMS: MenuItem[] = [
  {
    id: "report",
    label: "Report Screen Generator",
    icon: "⚡",
    description: "AI destekli rapor ekranı üretici",
  },
  {
    id: "release",
    label: "Release Manager",
    icon: "🚀",
    description: "Sürüm yönetim ve dağıtım merkezi",
  },
  {
    id: "version",
    label: "Version Comparator",
    icon: "⚖",
    description: "Sürümler arası fark analizi",
  },
];

function HomePage({ onNavigate }: { onNavigate: (page: Page) => void }) {
  return (
    <div className="main-home">
      <div className="main-hero">
        <div className="main-hero__badge">
          <span className="main-hero__badge-dot" />
          Aktif
        </div>
        <h1 className="main-hero__title">
          Teb<span className="main-hero__title--accent">UI</span>Accelerator
        </h1>
        <p className="main-hero__sub">
          Geliştirici araçları ve yapay zeka destekli kod üretim platformu
        </p>
      </div>

      <div className="main-cards">
        {MENU_ITEMS.map((item) => (
          <button
            key={item.id}
            className="main-card"
            onClick={() => onNavigate(item.id)}
          >
            <div className="main-card__icon">{item.icon}</div>
            <div className="main-card__body">
              <p className="main-card__label">{item.label}</p>
              <p className="main-card__desc">{item.description}</p>
            </div>
            <span className="main-card__arrow">›</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Main() {
  const [activePage, setActivePage] = useState<Page>("home");
  const [menuOpen, setMenuOpen] = useState(false);

  const activeItem = MENU_ITEMS.find((m) => m.id === activePage);

  function renderContent() {
    switch (activePage) {
      case "report":  return <ReportScreenGenerator />;
      case "release": return <ReleaseManager />;
      case "version": return <VersionComparator />;
      default:        return <HomePage onNavigate={setActivePage} />;
    }
  }

  return (
    <div className="main-layout">
      {/* Sidebar */}
      <aside className={`main-sidebar${menuOpen ? " main-sidebar--open" : ""}`}>
        <div
          className="main-sidebar__logo"
          onClick={() => { setActivePage("home"); setMenuOpen(false); }}
        >
          <div className="main-sidebar__logo-icon">T</div>
          <span className="main-sidebar__logo-text">
            TebUI<span>Accelerator</span>
          </span>
        </div>

        <div className="main-sidebar__divider" />

        <nav className="main-sidebar__nav">
          {MENU_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`main-nav-item${activePage === item.id ? " main-nav-item--active" : ""}`}
              onClick={() => { setActivePage(item.id); setMenuOpen(false); }}
            >
              <span className="main-nav-item__icon">{item.icon}</span>
              <span className="main-nav-item__label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="main-sidebar__footer">v0.1.0-alpha</div>
      </aside>

      {menuOpen && (
        <div className="main-overlay" onClick={() => setMenuOpen(false)} />
      )}

      {/* Content */}
      <div className="main-content">
        <header className="main-topbar">
          <button
            className="main-topbar__burger"
            onClick={() => setMenuOpen((v) => !v)}
          >
            <span /><span /><span />
          </button>
          <p className="main-topbar__breadcrumb">
            <span
              onClick={() => setActivePage("home")}
              style={{ cursor: "pointer", opacity: 0.5 }}
            >
              TebUIAccelerator
            </span>
            {activeItem && (
              <>
                <span style={{ opacity: 0.3, margin: "0 6px" }}>›</span>
                {activeItem.label}
              </>
            )}
          </p>
        </header>

        <main className="main-page-content">{renderContent()}</main>
      </div>
    </div>
  );
}
