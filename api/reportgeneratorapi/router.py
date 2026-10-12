import traceback
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from reportgeneratorapi.graph import agent_graph
from reportgeneratorapi.jsontoreport import transform_report
from reportgeneratorapi.schemas import GenerateRequest, GenerateResponse, TransformRequest, TransformResponse

router = APIRouter()

ANALYZED_REPORTS_DIR = Path(__file__).parent / "AnalyzedReports"


@router.get("/hamjson/{file_name}", response_class=PlainTextResponse)
async def get_ham_json(file_name: str):
    file_path = ANALYZED_REPORTS_DIR / file_name
    if not file_path.exists():
        file_path = ANALYZED_REPORTS_DIR / f"{file_name}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"'{file_name}' bulunamadı.")
    return file_path.read_text(encoding="utf-8")


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


@router.post("/transform", response_model=TransformResponse)
async def transform_json(request: TransformRequest):
    try:
        result = await transform_report(request.model_dump())
        return TransformResponse(**result)
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@router.get("/health")
async def health():
    return {"status": "ok"}
