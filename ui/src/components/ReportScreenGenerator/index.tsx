import { useState, ChangeEvent } from "react";
import "../../App.css";

interface GenerateResponse {
  generated_code: string;
  output_file: string;
  logs: string[];
  error: string;
}

type Layout = "vertical" | "horizontal";

function validatePrompt(value: string): boolean {
  const trimmed = value.trim().replace(/,$/, "");
  if (!trimmed) return false;
  return trimmed.split(",").every((t) => /^[a-z][a-z0-9]*$/i.test(t.trim()));
}

export default function ReportScreenGenerator() {
  const [secondaryTitle, setSecondaryTitle] = useState<string>("");
  const [infoLabel, setInfoLabel] = useState<string>("");
  const [prompt, setPrompt] = useState<string>("");
  const [componentNames, setComponentNames] = useState<string>("");
  const [gridColumns, setGridColumns] = useState<string>("");
  const [layout, setLayout] = useState<Layout>("vertical");
  const [promptError, setPromptError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [reportNo, setReportNo] = useState<string>("");
  const [fetchLoading, setFetchLoading] = useState<boolean>(false);
  const [dosyaUrl, setDosyaUrl] = useState<string>("");
  const [analyzeLoading, setAnalyzeLoading] = useState<boolean>(false);

  async function handleFetchReport(): Promise<void> {
    const name = reportNo.trim();
    if (!name) return;

    setFetchLoading(true);
    try {
      //0 prosedürün yazılı olduğu .prc dosyasını oku ve api/alayze'a gönder
      //bana api/analyze'dan ham json dönecek  

      // 1. Ham rapor JSON'unu çek
      const rawRes = await fetch(
        `http://localhost:8000/reportgeneratorapi/hamjson/${encodeURIComponent(name)}`
      );
      const rawText = await rawRes.text();
      const rawData = JSON.parse(rawText);
      console.log("Ham rapor JSON:", rawData);

      // 2. Transform API'ye gönder
      const transformRes = await fetch("http://localhost:8000/reportgeneratorapi/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rawData),
      });
      const transformData = await transformRes.json();
      console.log("Transform sonucu:", transformData);

      // 3. Root alanlarını doldur
      if (transformData.report_title) setSecondaryTitle(transformData.report_title);

      // 4. filter_components'ten inputType ve label'ları al
      if (Array.isArray(transformData.filter_components)) {
        const visible = transformData.filter_components.filter(
          (c: { inputType?: string }) => c.inputType && c.inputType !== "hidden"
        );

        const inputTypes = visible
          .map((c: { inputType?: string }) => c.inputType)
          .join(",");
        setPrompt(inputTypes);

        const labels = visible
          .map((c: { label?: string }) => (c.label !== undefined && c.label !== null && c.label !== "" ? c.label : "empty"))
          .join(",");
        setComponentNames(labels);
      }
    } finally {
      setFetchLoading(false);
    }
  }

  function handleCopy(code: string): void {
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(code).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = code;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

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

    const requestBody = {
      prompt: prompt.trim() + " rapor ekranı oluştur",
      layout,
      secondary_title: secondaryTitle.trim(),
      info_label: infoLabel.trim(),
      component_names: componentNames.trim(),
      grid_columns: gridColumns.trim(),
    };

    try {
      const response = await fetch("http://localhost:8000/reportgeneratorapi/generate", {
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
      {/* AI Loading Overlay — Kod oluşturma */}
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

      {/* AI Loading Overlay — Bilgi getirme */}
      {fetchLoading && (
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
              Bilgiler getiriliyor
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

          {/* Rapor Tanımından Bilgileri Oku */}
          <p className="section-group-label">Rapor Tanımından Bilgileri Oku</p>
          <div className="section-box">
            <div className="report-fetch-row">
              <div className="field" style={{ flex: 1 }}>
                <label className="label" htmlFor="reportNo">
                  <span className="label-dot" />
                  Rapor No
                </label>
                <input
                  id="reportNo"
                  className="input"
                  type="text"
                  value={reportNo}
                  onChange={(e) => setReportNo(e.target.value)}
                  placeholder="Örn: RPT-001"
                />
              </div>
              <button
                className="btn btn--secondary"
                onClick={handleFetchReport}
                disabled={fetchLoading}
              >
                {fetchLoading ? "Getiriliyor…" : "Bilgileri Getir"}
              </button>
            </div>
            <div className="report-fetch-row">
              <div className="field" style={{ flex: 1 }}>
                <label className="label" htmlFor="dosyaUrl">
                  <span className="label-dot" />
                  Dosya Url
                </label>
                <input
                  id="dosyaUrl"
                  className="input"
                  type="text"
                  value={dosyaUrl}
                  onChange={(e) => setDosyaUrl(e.target.value)}
                  placeholder="Örn: https://..."
                />
              </div>
              <button
                className="btn btn--secondary"
                onClick={() => {}}
                disabled={analyzeLoading}
              >
                {analyzeLoading ? "Analiz ediliyor…" : "Analiz Et"}
              </button>
            </div>
          </div>

          <div className="divider" />

          {/* Header Bilgileri */}
          <p className="section-group-label">Header Bilgileri</p>
          <div className="section-box">
            <div className="field">
              <label className="label" htmlFor="secondaryTitle">
                <span className="label-dot" />
                Ekran Adı
              </label>
              <input
                id="secondaryTitle"
                className="input"
                type="text"
                value={secondaryTitle}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setSecondaryTitle(e.target.value)}
                placeholder="Örn: Raporlama Modülü"
              />
            </div>
            <div className="field">
              <label className="label" htmlFor="infoLabel">
                <span className="label-dot" />
                Bilgi Etiketi
              </label>
              <input
                id="infoLabel"
                className="input"
                type="text"
                value={infoLabel}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setInfoLabel(e.target.value)}
                placeholder="Örn: v1.0.0"
              />
            </div>
          </div>

          <div className="divider" />

          <p className="section-group-label">Filtre Alanları Bilgileri</p>
          <div className="section-box">
            <div className="field">
              <label className="label" htmlFor="prompt">
                <span className="label-dot" />
                Componentler
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
              <label className="label" htmlFor="componentNames">
                <span className="label-dot" />
                Component Etiketleri
              </label>
              <input
                id="componentNames"
                className="input"
                type="text"
                value={componentNames}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setComponentNames(e.target.value)}
                placeholder="Başlangıç Tarihi,Bitiş Tarihi,Durum"
              />
            </div>
          </div>

          <div className="field">
            <label className="label" htmlFor="gridColumns">
              <span className="label-dot" />
              Grid Kolon Başlıkları
            </label>
            <input
              id="gridColumns"
              className="input"
              type="text"
              value={gridColumns}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setGridColumns(e.target.value)}
              placeholder="Ad Soyad,Tutar,Tarih,Durum"
            />
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
              <div className="section-title-row">
                <p className="section-title">Oluşturulan Kod</p>
                <button
                  className={`copy-btn${copied ? " copy-btn--done" : ""}`}
                  onClick={() => handleCopy(result.generated_code)}
                  title="Kodu kopyala"
                >
                  {copied ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                  )}
                </button>
              </div>
              <pre className="code-block">{result.generated_code}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
