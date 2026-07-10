import { useEffect, useState } from "react";
import "../../App.css";

const STEPS = [
  "Paket bağımlılıkları analiz ediliyor",
  "Sürüm geçmişi taranıyor",
  "Değişiklik günlüğü hazırlanıyor",
  "Release taslağı oluşturuluyor",
];

export default function ReleaseManager() {
  const [activeStep, setActiveStep] = useState(0);
  const [dots, setDots] = useState("");

  useEffect(() => {
    const stepTimer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % STEPS.length);
    }, 1800);
    return () => clearInterval(stepTimer);
  }, []);

  useEffect(() => {
    const dotTimer = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 450);
    return () => clearInterval(dotTimer);
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
            background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 32px rgba(124,58,237,0.45)",
            fontSize: "2rem",
          }}
        >
          &#128640;
        </div>

        {/* Title */}
        <div>
          <h1 className="title" style={{ fontSize: "1.9rem" }}>
            Release Manager
          </h1>
          <p className="subtitle" style={{ justifyContent: "center", marginTop: "0.5rem" }}>
            Sürüm Yönetim Modülü
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
            border: "1px solid rgba(124,58,237,0.4)",
            background: "rgba(124,58,237,0.1)",
            fontSize: "0.8rem",
            fontWeight: 600,
            color: "#a78bfa",
            letterSpacing: "0.06em",
            textTransform: "uppercase" as const,
          }}
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              background: "#a78bfa",
              boxShadow: "0 0 8px #a78bfa",
              animation: "pulse-dot 1.4s ease-in-out infinite",
              display: "inline-block",
            }}
          />
          Geliştirme Devam Ediyor
        </div>

        <div className="divider" style={{ width: "100%" }} />

        {/* Progress steps */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
            width: "100%",
            maxWidth: 400,
          }}
        >
          {STEPS.map((step, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.65rem 1rem",
                borderRadius: 10,
                border: `1px solid ${i === activeStep ? "rgba(124,58,237,0.5)" : "rgba(255,255,255,0.05)"}`,
                background: i === activeStep ? "rgba(124,58,237,0.1)" : "rgba(255,255,255,0.02)",
                transition: "all 0.4s ease",
                opacity: i === activeStep ? 1 : 0.35,
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  flexShrink: 0,
                  background: i === activeStep ? "#a78bfa" : "rgba(255,255,255,0.2)",
                  boxShadow: i === activeStep ? "0 0 10px #a78bfa" : "none",
                  transition: "all 0.4s ease",
                }}
              />
              <span
                style={{
                  fontSize: "0.85rem",
                  color: i === activeStep ? "#e2e8f0" : "#475569",
                }}
              >
                {step}
                {i === activeStep ? dots : ""}
              </span>
            </div>
          ))}
        </div>

        <p style={{ fontSize: "0.78rem", color: "#475569", marginTop: "0.5rem" }}>
          Bu modül yakında kullanıma açılacak.
        </p>
      </div>
    </div>
  );
}
