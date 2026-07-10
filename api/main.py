import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reportgeneratorapi.graph import agent_graph

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
    layout: str = "vertical"      # "vertical" | "horizontal"
    secondary_title: str = ""     # TebRichHeader secondaryTitle
    info_label: str = ""          # TebRichHeader infoLabel
    component_names: str = ""     # virgülle ayrılmış isimler, prompt sırasıyla eşleşir
    grid_columns: str = ""        # virgülle ayrılmış kolon başlıkları


class GenerateResponse(BaseModel):
    generated_code: str
    output_file: str
    logs: list[str]
    error: str


# ── Endpoint'ler ─────────────────────────────────────────────────────────────
@app.post("/generate", response_model=GenerateResponse)
async def generate_ui(request: GenerateRequest):
    try:
        result = await agent_graph.ainvoke({
            "prompt": request.prompt,
            "layout": request.layout,
            "secondary_title": request.secondary_title,
            "info_label": request.info_label,
            "component_names": request.component_names,
            "grid_columns": request.grid_columns,
            "component_props": [],
            "error": "",
            "generated_code": "",
            "output_file": "",
            "logs": [],
            "matched_components": [],
        })
    except Exception:
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
