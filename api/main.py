import json
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path
from reportgeneratorapi.router import router as reportgeneratorapi_router
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

ALLOWED_ORIGIN_PATTERN = re.compile(r"^https?://([a-zA-Z0-9\-]+\.)*int\.teb\.com\.tr(:\d+)?$|^http://localhost:\d+$")
app = FastAPI(title="Teb Ui Accelerator", version="1.0.0", docs_url=None, openapi_url=None)
app.mount("/swagger-ui-static", StaticFiles(directory=swagger_ui_path), name="swagger-ui-static")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="Teb Ui Accelerator",
        version="1.0.0",
        openapi_version="3.0.0",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json():
    from fastapi.responses import JSONResponse
    return JSONResponse(app.openapi())


@app.get("/docs", include_in_schema=False)
async def swagger_ui_page():
    schema = app.openapi()
    schema_json = json.dumps(schema)
    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Teb Ui Accelerator</title>
  <meta charset="utf-8"/>
  <link rel="stylesheet" type="text/css" href="/swagger-ui-static/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="/swagger-ui-static/swagger-ui-bundle.js"></script>
<script>
  SwaggerUIBundle({{
    spec: {schema_json},
    dom_id: '#swagger-ui',
    presets: [SwaggerUIBundle.presets.apis],
    layout: "BaseLayout",
    requestInterceptor: function(request) {{
      if (request.body && typeof request.body === 'string') {{
        try {{
          JSON.parse(request.body);
        }} catch(e) {{
          var match = request.body.match(/^\\s*(\\{{[\\s\\S]*?\\}})\\s*/);
          if (match) {{ request.body = match[1]; }}
        }}
      }}
      return request;
    }}
  }})
</script>
</body>
</html>"""
    return HTMLResponse(html)

class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        allowed = bool(ALLOWED_ORIGIN_PATTERN.match(origin))

        if request.method == "OPTIONS":
            response = Response(status_code=204)
        else:
            response = await call_next(request)

        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"

        return response 


app.add_middleware(DynamicCORSMiddleware)

app.include_router(reportgeneratorapi_router,prefix="/reportgeneratorapi",tags=["Report Generator"])
