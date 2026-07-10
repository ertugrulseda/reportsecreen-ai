import { useEffect, useState } from "react";
import "../../App.css";

const BARS = [65, 40, 80, 55, 90, 30, 70, 50, 85, 45];

export default function VersionComparator() {
  const [tick, setTick] = useState(0);
  const [dots, setDots] = useState("");

  useEffect(() => {
    const t = setInterval(() => setTick((p) => p + 1), 900);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 450);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="page">
      <div
        className="card"
        style={{
          alignItems: "center",
          textAlign: "center",
          gap: "2rem",
          paddingTop: "3.5rem",
          paddingBottom: "3.5rem",
        }}
      >
        {/* Icon */}
        <div
          style={{
            width: 72,
            height: 72,
            borderRadius: 18,
            background: "linear-gradient(135deg, #06b6d4, #14b8a6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 32px rgba(6,182,212,0.4)",
            fontSize: "2rem",
          }}
        >
          &#9878;
        </div>

        {/* Title */}
        <div>
          <h1 className="title" style={{ fontSize: "1.9rem" }}>
            Version Comparator
          </h1>
          <p className="subtitle" style={{ justifyContent: "center", marginTop: "0.5rem" }}>
            Sürüm Karşılaştırma Modülü
          </p>
        </div>

        {/* WIP Badge */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            padding: "0.45rem 1.1rem",
            borderRadius: 999,
            border: "1px solid rgba(6,182,212,0.4)",
            background: "rgba(6,182,212,0.08)",
            fontSize: "0.8rem",
            fontWeight: 600,
            color: "#67e8f9",
            letterSpacing: "0.06em",
            textTransform: "uppercase" as const,
          }}
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              background: "#67e8f9",
              boxShadow: "0 0 8px #67e8f9",
              animation: "pulse-dot 1.4s ease-in-out infinite",
              display: "inline-block",
            }}
          />
          Yazılım Çalışması Devam Ediyor
        </div>

        <div className="divider" style={{ width: "100%" }} />

        {/* Animated diff bars */}
        <div style={{ width: "100%", maxWidth: 420 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "0.6rem",
              fontSize: "0.75rem",
              color: "#475569",
              fontWeight: 600,
              textTransform: "uppercase" as const,
              letterSpacing: "0.06em",
            }}
          >
            <span>v1.x</span>
            <span>Diff Analizi{dots}</span>
            <span>v2.x</span>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "center",
              gap: 6,
              height: 80,
            }}
          >
            {BARS.map((h, i) => {
              const animated = Math.max(
                10,
                h + Math.sin((tick + i) * 0.8) * 15
              );
              const isLeft = i < BARS.length / 2;
              return (
                <div
                  key={i}
                  style={{
                    width: 18,
                    height: `${animated}%`,
                    borderRadius: 4,
                    background: isLeft
                      ? "linear-gradient(to top, #7c3aed, #a78bfa)"
                      : "linear-gradient(to top, #06b6d4, #67e8f9)",
                    opacity: 0.75,
                    transition: "height 0.8s ease",
                    boxShadow: isLeft
                      ? "0 0 8px rgba(124,58,237,0.4)"
                      : "0 0 8px rgba(6,182,212,0.4)",
                  }}
                />
              );
            })}
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "1.5rem",
              marginTop: "1rem",
              fontSize: "0.75rem",
              color: "#64748b",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 2,
                  background: "linear-gradient(135deg, #7c3aed, #a78bfa)",
                  display: "inline-block",
                }}
              />
              Mevcut
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 2,
                  background: "linear-gradient(135deg, #06b6d4, #67e8f9)",
                  display: "inline-block",
                }}
              />
              Hedef
            </span>
          </div>
        </div>

        <p style={{ fontSize: "0.78rem", color: "#475569", marginTop: "0.5rem" }}>
          Sürümler arası fark analizi yakında hazır olacak.
        </p>
      </div>
    </div>
  );
}
