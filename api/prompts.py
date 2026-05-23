from utils import load_component_types, load_lint_rules, load_storybook_examples, load_exported_types

# Sunucu ayağa kalkarken bir kez okunur
_EXPORTED_TYPES: str = load_exported_types()
print(f"[prompts] Exported types loaded: {_EXPORTED_TYPES}")


_VERTICAL_LAYOUT = (
    "MANDATORY LAYOUT — VERTICAL MODE:\n"
    "The returned JSX MUST follow this exact structure, no exceptions:\n"
    "<TebLayoutGrid container spacing='4px' columns={24}>\n"
    "  <TebLayoutGrid child columns={24}>\n"
    "    <TebRichHeader />                           {/* 1. Always first, full width */}\n"
    "  </TebLayoutGrid>\n"
    "  <TebLayoutGrid child lg={6} md={6} sm={6} style={{ margin: '4px' }}>\n"
    "    <TebCard>                                   {/* 2. Left — filter area */}\n"
    "<div style={{ display: 'flex', flexDirection: 'column', gap: '16px' marginTop:'8px' }}>\n"
    "      {{ ...filter components from prompt... }}\n"
    "</div>\n"
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
    "    <TebRichHeader />                           {/* 1. Always first, full width */}\n"
    "  </TebLayoutGrid>\n"
    "  <TebLayoutGrid child columns={24} lg={24} md={24} sm={24} style={{ margin: '4px'}}>\n"
    "    <TebCard width='full' disableHorizontalScroll={true} disableVerticalScroll={true}\n"
    "             height='fit-content'>                          {/* 2. Filter area — no scroll, height fits content */}\n"
    "      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-start', gap: '8px'}}>\n"
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


async def build_ui_writer_prompt(lib_hint: str, matched_components: list[str], layout: str = "vertical") -> str:
    storybook_examples = await load_storybook_examples(matched_components)
    layout_rule = _VERTICAL_LAYOUT if layout.lower() == "vertical" else _HORIZONTAL_LAYOUT

    return (
        "You are an expert React/TypeScript UI developer.\n"
        "Generate a clean, well-structured React TSX component based on the user's description.\n\n"
        + lib_hint
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
        "NEVER place anything above <TebRichHeader />.\n"
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
        "- TebInput MUST always have type={InputType.text}. Always import InputType from 'basic-ui-lib'.\n"
        "- TebInput MUST NOT have an assistiveText prop. Never pass assistiveText to TebInput.\n"
        "- Count how many times each component name appears in the user's prompt. "
        "Add exactly that many instances of that component to the screen. "
        "If a component is mentioned once, add it once. If mentioned twice, add two separate instances. "
        "Do not add more or fewer instances than the count in the prompt.\n"
        "- Apply the following linting and formatting rules strictly:\n"
        + load_lint_rules()
    )
