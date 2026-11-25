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
