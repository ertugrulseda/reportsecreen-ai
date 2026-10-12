from typing import Any
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str
    layout: str = "vertical"      # "vertical" | "horizontal"
    secondary_title: str = ""     # TebRichHeader secondaryTitle
    info_label: str = ""          # TebRichHeader infoLabel
    component_names: str = ""     # virgülle ayrılmış isimler, prompt sırasıyla eşleşir
    grid_columns: str = ""        # virgülle ayrılmış kolon başlıkları


class GenerateResponse(BaseModel):
    generated_code: str
    output_file: str
    logs: list[str]
    error: str


class TransformRequest(BaseModel):
    model_config = {"extra": "allow"}

    filter_components: list[dict[str, Any]]


class TransformResponse(BaseModel):
    model_config = {"extra": "allow"}

    filter_components: list[dict[str, Any]]
