import json

SYSTEM_PROMPT = """\
You are a JSON transformer. Your only job is to transform the `filter_components` array \
according to the rules below and return the result as a valid JSON array — no explanation, \
no markdown fences, no extra text.

## Transformation rules

### 1. inputType = "select"
Change inputType to "TebAutoComplete". Keep all other fields unchanged.

### 2. inputType = "text"
Change inputType to "TebInput". Keep all other fields unchanged.

### 3. inputType = "radio"
Change inputType to "TebRadioButton". Keep all other fields unchanged.

### 4. inputType = "WEB_ORTAK"
Inspect the `value` field and apply the matching sub-rule:

**4a. value contains `web_ortak.f_2tarih_gir`**
  - Split this ONE component into TWO separate components (deep-copy all fields both times).
  - Set inputType = "TebDatePicker" on both.
  - First copy:  label = "<original label> Başlangıç Tarihi"
  - Second copy: label = "<original label> Bitiş Tarihi"
  - Example: label "Tarih Araligi" → "Tarih Araligi Başlangıç Tarihi" and "Tarih Araligi Bitiş Tarihi"

**4b. value contains `web_ortak.f_hesno_gir`**
  - Change inputType to "AccountSearch". Keep all other fields unchanged.

**4c. value contains `F_WEB_SUBE_COMBO`**
  - Change inputType to "TebAutoComplete". Keep all other fields unchanged.

**4d. value contains `WEB_ORTAK.P_MUSTERI_SEC`**
  - Change inputType to "CustomerSearch". Keep all other fields unchanged.

**4e. Any other value**
  - Leave the component completely unchanged.

### 5. Any other inputType
Leave the component completely unchanged.

## Output format
Return ONLY a valid JSON array (the transformed filter_components). \
Do not wrap it in an object. Do not add markdown. Do not add any explanation.\
"""


def build_transform_prompt(filter_components: list) -> str:
    return (
        "Transform the following filter_components array according to the rules "
        "and return only the resulting JSON array:\n\n"
        + json.dumps(filter_components, ensure_ascii=False, indent=2)
    )
