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


# ── basic-ui-lib bileşen kataloğu (ilk istekte diskten okunur) ────────────────
_lib_loaded: bool = False
LIBRARY_COMPONENTS: set[str] = set()
_LOWER_TO_COMPONENT: dict[str, str] = {}


def _ensure_loaded() -> None:
    global _lib_loaded
    if not _lib_loaded:
        comps = _load_library_components()
        LIBRARY_COMPONENTS.update(comps)
        _LOWER_TO_COMPONENT.update({c.lower(): c for c in comps})
        print(f"[utils] LIBRARY_COMPONENTS loaded: {sorted(LIBRARY_COMPONENTS)}")
        _lib_loaded = True


def get_library_components() -> set[str]:
    _ensure_loaded()
    return LIBRARY_COMPONENTS

# Standart HTML etiketleri — bu isimler için hata verilmez, Teb* karşılığı aranır
_GENERAL_TAGS: frozenset[str] = frozenset({
    "button", "input", "datepicker",
    "checkbox", "radio",
    "menu", "meter",
    "optgroup", "option", "progress", "search",
    "select", "textarea",
})

# İsim/görsel benzerliğe göre sabit HTML → Teb* eşleştirme tablosu
# search için TebInput kullanılır; icon prop'u (icon="search") çağıran tarafında eklenmeli
_HTML_TO_TEB: dict[str, str] = {
    "button":     "TebButton",
    "input":      "TebInput",
    "datepicker": "TebDatePicker",
    "checkbox":   "TebCheckbox",
    "radio":      "TebRadioButton",
    "textarea":   "TebTextarea",
    "menu":       "TebMenu",
    "meter":      "TebLinearProgress",
    "progress":   "TebLinearProgress",
    "optgroup":   "TebAutocomplete",   # grup seçenekleri → autocomplete
    "option":     "TebCombobox",       # tekil seçenek → combobox
    "search":     "TebInput",          # icon="search" prop'u ile kullanılmalı
    "select":     "TebAutocomplete",   # açılır liste → autocomplete
}


def _find_teb_equivalent(tag: str) -> str | None:
    """
    HTML etiket adına en yakın Teb* bileşenini bulur.

    Önce _HTML_TO_TEB sabit tablosuna bakar (isim/görsel benzerlik).
    Bulamazsa LIBRARY_COMPONENTS üzerinde:
      1. 'teb' + tag tam eşleşmesi
      2. tag adını içeren ilk bileşen
    sırasıyla arar.

    Özel durum:
      'search' → TebInput  (çağıran taraf icon="search" prop'unu eklemelidir)
    """
    _ensure_loaded()
    tag_lower = tag.lower().strip()

    # 1. Sabit eşleşme tablosu — en güvenilir kaynak
    explicit = _HTML_TO_TEB.get(tag_lower)
    if explicit:
        # Bileşenin kütüphanede gerçekten var olduğunu doğrula
        if explicit.lower() in _LOWER_TO_COMPONENT:
            return _LOWER_TO_COMPONENT[explicit.lower()]
        # Kütüphanede yoksa yine de sabit adı dön (geliştirme aşaması için)
        return explicit

    # 2. 'teb' + tag tam eşleşmesi
    exact_key = f"teb{tag_lower}"
    if exact_key in _LOWER_TO_COMPONENT:
        return _LOWER_TO_COMPONENT[exact_key]

    # 3. tag adını içeren ilk bileşen (kısmi eşleşme)
    for comp_lower, comp in _LOWER_TO_COMPONENT.items():
        if tag_lower in comp_lower:
            return comp

    return None


_TRACKED_PROPS: list[str] = ["name", "label", "placeholder", "value", "children"]
_NAME_PROP_PRIORITY: list[str] = ["label", "children", "placeholder", "name"]


def _extract_interface_block(content: str, type_name: str) -> str:
    """interface veya type bloğunun gövdesini dengeli süslü parantezle çıkarır."""
    pattern = rf'(?:interface|type)\s+{re.escape(type_name)}\b[^{{]*\{{'
    m = re.search(pattern, content)
    if not m:
        return ""
    start = m.end() - 1
    depth = 0
    i = start
    while i < len(content):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return content[start + 1 : i]
        i += 1
    return ""


def get_component_prop_keys(component_names: list[str]) -> dict[str, list[str]]:
    """Her component için TypeScript tanımında mevcut olan _TRACKED_PROPS anahtarlarını döner."""
    content = _load_dts_content()
    if not content:
        return {c: [] for c in component_names}

    result: dict[str, list[str]] = {}
    for comp in component_names:
        export_pattern = (
            rf'export\s+(?:declare\s+)?const\s+{re.escape(comp)}\s*[^<\n]*<\s*([A-Za-z_]\w*)'
        )
        m = re.search(export_pattern, content)
        found: list[str] = []
        if m:
            block = _extract_interface_block(content, m.group(1).strip())
            if block:
                for key in _TRACKED_PROPS:
                    if re.search(rf'(?<!\w){re.escape(key)}\s*\??\s*:', block):
                        found.append(key)
        result[comp] = found
    return result


def resolve_tokens_ordered(tokens: list[str]) -> list[str | None]:
    """
    Her token'ı sırasıyla canonical component adına çevirir;
    tekrarları **korur**, eşleşmeyenlere None döner.
    match_to_library'nin tekilleştirme davranışını kullanmaz.
    """
    _ensure_loaded()
    result: list[str | None] = []
    for token in tokens:
        key = token.strip().lower()
        lib_comp = _LOWER_TO_COMPONENT.get(key)
        if lib_comp:
            result.append(lib_comp)
        elif key in _GENERAL_TAGS:
            result.append(_find_teb_equivalent(key))
        else:
            result.append(None)
    return result


def resolve_name_props(
    prompt_tokens: list[str],
    names: list[str],
) -> list[dict]:
    """
    prompt_tokens ile names'i sıra korunarak (tekrarlar dahil) eşler.
    Her çift için TypeScript tanımından en uygun prop'u seçip
    [{component, props: {prop_key: name}}] döner.
    Eşleşmeyen veya boş isimli girişler atlanır.
    """
    canonical = resolve_tokens_ordered(prompt_tokens)
    # Yalnızca eşleşen (non-None) component'lerin canonical adlarını topla
    unique_comps = list({c for c in canonical if c})
    prop_keys_map = get_component_prop_keys(unique_comps)

    result: list[dict] = []
    for comp, name in zip(canonical, names):
        name = name.strip()
        if not comp or not name:
            continue
        available = prop_keys_map.get(comp, [])
        chosen = next((k for k in _NAME_PROP_PRIORITY if k in available), None)
        if chosen:
            result.append({"component": comp, "props": {chosen: name}})
    return result


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


def match_to_library(extracted: list[str]) -> tuple[list[str], list[str], dict[str, str]]:
    """
    Kullanıcının yazdığı bileşen adlarını LIBRARY_COMPONENTS ile birebir
    (büyük/küçük harf duyarsız) karşılaştırır.
    Standart HTML etiketleri için hata vermek yerine en yakın Teb* bileşenini bulur.

    Returns
    -------
    matched      : kütüphanede bulunan bileşenlerin orijinal adları
    unmatched    : kütüphanede karşılığı olmayan ham isimler
    html_mapped  : { html_tag: TebComponent } — otomatik eşleştirilen HTML etiketleri
    """
    _ensure_loaded()
    matched: list[str] = []
    unmatched: list[str] = []
    html_mapped: dict[str, str] = {}

    for item in extracted:
        key = item.strip().lower()
        lib_comp = _LOWER_TO_COMPONENT.get(key)
        if lib_comp:
            if lib_comp not in matched:
                matched.append(lib_comp)
        elif key in _GENERAL_TAGS:
            equiv = _find_teb_equivalent(key)
            if equiv:
                html_mapped[item.strip()] = equiv
                if equiv not in matched:
                    matched.append(equiv)
            # Karşılığı bulunamayan HTML etiketi → sessizce atla, hata verme
        else:
            # Fallback: LLM çok kelimeli string döndürdüyse her kelimeyi ayrı dene
            words = key.split()
            found_in_words = False
            if len(words) > 1:
                for word in words:
                    wlib = _LOWER_TO_COMPONENT.get(word)
                    if wlib:
                        if wlib not in matched:
                            matched.append(wlib)
                        found_in_words = True
                    elif word in _GENERAL_TAGS:
                        equiv = _find_teb_equivalent(word)
                        if equiv:
                            html_mapped[word] = equiv
                            if equiv not in matched:
                                matched.append(equiv)
                        found_in_words = True
            if not found_in_words:
                unmatched.append(item)

    return matched, unmatched, html_mapped
