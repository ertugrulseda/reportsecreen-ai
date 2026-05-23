import operator
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    prompt: str
    layout: str                     # "vertical" | "horizontal"
    error: str
    generated_code: str
    output_file: str
    logs: Annotated[list[str], operator.add]
    matched_components: list[str]   # component_checker → ui_writer arası
