import operator
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    prompt: str
    layout: str                     # "vertical" | "horizontal"
    secondary_title: str            # TebRichHeader secondaryTitle
    info_label: str                 # TebRichHeader infoLabel
    error: str
    generated_code: str
    output_file: str
    logs: Annotated[list[str], operator.add]
    matched_components: list[str]   # component_checker → name_matcher arası
    component_names: str            # virgülle ayrılmış isimler, prompt sırasıyla eşleşir
    component_props: list[dict]     # [{component, props: {key: value}}] — name_matcher → ui_writer arası
