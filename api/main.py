import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import agent_graph

app = FastAPI(title="UI Code Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Şemalar ──────────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    prompt: str
    layout: str = "vertical"  # "vertical" | "horizontal"


class GenerateResponse(BaseModel):
    generated_code: str
    output_file: str
    logs: list[str]
    error: str


# ── Endpoint'ler ─────────────────────────────────────────────────────────────
@app.post("/generate", response_model=GenerateResponse)
async def generate_ui(request: GenerateRequest):
    """
    Verilen prompt'a göre:
    1. React/TSX bileşeni üretir  (UI Writer Agent)
    2. Kodu ESLint + Prettier'a göre düzenler (Linter Agent)
    3. İşlem loglarını konsola basar  (Logger Agent)
    """
    try:
        result = await agent_graph.ainvoke({
            "prompt": request.prompt,
            "layout": request.layout,
            "error": "",
            "generated_code": "",
            "output_file": "",
            "logs": [],
            "matched_components": [],
        })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=traceback.format_exc())

    return GenerateResponse(
        generated_code=result.get("generated_code", ""),
        output_file=result.get("output_file", ""),
        logs=result.get("logs", []),
        error=result.get("error", ""),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
