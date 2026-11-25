import traceback
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from reportgeneratorapi.graph import agent_graph
from reportgeneratorapi.schemas import GenerateRequest, GenerateResponse

router = APIRouter()

@router.get("/hamjson", response_class=PlainTextResponse)
async def get_ham_json(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"'{file_path}' bulunamadı.")
    return path.read_text(encoding="utf-8")


@router.post("/generate", response_model=GenerateResponse)
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




@router.get("/health")
async def health():
    return {"status": "ok"}
