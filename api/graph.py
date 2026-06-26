import json
import os
import random
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from state import State
from utils import LIBRARY_COMPONENTS, match_to_library
from prompts import build_ui_writer_prompt
from log_db import db_logger

load_dotenv()

llm = init_chat_model(
    model="qwen/qwen3-coder",
    model_provider="openai",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Node'lar ──────────────────────────────────────────────────────────────────

async def component_checker(state: State) -> dict:
    """
    Prompt'tan istenen UI bileşenlerini çıkarır ve basic-ui-lib ile karşılaştırır.
    - Eşleşmeyen varsa → error mesajı yazar, pipeline durur.
    - Tümü eşleşiyorsa → matched_components state'e eklenir, ui_writer devam eder.
    """
    prompt = state["prompt"]
    available = ", ".join(sorted(LIBRARY_COMPONENTS))

    extract_prompt = (
        "You are a UI component extractor.\n"
        "Extract every component or element name the user explicitly mentions in the description below.\n"
        "Rules:\n"
        "- Copy the names EXACTLY as written by the user — do NOT fix spelling, do NOT map to other names.\n"
        "- If the user writes 'button', return 'button'. If the user writes 'TebButton', return 'TebButton'.\n"
        "- Return ONLY a JSON array of strings, nothing else.\n\n"
        f"Description: {prompt}"
    )

    response = await llm.ainvoke([{"role": "user", "content": extract_prompt}])
    raw = response.content.strip()

    json_match = re.search(r"\[.*?\]", raw, re.DOTALL)
    try:
        extracted: list[str] = json.loads(json_match.group()) if json_match else []
    except (json.JSONDecodeError, AttributeError):
        extracted = []

    log_extract = f"[component_checker] Extracted elements: {extracted}"

    if not extracted:
        return {
            "matched_components": [],
            "logs": [log_extract, "[component_checker] No specific components detected; proceeding freely."],
        }

    matched, unmatched = match_to_library(extracted)

    if unmatched:
        missing_str = ", ".join(unmatched)
        error_msg = f"[{missing_str}] basic-ui-lib'de bulunmamaktadır."
        return {
            "error": error_msg,
            "matched_components": [],
            "logs": [
                log_extract,
                f"[component_checker] Matched   : {matched}",
                f"[component_checker] Unmatched : {unmatched}",
                f"[component_checker] ERROR     : {error_msg}",
            ],
        }

    return {
        "matched_components": matched,
        "logs": [
            log_extract,
            f"[component_checker] All components matched: {matched}",
        ],
    }


def _route_after_checker(state: State) -> str:
    """component_checker sonrası yönlendirme."""
    return "logger" if state.get("error") else "ui_writer"


async def ui_writer(state: State) -> dict:
    """Generates a React/TSX component based on the prompt."""
    prompt = state["prompt"]
    matched = state.get("matched_components", [])

    if matched:
        lib_hint = (
            "You MUST import and use the following components from 'basic-ui-lib': "
            + ", ".join(matched)
            + ".\n"
            f"Add this import at the top: import {{ {', '.join(matched)} }} from 'basic-ui-lib';\n"
        )
    else:
        lib_hint = ""

    layout = state.get("layout", "vertical")
    system_prompt = await build_ui_writer_prompt(lib_hint, matched, layout)

    response = await llm.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Create a React TSX component for: {prompt}"},
    ])

    code = response.content.strip()
    code = re.sub(r"^```(?:tsx|typescript|jsx|js)?\n?", "", code)
    code = re.sub(r"\n?```$", "", code)
    code = code.strip()

    # Var olan tüm dosyaları temizle
    for existing in OUTPUT_DIR.iterdir():
        if existing.is_file():
            existing.unlink()

    random_suffix = random.randint(1000, 9999)
    filename = f"Screen_{random_suffix}.tsx"
    output_path = OUTPUT_DIR / filename
    output_path.write_text(code, encoding="utf-8")

    return {
        "generated_code": code,
        "output_file": str(output_path),
        "logs": [f"[ui_writer] Component generated and saved to {filename}"],
    }


async def logger(state: State) -> dict:
    """Logs the result of the generation pipeline."""
    timestamp = datetime.now().isoformat(timespec="seconds")
    output_file = state.get("output_file", "")
    code_lines = len(state.get("generated_code", "").splitlines())
    error = state.get("error", "")

    log_entries = [
        f"[logger] {timestamp} — Pipeline finished",
        f"[logger] Status     : {'ERROR' if error else 'OK'}",
    ]
    if error:
        log_entries.append(f"[logger] Error      : {error}")
    else:
        log_entries.append(f"[logger] Output file: {output_file}")
        log_entries.append(f"[logger] Lines      : {code_lines}")

    for entry in log_entries:
        print(entry)

    return {"logs": log_entries}


# ── Graph ─────────────────────────────────────────────────────────────────────
builder = StateGraph(State)

builder.add_node("component_checker", component_checker)
builder.add_node("ui_writer", ui_writer)
builder.add_node("logger", logger)
builder.add_node("db_logger", db_logger)

builder.add_edge(START, "component_checker")
builder.add_conditional_edges("component_checker", _route_after_checker, ["ui_writer", "logger"])
builder.add_edge("ui_writer", "logger")
builder.add_edge("logger", "db_logger")
builder.add_edge("db_logger", END)

agent_graph = builder.compile()

# Show workflow
graph_png = agent_graph.get_graph().draw_mermaid_png()
with open("workflow_graph.png", "wb") as f:
    f.write(graph_png)
print("Graph saved as workflow_graph.png")
