from .utils import load_component_types, load_lint_rules, load_storybook_examples, load_exported_types

# Sunucu ayağa kalkarken bir kez okunur
_EXPORTED_TYPES: str = load_exported_types()
print(f"[prompts] Exported types loaded: {_EXPORTED_TYPES}")


_VERTICAL_LAYOUT = (
    "MANDATORY LAYOUT — VERTICAL MODE:\n"
    "The returned JSX MUST follow this exact structure, no exceptions:\n"
    "<TebLayoutGrid container spacing='4px' columns={24}>\n"
    "  <TebLayoutGrid child columns={24}>\n"
    "    <TebRichHeader variant={HeaderVariant.filled} />           {/* 1. Always first, full width */}\n"
    "  </TebLayoutGrid>\n"
    "  <TebLayoutGrid child lg={6} md={6} sm={6} style={{ margin: '4px' }}>\n"
    "    <TebCard>                                   {/* 2. Left — filter area — NO title prop */}\n"
    "      <div style={{ width: '100%' , display: 'flex', flexDirection: 'column', gap: '16px',paddingTop: '8px', boxSizing: 'border-box', }}>\n"
    "        {{ ...filter components from prompt... }}\n"
    "      </div>\n"
    "    </TebCard>\n"
    "  </TebLayoutGrid>\n"
    "  <TebLayoutGrid child lg={18} md={18} sm={18} >\n"
    "    <TebDataGridEnterprise ... />               {/* 3. Right — data grid */}\n"
    "  </TebLayoutGrid>\n"
    "</TebLayoutGrid>\n"
)

_HORIZONTAL_LAYOUT = (
    "MANDATORY LAYOUT — HORIZONTAL MODE:\n"
    "The returned JSX MUST follow this exact structure, no exceptions:\n"
    "<TebLayoutGrid container spacing='4px' columns={24}>\n"
    "  <TebLayoutGrid child columns={24} lg={24} md={24} sm={24}>\n"
    "    <TebRichHeader variant={HeaderVariant.filled} />           {/* 1. Always first, full width */}\n"
    "  </TebLayoutGrid>\n"
    "  <TebLayoutGrid child columns={24} lg={24} md={24} sm={24} style={{ margin: '4px'}}>\n"
    "    <TebCard width='full' disableHorizontalScroll={true} disableVerticalScroll={true}\n"
    "             height='fit-content'>                          {/* 2. Filter area — NO title prop, no scroll, height fits content */}\n"
    "      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-start', gap: '8px'}}>\n"
    "        {{  ...Count the total number of filter components (N). \n"
    "            The container is 1200px wide. Calculate each component's pixel width as: floor((1200 - (N - 1) * 8) / N) \n"
    "            Use the resulting integer pixel value (e.g. for N=3: floor((1200 - 16) / 3) = 394). \n"
    "            If the component has a width prop, pass this integer value directly: width={394} \n"
    "            If the component does not have a width prop, wrap it in a <div style={{ width: 394 }}> \n"
    "            Replace N with the actual count of filter components. }}\n"
    "      </div>\n"
    "    </TebCard>\n"
    "  </TebLayoutGrid>\n"
    "  <TebLayoutGrid child columns={24} lg={24} md={24} sm={24}>\n"
    "    <TebDataGridEnterprise ... />               {/* 3. Data grid — below TebCard */}\n"
    "  </TebLayoutGrid>\n"
    "</TebLayoutGrid>\n"
)


def _build_prop_overrides(component_props: list[dict]) -> str:
    """
    [{component, props: {key: value}}] listesinden AI prompt'u için
    zorunlu prop değerleri bloğu oluşturur.
    children prop'u JSX inner-text sözdizimi olarak gösterilir.
    """
    lines: list[str] = []
    for entry in component_props:
        comp = entry.get("component", "")
        props: dict = entry.get("props", {})
        non_empty = {k: v for k, v in props.items() if v and str(v).strip()}
        if not comp or not non_empty:
            continue

        children_val = non_empty.pop("children", None)
        other_parts = []
        for key, val in non_empty.items():
            val = str(val).strip()
            if val.startswith("{") and val.endswith("}"):
                other_parts.append(f"{key}={val}")
            else:
                other_parts.append(f'{key}="{val}"')

        if children_val is not None:
            # children için JSX sözdizimini açıkça göster
            props_str = (" " + " ".join(other_parts)) if other_parts else ""
            lines.append(f"  {comp}: MUST be written as <{comp}{props_str}>{children_val}</{comp}> — NEVER use children as a prop attribute")
        elif other_parts:
            lines.append(f"  {comp}: {', '.join(other_parts)}")

    if not lines:
        return ""

    return (
        "MANDATORY PROP VALUES — use these exact values, do NOT use placeholder text or invent alternatives:\n"
        + "\n".join(lines)
        + "\n\n"
    )


async def build_ui_writer_prompt(
    lib_hint: str,
    matched_components: list[str],
    layout: str = "vertical",
    secondary_title: str = "",
    info_label: str = "",
    component_props: list[dict] | None = None,
    grid_columns: str = "",
) -> str:
    storybook_examples = await load_storybook_examples(matched_components)
    layout_rule = _VERTICAL_LAYOUT if layout.lower() == "vertical" else _HORIZONTAL_LAYOUT
    prop_overrides = _build_prop_overrides(component_props or [])

    cols = [c.strip() for c in grid_columns.split(",") if c.strip()]
    grid_columns_rule = (
        "TebDataGridEnterprise columnDefs MUST contain exactly these columns in this order:\n"
        + "".join(
            f"  {{ field: '{c}', headerName: '{c}', flex: 1 }}\n"
            for c in cols
        )
        + "\n"
    ) if cols else ""

    return (
        "You are an expert React/TypeScript UI developer.\n"
        "Generate a clean, well-structured React TSX component based on the user's description.\n\n"
        + lib_hint
        + prop_overrides
        + "The following are the exact TypeScript prop definitions for the available components in 'basic-ui-lib'.\n"
        "Use these definitions to pass correct and complete props:\n"
        + load_component_types()
        + "\n\n"
        + storybook_examples
        + "Import rules — ALL of these must be included at the top of the file:\n"
        "- Always add: import React from 'react'; as the very first line\n"
        "- Import every React hook you use (useState, useEffect, useCallback, etc.) from 'react'\n"
        "- Import every third-party package you use\n"
        "- The following enums and types are exported from 'basic-ui-lib' — import them from there, NEVER define them yourself:\n"
        f"  {_EXPORTED_TYPES}\n"
        "  Example: import { InputSize, HeaderVariant } from 'basic-ui-lib';\n"
        "- All other types must be imported from their correct source package.\n\n"
        + layout_rule
        + "\n"
        "ALWAYS import TebRichHeader, TebCard, TebDataGridEnterprise, TebLayoutGrid from 'basic-ui-lib'.\n"
        "Always name the generated component 'ReportScreen'\n"
        "NEVER place anything above <TebRichHeader />.\n"
        + (
            "TebRichHeader MUST always include ALL of the following props — none are optional:\n"
            "  primaryTitle=\"TEB\"\n"
            "  primaryIcon=\"\"\n"
            "  secondaryIcon=\"\"\n"
            "  onPrimaryAction={() => { console.log('primary action clicked'); }}\n"
            "  onSecondaryAction={() => { console.log('secondary action clicked'); }}\n"
        )
        + (f"TebRichHeader MUST have infoLabel=\"{info_label}\".\n" if info_label else "TebRichHeader MUST have infoLabel=\"\".\n")
        + (f"TebRichHeader MUST have secondaryTitle=\"{secondary_title}\".\n" if secondary_title else "")
        + grid_columns_rule
        + (
            "TebDataGridEnterprise columnDefs: every ColDef MUST have flex: 1 — never use fixed width on columns.\n\n"
            "Additional rules:\n"
            "- Use functional components with TypeScript\n"
            "- Use only inline styles via the style prop (e.g. style={{ color: 'red' }}); do not use any CSS files, CSS Modules, or Tailwind classes\n"
            "- Export the component as default\n"
            "- Only output the raw TSX code, no markdown fences, no explanations\n"
            "- Remove every import that is not actually used in the component\n"
            "- NEVER use generic type parameters directly in JSX tags (e.g. <TebAutoComplete<OptionType> is WRONG). "
            "Always write <TebAutoComplete and handle typing via props or local variable types.\n"
            "- Checkbox label prop only accepts a plain string value (e.g. label='Include Tax'). NEVER pass JSX or a React element to label. The string must be a single line with no line breaks.\n"
            "- NEVER pass children as a JSX prop attribute (children='...' or children={...} is WRONG). "
            "Always use inner text syntax: <Component>text</Component>.\n"
            "- TebInput MUST always have type={InputType.text}. Always import InputType from 'basic-ui-lib'.\n"
            "- TebInput MUST NOT have an assistiveText prop. Never pass assistiveText to TebInput.\n"
            "- The filter area TebCard MUST NOT have a title prop — never pass title to it.\n"
            "- The div directly inside the filter area TebCard MUST have width: '100%' and height: '100%' — it must fill the card completely.\n"
            "- Count how many times each component name appears in the user's prompt. "
            "Add exactly that many instances of that component to the screen. "
            "If a component is mentioned once, add it once. If mentioned twice, add two separate instances. "
            "Do not add more or fewer instances than the count in the prompt.\n"
            "- Apply the following linting and formatting rules strictly:\n"
        )
        + load_lint_rules()
    )
