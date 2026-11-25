from fastapi import APIRouter, Form
from webreportanalyze.schemas import (
    AnalyzeReportResponse,
    FilterComponent,
    FilterComponentApi,
    JavaFile,
    QueryApi,
    QueryApiResponseExample,
    QueryApiResponseField,
    SelectOption,
)

router = APIRouter()


@router.post(
    "/analyze/analyze-report",
    response_model=AnalyzeReportResponse,
    summary="Analyze Report",
    description=(
        "G ve S prosedür kaynak kodlarını analiz ederek filtre bileşenlerini, "
        "Java dosyalarını ve sorgu API tanımını döner. "
        "SQL içindeki özel karakterler (çift tırnak, satır sonu) nedeniyle "
        "giriş alanları **form-data** olarak gönderilir."
    ),
)
async def analyze_report(
    G: str = Form(..., description="G (Giriş ekranı) prosedür kaynak kodu"),
    S: str = Form(..., description="S (Sonuç ekranı) prosedür kaynak kodu"),
) -> AnalyzeReportResponse:
    g_raw = G
    s_raw = S

    # ── Fake filter components ────────────────────────────────────────────────
    filter_components: list[FilterComponent] = [
        FilterComponent(
            startLineNumber=14,
            label="Kurum",
            inputType="select",
            name="pkurum",
            value="",
            className="acik",
            options=[
                SelectOption(value="0", label="Hepsi"),
                SelectOption(
                    value="rec_okul.fatkurumno",
                    label="rec_okul.ad",
                    cursor="cur_okul",
                ),
            ],
            api=FilterComponentApi(
                java_files=[
                    JavaFile(
                        path="src/main/java/tr/com/teb/bff/next/report/controller/OkulController.java",
                        javaClass=(
                            "package tr.com.teb.bff.next.report.controller;\n\n"
                            "@RestController\n@RequestMapping(\"/api/v1/schools\")\n"
                            "public class OkulController {\n    // stub\n}"
                        ),
                    ),
                    JavaFile(
                        path="src/main/java/tr/com/teb/bff/next/report/service/OkulService.java",
                        javaClass=(
                            "package tr.com.teb.bff.next.report.service;\n\n"
                            "@Service\npublic class OkulService {\n    // stub\n}"
                        ),
                    ),
                    JavaFile(
                        path="src/main/java/tr/com/teb/bff/next/report/response/OkulDTO.java",
                        javaClass=(
                            "package tr.com.teb.bff.next.report.response;\n\n"
                            "public record OkulDTO(String fatkurumno, String ad) {}"
                        ),
                    ),
                ],
                controller_source=None,
                query_api=QueryApi(
                    name="School Institution List",
                    url="/api/v1/schools/list",
                    method="POST",
                    description="Fetch list of school institutions for payment control dropdown",
                    query_params=[],
                    path_params=[],
                    request_body={
                        "type": "Map<String, Object>",
                        "description": "Parsed JSON request body",
                    },
                    response_fields=[
                        QueryApiResponseField(
                            name="fatkurumno", type="String", description="Institution number"
                        ),
                        QueryApiResponseField(
                            name="ad",
                            type="String",
                            description="Institution name with institution number appended",
                        ),
                    ],
                    response_example=QueryApiResponseExample(
                        data=[
                            {"fatkurumno": "0", "ad": "Hepsi"},
                            {"fatkurumno": "1001", "ad": "Ankara Koleji (Kurumno:1001)"},
                        ],
                        metadata={"totalCount": 2},
                    ),
                    source_cursor=(
                        "CURSOR cur_okul IS\n"
                        "SELECT f.fatkurumno, (f.ad || ' (Kurumno:'|| f.fatkurumno || ')') ad\n"
                        "FROM fat_kurum f, referans r\n"
                        "WHERE f.fatkurumno=r.krt1\n"
                        "AND r.tblad='OKUL_KRM_BILGI'\n"
                        "AND f.drm='G' order BY 2;"
                    ),
                    input_parameters=[],
                    extra_options=[SelectOption(value="0", label="Hepsi")],
                ),
            ),
        ),
        FilterComponent(
            startLineNumber=22,
            label="Ögrenci No",
            inputType="text",
            name="iogrencino",
            value="",
            className="",
        ),
        FilterComponent(
            startLineNumber=24,
            label="T.C.Kimlik No",
            inputType="text",
            name="iTCKN",
            value="",
            className="",
        ),
        FilterComponent(
            startLineNumber=26,
            label="Tarih Araligi",
            inputType="WEB_ORTAK",
            name="",
            value="web_ortak.f_2tarih_gir('Tarih Araligi:',To_Char(TRUNC(sysdate,'YY'),'DDMMRR'))",
        ),
        FilterComponent(
            startLineNumber=28,
            label="TEB Kayit No",
            inputType="text",
            name="iokulodemeplanno",
            value="",
            className="",
        ),
        FilterComponent(
            startLineNumber=33,
            label="Plan Durumu",
            inputType="select",
            name="pdrm",
            value="",
            className="acik",
            options=[
                SelectOption(value="0", label="Hepsi"),
                SelectOption(value="1", label="Geçerli"),
                SelectOption(value="9", label="Iptal"),
            ],
        ),
    ]

    # ── Fake Java files ───────────────────────────────────────────────────────
    java_files: list[JavaFile] = [
        JavaFile(
            path="src/main/java/tr/com/teb/bff/next/report/request/WpRpCrOkulOdemeKontrolSRequestDTO.java",
            javaClass=(
                "package tr.com.teb.bff.next.report.request;\n\n"
                "public record WpRpCrOkulOdemeKontrolSRequestDTO(\n"
                "        Integer pkurum,\n"
                "        String iogrencino,\n"
                "        String iTCKN,\n"
                "        String dbastar,\n"
                "        String dbittar,\n"
                "        Integer iokulodemeplanno,\n"
                "        Integer pdrm\n"
                ") {}"
            ),
        ),
        JavaFile(
            path="src/main/java/tr/com/teb/bff/next/report/response/OkulOdemePlanDTO.java",
            javaClass=(
                "package tr.com.teb.bff.next.report.response;\n\n"
                "import java.math.BigDecimal;\nimport java.time.LocalDate;\n\n"
                "public record OkulOdemePlanDTO(\n"
                "        Integer okulodemeplanno,\n"
                "        Integer fatkurumno,\n"
                "        String ogrencino,\n"
                "        String borcno,\n"
                "        String borcack,\n"
                "        String tckn,\n"
                "        String adsoyad,\n"
                "        String fakulte,\n"
                "        String bolum,\n"
                "        Integer drm,\n"
                "        String odemetipi,\n"
                "        String durum,\n"
                "        String odemesekli,\n"
                "        BigDecimal toplamtutar,\n"
                "        BigDecimal pesinatTut,\n"
                "        Integer fatodemeno,\n"
                "        Integer taksitsayisi,\n"
                "        String kmhDrm,\n"
                "        BigDecimal kmhLimit,\n"
                "        LocalDate planBldTar,\n"
                "        LocalDate tarih,\n"
                "        Integer sube,\n"
                "        Integer hesno,\n"
                "        LocalDate ilktaksittar,\n"
                "        String hataAck\n"
                ") {}"
            ),
        ),
        JavaFile(
            path="src/main/java/tr/com/teb/bff/next/report/controller/WpRpCrOkulOdemeKontrolSController.java",
            javaClass=(
                "package tr.com.teb.bff.next.report.controller;\n\n"
                "@RestController\n@RequestMapping(\"/api/reports\")\n"
                "public class WpRpCrOkulOdemeKontrolSController {\n    // stub\n}"
            ),
        ),
    ]

    # ── Fake query API ────────────────────────────────────────────────────────
    query_api = QueryApi(
        name="Get Okul Odeme Kontrol",
        url="/api/reports/okul-odeme-kontrol",
        method="POST",
        description="POST /api/reports/okul-odeme-kontrol — Okul odeme kontrol listesi",
        query_params=[],
        path_params=[],
        request_body={
            "type": "Object",
            "source_type": "WpRpCrOkulOdemeKontrolSRequestDTO",
        },
        response_fields=[
            QueryApiResponseField(name="title", type="String", description=""),
            QueryApiResponseField(name="headers", type="Array", description=""),
            QueryApiResponseField(name="rows", type="Array", description=""),
        ],
        response_example=QueryApiResponseExample(
            data=[{"title": "", "headers": [], "rows": []}],
            metadata={"totalCount": 1},
        ),
        source_cursor=None,
    )

    return AnalyzeReportResponse(
        report_g_raw_content=g_raw,
        report_s_raw_content=s_raw,
        report_title="Okul Tahsilatlari Gözlem",
        filter_components=filter_components,
        java_files=java_files,
        query_api=query_api,
        error=None,
        result={},
    )
