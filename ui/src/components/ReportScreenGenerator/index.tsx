import { useState, ChangeEvent } from "react";
import "./style.css";

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
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedFiles2, setSelectedFiles2] = useState<File[]>([]);
  const [analyzeLoading, setAnalyzeLoading] = useState<boolean>(false);
  const [inputMode, setInputMode] = useState<"manuel" | "rapor">("manuel");
  const [analyzedJson, setAnalyzedJson] = useState<Record<string, unknown> | null>(null);

  async function handleFetchReport(): Promise<void> {
    if (selectedFiles.length === 0 || selectedFiles2.length === 0) return;

    setFetchLoading(true);
    try {
      const gText = await selectedFiles[0].text();
      const sText = await selectedFiles2[0].text();

      const formData = new FormData();
      formData.append("G", gText);
      formData.append("S", sText);

      const res = await fetch("http://localhost:8000/webreportanalyze/analyze/analyze-report", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json();
        throw new Error(detail?.detail ?? `HTTP ${res.status}`);
      }

      const data = await res.json();
      console.log("Analiz sonucu:", data);

      if (data.report_title) setSecondaryTitle(data.report_title);

      // filter_components'ı dönüştürmek için transform-filters'a gönder
      const transformRes = await fetch("http://localhost:8000/analyzedjsonparser/transform-filters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!transformRes.ok) {
        const detail = await transformRes.json();
        throw new Error(detail?.detail ?? `HTTP ${transformRes.status}`);
      }

      const transformedData = await transformRes.json();
      console.log("Transform sonucu:", transformedData);

      if (Array.isArray(transformedData.filter_components)) {
        const visible = transformedData.filter_components.filter(
          (c: { inputType?: string }) => c.inputType && c.inputType !== "hidden"
        );
        setPrompt([...visible.map((c: { inputType?: string }) => c.inputType), "TebButton"].join(","));
        setComponentNames(
          [...visible
            .map((c: { label?: string }) =>
              c.label !== undefined && c.label !== null && c.label !== "" ? c.label : "empty"
            ), "Sorgula"]
            .join(",")
        );
      }

      setAnalyzedJson(transformedData);
    } catch (err) {
      setError((err as Error).message);
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

      // Java dosyalarını ZIP olarak indir
      if (analyzedJson) {
        const downloadRes = await fetch("http://localhost:8000/api/v1/java-files/download", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(analyzedJson),
        });

        if (!downloadRes.ok) {
          const detail = await downloadRes.json();
          throw new Error(detail?.detail ?? `HTTP ${downloadRes.status}`);
        }

        const blob = await downloadRes.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "generated-java-files.zip";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function handleClear(): void {
    setSecondaryTitle("");
    setInfoLabel("");
    setPrompt("");
    setComponentNames("");
    setGridColumns("");
    setLayout("vertical");
    setPromptError(false);
    setResult(null);
    setError(null);
    setReportNo("");
    setSelectedFiles([]);
    setSelectedFiles2([]);
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

          {/* Mod Seçimi */}
          <div className="mode-radio-group">
            <label className="mode-radio-label">
              <input
                type="radio"
                name="inputMode"
                value="rapor"
                checked={inputMode === "rapor"}
                onChange={() => setInputMode("rapor")}
              />
              Rapor Tanımından Ekran Oluştur
            </label>
            <label className="mode-radio-label">
              <input
                type="radio"
                name="inputMode"
                value="manuel"
                checked={inputMode === "manuel"}
                onChange={() => setInputMode("manuel")}
              />
              Manuel Giriş
            </label>
          </div>

          <div className="divider" />

          {/* Rapor Tanımından Bilgileri Oku */}
          <p className={`section-group-label${inputMode === "manuel" ? " section-group-label--disabled" : ""}`}>Rapor Tanımından Bilgileri Oku</p>
          <div className={`section-box${inputMode === "manuel" ? " section-box--disabled" : ""}`}>
            <div className="report-fetch-row">
              <div className="field" style={{ flex: 1 }}>
                <label className="label" htmlFor="reportNo">
                  <span className="label-dot" />
                 Giriş Dosyasını Seç _G
                </label>
                <label htmlFor="filtrebilgileridosyaurlid" className={`file-upload-label${inputMode === "manuel" ? " file-upload-label--disabled" : ""}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                  <span>{selectedFiles.length > 0 ? `${selectedFiles.length} dosya seçildi` : "Dosya seç"}</span>
                </label>
                <input
                  id="filtrebilgileridosyaurlid"
                  type="file"
                  accept=".prc,.sql"
                  disabled={inputMode === "manuel"}
                  style={{ display: "none" }}
                  onChange={(e) => setSelectedFiles(e.target.files ? Array.from(e.target.files) : [])}
                />
                {selectedFiles.length > 0 && (
                  <div className="extra-files-list" style={{ marginTop: "8px" }}>
                    {selectedFiles.map((f, i) => (
                      <span key={i} className="extra-file-tag">
                        {f.name}
                        <button
                          className="extra-file-remove"
                          onClick={() => setSelectedFiles(selectedFiles.filter((_, j) => j !== i))}
                          title="Kaldır"
                        >×</button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label className="label" htmlFor="filtrebilgileridosyaurlid2">
                  <span className="label-dot" />
                  Sonuç Dosyasını Seç _S
                </label>
                <label htmlFor="filtrebilgileridosyaurlid2" className={`file-upload-label${inputMode === "manuel" ? " file-upload-label--disabled" : ""}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                  <span>{selectedFiles2.length > 0 ? `${selectedFiles2.length} dosya seçildi` : "Dosya seç"}</span>
                </label>
                <input
                  id="filtrebilgileridosyaurlid2"
                  type="file"
                  accept=".prc,.sql"
                  disabled={inputMode === "manuel"}
                  style={{ display: "none" }}
                  onChange={(e) => setSelectedFiles2(e.target.files ? Array.from(e.target.files) : [])}
                />
                {selectedFiles2.length > 0 && (
                  <div className="extra-files-list" style={{ marginTop: "8px" }}>
                    {selectedFiles2.map((f, i) => (
                      <span key={i} className="extra-file-tag">
                        {f.name}
                        <button
                          className="extra-file-remove"
                          onClick={() => setSelectedFiles2(selectedFiles2.filter((_, j) => j !== i))}
                          title="Kaldır"
                        >×</button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="field" style={{ flex: "none" }}>
                <span className="label" style={{ visibility: "hidden" }}>_</span>
                <button
                  className="btn btn--secondary"
                  onClick={handleFetchReport}
                  disabled={fetchLoading || selectedFiles.length === 0 || selectedFiles2.length === 0 || inputMode === "manuel"}
                >
                  {fetchLoading ? "Getiriliyor…" : "Analiz Et"}
                </button>
              </div>
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
                className={`input${inputMode === "rapor" ? " input--readonly" : ""}`}
                type="text"
                value={secondaryTitle}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setSecondaryTitle(e.target.value)}
                readOnly={inputMode === "rapor"}
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
                className={`input${inputMode === "rapor" ? " input--readonly" : ""}`}
                type="text"
                value={infoLabel}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setInfoLabel(e.target.value)}
                readOnly={inputMode === "rapor"}
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
                className={`input${promptError ? " input--error" : ""}${inputMode === "rapor" ? " input--readonly" : ""}`}
                type="text"
                value={prompt}
                onChange={handlePromptChange}
                readOnly={inputMode === "rapor"}
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
                className={`input${inputMode === "rapor" ? " input--readonly" : ""}`}
                type="text"
                value={componentNames}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setComponentNames(e.target.value)}
                readOnly={inputMode === "rapor"}
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
              className={`input${inputMode === "rapor" ? " input--readonly" : ""}`}
              type="text"
              value={gridColumns}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setGridColumns(e.target.value)}
              readOnly={inputMode === "rapor"}
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

        <div className="action-row">
          <button
            className={`btn${loading ? " btn--loading" : ""}`}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Oluşturuluyor…" : "Rapor Ekranı Oluştur"}
          </button>
          <button
            className="btn btn--ghost"
            onClick={handleClear}
            disabled={loading}
          >
            Temizle
          </button>
        </div>

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
