from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# ── Response ─────────────────────────────────────────────────────────────────

class SelectOption(BaseModel):
    value: str
    label: str
    cursor: Optional[str] = None


class QueryApiResponseField(BaseModel):
    name: str
    type: str
    description: str


class QueryApiResponseExample(BaseModel):
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class QueryApi(BaseModel):
    name: str
    url: str
    method: str
    description: str
    query_params: List[Any]
    path_params: List[Any]
    request_body: Optional[Dict[str, Any]] = None
    response_fields: List[QueryApiResponseField]
    response_example: Optional[QueryApiResponseExample] = None
    source_cursor: Optional[str] = None
    input_parameters: Optional[List[Any]] = None
    extra_options: Optional[List[SelectOption]] = None


class JavaFile(BaseModel):
    path: str
    javaClass: str


class FilterComponentApi(BaseModel):
    java_files: List[JavaFile]
    controller_source: Optional[str] = None
    query_api: QueryApi


class FilterComponent(BaseModel):
    startLineNumber: int
    label: str
    inputType: str
    name: Optional[str] = None
    value: Optional[str] = None
    className: Optional[str] = None
    options: Optional[List[SelectOption]] = None
    api: Optional[FilterComponentApi] = None


class AnalyzeReportResponse(BaseModel):
    report_g_raw_content: str
    report_s_raw_content: str
    report_title: str
    filter_components: List[FilterComponent]
    java_files: List[JavaFile]
    query_api: QueryApi
    error: Optional[str] = None
    result: Dict[str, Any] = {}
