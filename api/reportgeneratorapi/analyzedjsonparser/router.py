import copy
import json
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
from langchain.chat_models import init_chat_model

from reportgeneratorapi.analyzedjsonparser.prompts import SYSTEM_PROMPT, build_transform_prompt

load_dotenv()

router = APIRouter()

_llm = init_chat_model(
    model="qwen/qwen3-coder",
    model_provider="openai",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


@router.post("/transform-filters")
async def transform_filters(payload: Dict[str, Any] = Body(...)):
    """
    Gelen JSON'ı olduğu gibi döndürür; yalnızca filter_components dizisini
    kural setine göre LLM aracılığıyla dönüştürür.

    Dönüşüm kuralları (prompts.py):
      select          → TebAutoComplete
      text            → TebInput
      radio           → TebRadioButton
      WEB_ORTAK:
        f_2tarih_gir  → 2x TebDatePicker (Başlangıç / Bitiş)
        f_hesno_gir   → AccountSearch
        F_WEB_SUBE_COMBO → TebAutoComplete
        P_MUSTERI_SEC → CustomerSearch
    """
    if "filter_components" not in payload:
        raise HTTPException(status_code=422, detail="'filter_components' alanı zorunludur.")

    user_message = build_transform_prompt(payload["filter_components"])

    try:
        response = await _llm.ainvoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM hatası: {e}")

    raw = response.content.strip()

    # Markdown fence varsa soy
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    # JSON array'i bul ve parse et
    json_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not json_match:
        raise HTTPException(
            status_code=500,
            detail=f"LLM geçerli bir JSON array döndürmedi. Ham yanıt: {raw[:500]}",
        )

    try:
        transformed: list = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON parse hatası: {e}")

    result = copy.deepcopy(payload)
    result["filter_components"] = transformed
    return result
