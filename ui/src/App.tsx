import { useState, ChangeEvent } from "react";
import "./App.css";

interface GenerateResponse {
  generated_code: string;
  output_file: string;
  logs: string[];
  error: string;
}

type Layout = "vertical" | "horizontal";

// Her token "teb" ile başlayıp sadece harf içermeli, aralarında virgül olmalı, sonda virgül isteğe bağlı
const VALID_FORMAT = /^teb[a-z]+(,teb[a-z]+)*,?$/i;

function validatePrompt(value: string): boolean {
  if (!value.trim()) return false;
  return VALID_FORMAT.test(value.trim());
}

export default function App() {
  const [prompt, setPrompt] = useState<string>("");
  const [layout, setLayout] = useState<Layout>("vertical");
  const [promptError, setPromptError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  function handlePromptChange(e: ChangeEvent<HTMLInputElement>): void {
    const value = e.target.value;
    setPrompt(value);
    if (promptError) {
      if (value === "") {
        setPromptError(false);
      } else {
        setPromptError(!validatePrompt(value));
      }
    }
  }

  async function handleGenerate(): Promise<void> {
    if (!validatePrompt(prompt)) {
      setPromptError(true);
      return;
    }

    setPromptError(false);
    setLoading(true);
    setResult(null);
    setError(null);

    const requestBody = { prompt: prompt.trim() + " rapor ekranı oluştur", layout };

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail?.detail ?? `HTTP ${response.status}`);
      }

      const data: GenerateResponse = await response.json();
      if (data.error) {
        setError(data.error);
      }
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      {/* AI Loading Overlay */}
      {loading && (
        <div className="ai-overlay">
          <div className="ai-loader">
            <div className="ai-orb-ring">
              <div className="ai-orb">&#9679;</div>
            </div>
            <div className="ai-bars">
              {[...Array(7)].map((_, i) => (
                <div key={i} className="ai-bar" style={{ animationDelay: `${i * 0.1}s` }} />
              ))}
            </div>
            <p className="ai-label">
              Kod oluşturuluyor
              <span className="ai-thinking-dots">
                <span /><span /><span />
              </span>
            </p>
          </div>
        </div>
      )}

      <div className="card">
        {/* Header */}
        <div className="header">
          <div className="header-icon">&#9678;</div>
          <div>
            <h1 className="title">Report Screen Generator</h1>
            <p className="subtitle">AI-Powered Code Generation</p>
          </div>
        </div>

        <div className="divider" />

        {/* Form */}
        <div className="form">
          <div className="field">
            <label className="label" htmlFor="prompt">
              <span className="label-dot" />
              Filtre alanı componentleri
            </label>
            <input
              id="prompt"
              className={`input${promptError ? " input--error" : ""}`}
              type="text"
              value={prompt}
              onChange={handlePromptChange}
              placeholder="tebinput,tebcombobox,tebcheckbox"
            />
            {promptError && (
              <span className="field-error">
                &#9888; Yanlış formatta giriş yaptınız
              </span>
            )}
          </div>

          <div className="field">
            <label className="label" htmlFor="layout">
              <span className="label-dot" />
              Yerleşim
            </label>
            <select
              id="layout"
              className="select"
              value={layout}
              onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                setLayout(e.target.value as Layout)
              }
            >
              <option value="vertical">Vertical</option>
              <option value="horizontal">Horizontal</option>
            </select>
          </div>
        </div>

        <button
          className={`btn${loading ? " btn--loading" : ""}`}
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? "Oluşturuluyor…" : "Rapor Ekranı Oluştur"}
        </button>

        {/* Error */}
        {error && (
          <div className="error-box">
            <span>&#9888;</span>
            <span><strong>Hata:</strong> {error}</span>
          </div>
        )}

        {/* Result */}
        {result?.generated_code && (
          <div className="result">
            <div className="divider" />
            <div className="section">
              <p className="section-title">Oluşturulan Kod</p>
              <pre className="code-block">{result.generated_code}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
