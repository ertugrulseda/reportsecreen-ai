from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from reportgeneratorapi.javafilesdownload.models import JavaFilesRequest
from reportgeneratorapi.javafilesdownload.service import generate_java_zip

router = APIRouter()


@router.post(
    "/java-files/download",
    summary="Java dosyalarını ZIP olarak indir",
    response_description="ZIP arşivi",
    responses={
        200: {"content": {"application/zip": {}}},
        400: {"description": "Geçersiz istek (yinelenen yol, güvensiz yol vb.)"},
        422: {"description": "Eksik veya hatalı alan"},
        500: {"description": "Beklenmeyen sunucu hatası"},
    },
)
async def download_java_files(request: JavaFilesRequest):
    """
   JSON içerisindeki `java_files` dizisini ZIP dosyasına dönüştürür ve
    HTTP response üzerinden indirir.

    Sadece kök seviyesindeki `java_files` altındaki dosyalar  işlenir;
    tek ZIP arşivine eklenir. 

    ---
    ### Örnek request
    ```json
    {
      "java_files": [
        {
          "path": "src/main/java/tr/com/teb/bff/next/report/controller/OkulController.java",
          "javaClass": "package tr.com.teb.bff.next.report.controller;\\n\\npublic class OkulController {}"
        },
        {
          "path": "src/main/java/tr/com/teb/bff/next/report/service/OkulService.java",
          "javaClass": "package tr.com.teb.bff.next.report.service;\\n\\npublic class OkulService {}"
        }
      ]
    }
    ```

    ZIP içeriği `path` değerlerine göre klasör yapısını korur:
    ```
    src/main/java/tr/com/teb/bff/next/report/
    ├── controller/OkulController.java
    └── service/OkulService.java
    ```
    """
    try:
        zip_buffer = generate_java_zip(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {exc}")

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="generated-java-files.zip"'
        },
    )
