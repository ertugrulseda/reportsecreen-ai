from pydantic import BaseModel


class JavaFile(BaseModel):
    path: str
    javaClass: str


class JavaFilesRequest(BaseModel):
    java_files: list[JavaFile] = []

    model_config = {"extra": "ignore"}
