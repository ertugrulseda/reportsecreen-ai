import json
import logging
import os
import random
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

log = logging.getLogger(__name__)

from .state import State
from .utils import get_library_components, match_to_library, resolve_name_props
from .prompts import build_ui_writer_prompt
from .log_db import db_logger

load_dotenv()

llm = init_chat_model(
    model="qwen/qwen3-coder",
    model_provider="openai",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "reportgenerator"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Node'lar ──────────────────────────────────────────────────────────────────

async def component_checker(state: State) -> dict:
    """
    Prompt'tan istenen UI bileşenlerini çıkarır ve basic-ui-lib ile karşılaştırır.
    - Eşleşmeyen varsa → error mesajı yazar, pipeline durur.
    - Tümü eşleşiyorsa → matched_components state'e eklenir, ui_writer devam eder.
    """
    log.info("[STEP] component_checker — başladı")
    global _graph_png_saved
    if not _graph_png_saved:
        graph_png = agent_graph.get_graph().draw_mermaid_png()
        graph_path = OUTPUT_DIR / "workflow_graph.png"
        with open(graph_path, "wb") as f:
            f.write(graph_png)
        log.info("Graph saved as %s", graph_path)
        _graph_png_saved = True

    prompt = state["prompt"]
    log.info("[STEP] component_checker → get_library_components()")
    available = ", ".join(sorted(get_library_components()))

    extract_prompt = (
        "You are a UI component extractor.\n"
        "From the description below, extract ONLY the UI component or HTML element type names.\n"
        "Rules:\n"
        "- Extract ONLY the element/component type word (e.g. 'button', 'input', 'TebButton').\n"
        "- Do NOT include surrounding text, page names, screen names, or descriptions.\n"
        "- Each entry must be a single word — the element type only.\n"
        "- Copy the names EXACTLY as written by the user — do NOT fix spelling, do NOT map to other names.\n"
        "- If the user writes 'button rapor ekranı', return 'button'. If the user writes 'TebButton', return 'TebButton'.\n"
        "- Return ONLY a JSON array of strings, nothing else. Example: [\"button\", \"input\"]\n\n"
        f"Description: {prompt}"
    )

    log.info("[STEP] component_checker → llm.ainvoke() | prompt: %r", prompt)
    try:
        response = await llm.ainvoke([{"role": "user", "content": extract_prompt}])
    except Exception as e:
        print("[ERROR] component_checker → llm.ainvoke() başarısız: %s: %s", type(e).__name__, e)
        return {"matched_components": [], "logs": [f"[component_checker] LLM hatası: {e}"]}
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

    log.info("[STEP] component_checker → match_to_library() | extracted: %s", extracted)
    matched, unmatched, html_mapped = match_to_library(extracted)

    logs = [log_extract]

    if html_mapped:
        for html_tag, teb_comp in html_mapped.items():
            logs.append(f"[component_checker] HTML tag mapped: <{html_tag}> → {teb_comp}")

    if unmatched:
        missing_str = ", ".join(unmatched)
        error_msg = f"[{missing_str}] basic-ui-lib'de bulunmamaktadır."
        return {
            "error": error_msg,
            "matched_components": [],
            "logs": [
                *logs,
                f"[component_checker] Matched   : {matched}",
                f"[component_checker] Unmatched : {unmatched}",
                f"[component_checker] ERROR     : {error_msg}",
            ],
        }

    return {
        "matched_components": matched,
        "logs": [
            *logs,
            f"[component_checker] All components matched: {matched}",
        ],
    }


def _route_after_checker(state: State) -> str:
    """component_checker sonrası yönlendirme."""
    return "logger" if state.get("error") else "name_matcher"


async def name_matcher(state: State) -> dict:
    """
    Prompt'taki component sırası ile kullanıcının girdiği isimleri eşler.
    Her component için TypeScript tanımından en uygun prop seçilip
    component_props state'e yazılır.
    """
    log.info("[STEP] name_matcher — başladı")
    prompt = state["prompt"]
    component_names = state.get("component_names", "")

    prompt_tokens = [t.strip() for t in prompt.split(",") if t.strip()]
    name_tokens = [t.strip() for t in component_names.split(",")]

    log.info("[STEP] name_matcher → resolve_name_props() | prompt_tokens: %s | name_tokens: %s", prompt_tokens, name_tokens)
    component_props = resolve_name_props(prompt_tokens, name_tokens)

    logs = [f"[name_matcher] Resolved props: {component_props}"]
    return {"component_props": component_props, "logs": logs}


async def ui_writer(state: State) -> dict:
    """Generates a React/TSX component based on the prompt."""
    log.info("[STEP] ui_writer — başladı")
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
    secondary_title = state.get("secondary_title", "")
    info_label = state.get("info_label", "")
    component_props = state.get("component_props", [])
    grid_columns = state.get("grid_columns", "")
    log.info("[STEP] ui_writer → build_ui_writer_prompt() | matched: %s | layout: %r | secondary_title: %r | info_label: %r | component_props: %s | grid_columns: %r", matched, layout, secondary_title, info_label, component_props, grid_columns)
    system_prompt = await build_ui_writer_prompt(
        lib_hint, matched, layout, secondary_title, info_label, component_props, grid_columns
    )

    log.info("[STEP] ui_writer → llm.ainvoke() | prompt: %r", prompt)
    try:
        response = await llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a React TSX component for: {prompt}"},
        ])
    except Exception as e:
        print("[ERROR] ui_writer → llm.ainvoke() başarısız: %s: %s", type(e).__name__, e)
        return {"generated_code": "", "output_file": "", "logs": [f"[ui_writer] LLM hatası: {e}"]}

    code = response.content.strip()
    code = re.sub(r"^```(?:tsx|typescript|jsx|js)?\n?", "", code)
    code = re.sub(r"\n?```$", "", code)
    code = code.strip()

    # Var olan TSX dosyalarını temizle
    for existing in OUTPUT_DIR.glob("*.tsx"):
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
    log.info("[STEP] logger — başladı")
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
        log.info(entry)

    return {"logs": log_entries}


# ── Graph ─────────────────────────────────────────────────────────────────────
builder = StateGraph(State)

builder.add_node("component_checker", component_checker)
builder.add_node("name_matcher", name_matcher)
builder.add_node("ui_writer", ui_writer)
builder.add_node("logger", logger)
builder.add_node("db_logger", db_logger)

builder.add_edge(START, "component_checker")
builder.add_conditional_edges("component_checker", _route_after_checker, ["name_matcher", "logger"])
builder.add_edge("name_matcher", "ui_writer")
builder.add_edge("ui_writer", "logger")
builder.add_edge("logger", "db_logger")
builder.add_edge("db_logger", END)

agent_graph = builder.compile()

_graph_png_saved: bool = False
