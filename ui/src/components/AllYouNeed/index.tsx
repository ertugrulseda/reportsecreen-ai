import "../../App.css";

interface Resource {
  icon: string;
  title: string;
  badge: string;
  description: string;
  href: string;
  accentColor: string;
  glowColor: string;
}

const RESOURCES: Resource[] = [
  {
    icon: "🎨",
    title: "TebUiDesign",
    badge: "Component Library",
    description:
      "Projelerde kullanılan standart UI bileşenlerinin bulunduğu kütüphane. Button, Input, Table, Modal ve daha fazlası.",
    href: "#",
    accentColor: "#a855f7",
    glowColor: "rgba(168, 85, 247, 0.3)",
  },
  {
    icon: "⚛️",
    title: "NextReactSkeleton",
    badge: "UI Framework",
    description:
      "Next.js tabanlı, TebUiDesign entegrasyonu hazır proje iskeleti. Routing, layout ve tema yapılandırması dahil.",
    href: "#",
    accentColor: "#3b82f6",
    glowColor: "rgba(59, 130, 246, 0.3)",
  },
  {
    icon: "🔗",
    title: "BFF Initializer",
    badge: "BFF Framework",
    description:
      "Backend For Frontend katmanı oluşturmak için başlangıç şablonu. API proxy, auth ve servis entegrasyonları hazır.",
    href: "#",
    accentColor: "#06b6d4",
    glowColor: "rgba(6, 182, 212, 0.3)",
  },
  {
    icon: "📖",
    title: "Wiki",
    badge: "Dokümantasyon",
    description:
      "Tüm araçların kullanım kılavuzları, örnekler ve best practice rehberleri. Kurulum adımlarından advanced kullanıma.",
    href: "#",
    accentColor: "#14b8a6",
    glowColor: "rgba(20, 184, 166, 0.3)",
  },
];

export default function AllYouNeed() {
  return (
    <div className="page">
      <div className="card" style={{ maxWidth: 860 }}>

        {/* Header */}
        <div className="header">
          <div className="header-icon">🗺️</div>
          <div>
            <h1 className="title">All You Need</h1>
            <p className="subtitle">UI Projesi Geliştirici Rehberi</p>
          </div>
        </div>

        <div className="divider" />

        {/* Açıklama */}
        <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", lineHeight: 1.7 }}>
          Bir UI projesi geliştirmek için ihtiyaç duyacağın tüm kaynaklar aşağıda listelenmiştir.
          Önce <strong style={{ color: "var(--text-secondary)" }}>Wiki</strong>'yi okuyarak başlaman,
          ardından <strong style={{ color: "var(--text-secondary)" }}>NextReactSkeleton</strong> ile
          projeyi oluşturman önerilir.
        </p>

        <div className="divider" />

        {/* Kaynak Kartları */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))",
            gap: "1rem",
          }}
        >
          {RESOURCES.map((res) => (
            <a
              key={res.title}
              href={res.href}
              target="_blank"
              rel="noopener noreferrer"
              style={{ textDecoration: "none" }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.75rem",
                  padding: "1.25rem",
                  borderRadius: 14,
                  border: `1px solid ${res.accentColor}33`,
                  background: "rgba(10, 16, 35, 0.55)",
                  backdropFilter: "blur(8px)",
                  cursor: "pointer",
                  transition: "border-color 0.2s, box-shadow 0.2s, transform 0.15s",
                  height: "100%",
                }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLDivElement;
                  el.style.borderColor = res.accentColor;
                  el.style.boxShadow = `0 0 24px ${res.glowColor}`;
                  el.style.transform = "translateY(-2px)";
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLDivElement;
                  el.style.borderColor = `${res.accentColor}33`;
                  el.style.boxShadow = "none";
                  el.style.transform = "translateY(0)";
                }}
              >
                {/* Başlık satırı */}
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <div
                    style={{
                      width: 42,
                      height: 42,
                      borderRadius: 10,
                      background: `${res.accentColor}1a`,
                      border: `1px solid ${res.accentColor}40`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "1.3rem",
                      flexShrink: 0,
                    }}
                  >
                    {res.icon}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p
                      style={{
                        fontWeight: 700,
                        fontSize: "0.95rem",
                        color: "var(--text-primary)",
                        marginBottom: 2,
                      }}
                    >
                      {res.title}
                    </p>
                    <span
                      style={{
                        display: "inline-block",
                        fontSize: "0.68rem",
                        fontWeight: 600,
                        letterSpacing: "0.07em",
                        textTransform: "uppercase",
                        color: res.accentColor,
                        background: `${res.accentColor}18`,
                        border: `1px solid ${res.accentColor}30`,
                        borderRadius: 999,
                        padding: "1px 8px",
                      }}
                    >
                      {res.badge}
                    </span>
                  </div>
                  {/* Ok */}
                  <span
                    style={{
                      fontSize: "1.1rem",
                      color: res.accentColor,
                      opacity: 0.6,
                      flexShrink: 0,
                    }}
                  >
                    ↗
                  </span>
                </div>

                {/* Açıklama */}
                <p
                  style={{
                    fontSize: "0.82rem",
                    color: "var(--text-muted)",
                    lineHeight: 1.6,
                    margin: 0,
                  }}
                >
                  {res.description}
                </p>

                {/* Alt link göstergesi */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.35rem",
                    fontSize: "0.75rem",
                    color: res.accentColor,
                    fontWeight: 600,
                    marginTop: "auto",
                    paddingTop: "0.25rem",
                  }}
                >
                  <span
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: "50%",
                      background: res.accentColor,
                      display: "inline-block",
                      boxShadow: `0 0 6px ${res.accentColor}`,
                    }}
                  />
                  Sayfaya git
                </div>
              </div>
            </a>
          ))}
        </div>

        {/* Alt not */}
        <div className="divider" />
        <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textAlign: "center" }}>
          Link güncellemek için{" "}
          <code
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              background: "rgba(99,102,241,0.1)",
              padding: "1px 6px",
              borderRadius: 4,
              color: "var(--text-secondary)",
            }}
          >
            components/AllYouNeed/index.tsx
          </code>{" "}
          içindeki <code style={{ fontFamily: "'JetBrains Mono', monospace", background: "rgba(99,102,241,0.1)", padding: "1px 6px", borderRadius: 4, color: "var(--text-secondary)" }}>RESOURCES</code> dizisini düzenle.
        </p>
      </div>
    </div>
  );
}
