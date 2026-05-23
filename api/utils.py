import re
import tarfile
from pathlib import Path

import httpx

STORYBOOK_URL = "http://localhost:6006"

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def _parse_components_from_dts(dts_content: str) -> set[str]:
    """index.d.ts içindeki 'export const Teb*' isimlerini çıkarır."""
    return set(re.findall(r"export const (Teb\w+)", dts_content))


def _load_dts_content() -> str:
    """documents/ altındaki basic-ui-lib-*.tgz'den index.d.ts içeriğini döner."""
    matches = sorted(DOCUMENTS_DIR.glob("basic-ui-lib-*.tgz"))
    if not matches:
        return ""
    tgz_path = matches[-1]
    try:
        with tarfile.open(tgz_path, "r:gz") as tar:
            member = tar.getmember("package/index.d.ts")
            f = tar.extractfile(member)
            return f.read().decode("utf-8") if f else ""
    except Exception:
        return ""


def load_exported_types() -> str:
    """
    index.d.ts içindeki export enum ve export type isimlerini okur.
    Startup'ta prompts.py tarafından çağrılır.
    """
    dts = _load_dts_content()
    if not dts:
        return ""
    enums = re.findall(r"export enum (\w+)", dts)
    types = re.findall(r"export type (\w+)\s*=", dts)
    all_types = sorted(set(enums + types))
    return ", ".join(all_types)


def _load_library_components() -> set[str]:
    """Sunucu ayağa kalkarken basic-ui-lib-*.tgz'den component listesini okur."""
    matches = sorted(DOCUMENTS_DIR.glob("basic-ui-lib-*.tgz"))
    if not matches:
        return set()
    tgz_path = matches[-1]
    try:
        with tarfile.open(tgz_path, "r:gz") as tar:
            member = tar.getmember("package/index.d.ts")
            f = tar.extractfile(member)
            dts = f.read().decode("utf-8") if f else ""
        return _parse_components_from_dts(dts)
    except Exception:
        return set()


# ── basic-ui-lib bileşen kataloğu (startup'ta diskten okunur) ─────────────────
LIBRARY_COMPONENTS: set[str] = _load_library_components()
print(f"[utils] LIBRARY_COMPONENTS loaded: {sorted(LIBRARY_COMPONENTS)}")

# Hızlı arama için lowercase → orijinal ad eşlemesi
_LOWER_TO_COMPONENT: dict[str, str] = {c.lower(): c for c in LIBRARY_COMPONENTS}


def load_component_types() -> str:
    """documents/ altındaki basic-ui-lib-*.tgz dosyasını bulup index.d.ts okur."""
    content = _load_dts_content()
    return content if content else "(basic-ui-lib type definitions not found)"


def load_lint_rules() -> str:
    """Her çağrıda eslint.js ve prettier.json dosyalarını diskten okur."""
    eslint_path = DOCUMENTS_DIR / "eslint.js"
    prettier_path = DOCUMENTS_DIR / "prettier.json"

    eslint_content = eslint_path.read_text(encoding="utf-8") if eslint_path.exists() else "(not found)"
    prettier_content = prettier_path.read_text(encoding="utf-8") if prettier_path.exists() else "(not found)"

    return (
        "Prettier config (prettier.json):\n"
        f"{prettier_content}\n\n"
        "ESLint config (eslint.js):\n"
        f"{eslint_content}\n"
    )


async def load_storybook_examples(matched_components: list[str]) -> str:
    """
    Storybook'tan (localhost:6006) stories.json'u çeker.
    matched_components ile ilgili story'leri filtreler ve LLM için örnek olarak döner.
    Storybook erişilemezse boş string döner.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{STORYBOOK_URL}/stories.json")
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return ""

    stories = data.get("stories", {})
    if not stories:
        return ""

    # matched_components yoksa tüm story'leri al
    filter_names = [c.lower() for c in matched_components] if matched_components else []

    relevant: list[str] = []
    for story in stories.values():
        title: str = story.get("title", "")
        name: str = story.get("name", "")
        args: dict = story.get("args", {})

        if filter_names and not any(f in title.lower() for f in filter_names):
            continue

        entry = f"### {title} / {name}"
        if args:
            entry += f"\nArgs: {args}"
        relevant.append(entry)

    if not relevant:
        return ""

    return (
        "The following are real Storybook examples from the component library. "
        "Use them as reference for prop usage and patterns:\n\n"
        + "\n\n".join(relevant)
        + "\n\n"
    )


def match_to_library(extracted: list[str]) -> tuple[list[str], list[str]]:
    """
    Kullanıcının yazdığı bileşen adlarını LIBRARY_COMPONENTS ile birebir
    (büyük/küçük harf duyarsız) karşılaştırır.

    Returns
    -------
    matched   : kütüphanede bulunan bileşenlerin orijinal adları
    unmatched : kütüphanede karşılığı olmayan ham isimler
    """
    matched: list[str] = []
    unmatched: list[str] = []

    for item in extracted:
        lib_comp = _LOWER_TO_COMPONENT.get(item.strip().lower())
        if lib_comp:
            if lib_comp not in matched:
                matched.append(lib_comp)
        else:
            unmatched.append(item)

    return matched, unmatched
