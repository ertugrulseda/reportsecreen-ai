"""
pytest test suite — javafilesdownload modülü

Çalıştırma (api/ dizininden):
    pytest reportgeneratorapi/javafilesdownload/tests/test_java_files.py -v
"""
import io
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from reportgeneratorapi.javafilesdownload.router import router
from reportgeneratorapi.javafilesdownload.service import generate_java_zip, _validate_path

# ── Test istemcisi ────────────────────────────────────────────────────────────

_app = FastAPI()
_app.include_router(router, prefix="/api/v1")
client = TestClient(_app)
URL = "/api/v1/java-files/download"


# ── Yardımcı ─────────────────────────────────────────────────────────────────

def _read_zip(content: bytes) -> dict[str, str]:
    """ZIP içeriğini {path: içerik} sözlüğüne dönüştürür."""
    result: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for name in zf.namelist():
            result[name] = zf.read(name).decode("utf-8")
    return result


# ── Test 1: Tek Java dosyası ──────────────────────────────────────────────────

def test_single_java_file():
    payload = {
        "java_files": [
            {
                "path": "src/main/java/tr/com/teb/OkulController.java",
                "javaClass": "package tr.com.teb;\npublic class OkulController {}",
            }
        ]
    }
    res = client.post(URL, json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    files = _read_zip(res.content)
    assert "src/main/java/tr/com/teb/OkulController.java" in files


# ── Test 2: Farklı klasörlerde birden fazla dosya ────────────────────────────

def test_multiple_java_files_different_folders():
    payload = {
        "java_files": [
            {
                "path": "src/main/java/tr/com/teb/controller/OkulController.java",
                "javaClass": "package controller;\npublic class OkulController {}",
            },
            {
                "path": "src/main/java/tr/com/teb/service/OkulService.java",
                "javaClass": "package service;\npublic class OkulService {}",
            },
        ]
    }
    res = client.post(URL, json=payload)
    assert res.status_code == 200
    files = _read_zip(res.content)
    assert len(files) == 2
    assert "src/main/java/tr/com/teb/controller/OkulController.java" in files
    assert "src/main/java/tr/com/teb/service/OkulService.java" in files


# ── Test 3: Boş java_files dizisi ────────────────────────────────────────────

def test_empty_java_files():
    res = client.post(URL, json={"java_files": []})
    assert res.status_code == 200
    files = _read_zip(res.content)
    assert len(files) == 0


# ── Test 4: java_files alanının bulunmaması ───────────────────────────────────

def test_missing_java_files_field():
    res = client.post(URL, json={"other_field": "value"})
    assert res.status_code == 422


# ── Test 5: Eksik path veya javaClass alanı ──────────────────────────────────

def test_missing_path_field():
    payload = {"java_files": [{"javaClass": "public class Foo {}"}]}
    res = client.post(URL, json=payload)
    assert res.status_code == 422


def test_missing_java_class_field():
    payload = {"java_files": [{"path": "src/Foo.java"}]}
    res = client.post(URL, json=payload)
    assert res.status_code == 422


# ── Test 6: Aynı path değerine sahip birden fazla dosya ──────────────────────

def test_duplicate_path():
    path = "src/main/java/tr/com/teb/Foo.java"
    payload = {
        "java_files": [
            {"path": path, "javaClass": "public class Foo {}"},
            {"path": path, "javaClass": "public class Foo { /* kopya */ }"},
        ]
    }
    res = client.post(URL, json=payload)
    assert res.status_code == 400
    assert "birden fazla" in res.json()["detail"].lower() or "duplicate" in res.json()["detail"].lower()


# ── Test 7: Türkçe karakter ve çok satırlı Java kodu ─────────────────────────

def test_turkish_characters_and_multiline():
    java_code = (
        "package tr.com.teb;\n\n"
        "/**\n"
        " * Öğrenci ödeme servisi — Türkçe açıklama\n"
        " * Ğ ğ Ü ü Ş ş İ ı Ö ö Ç ç\n"
        " */\n"
        "public class OgrenciOdemeServisi {\n"
        "    private String öğrenciAd = \"İbrahim\";\n"
        "}\n"
    )
    payload = {
        "java_files": [
            {
                "path": "src/main/java/tr/com/teb/OgrenciOdemeServisi.java",
                "javaClass": java_code,
            }
        ]
    }
    res = client.post(URL, json=payload)
    assert res.status_code == 200
    files = _read_zip(res.content)
    content = files["src/main/java/tr/com/teb/OgrenciOdemeServisi.java"]
    assert "Öğrenci" in content
    assert "İbrahim" in content
    assert "Ğ ğ Ü ü Ş ş" in content


# ── Test 8: İç içe java_files işlenmemeli ────────────────────────────────────

def test_nested_java_files_ignored():
    """
    filter_components[].api.java_files gibi iç içe alanlar işlenmemeli;
    yalnızca kök java_files dizi elemanları ZIP'e yazılmalıdır.
    """
    payload = {
        "java_files": [
            {
                "path": "src/main/java/tr/com/teb/TopLevel.java",
                "javaClass": "public class TopLevel {}",
            }
        ],
        "filter_components": [
            {
                "inputType": "select",
                "api": {
                    "java_files": [
                        {
                            "path": "src/main/java/tr/com/teb/Nested.java",
                            "javaClass": "public class Nested {}",
                        }
                    ]
                },
            }
        ],
    }
    res = client.post(URL, json=payload)
    assert res.status_code == 200
    files = _read_zip(res.content)
    assert len(files) == 1
    assert "src/main/java/tr/com/teb/TopLevel.java" in files
    assert "src/main/java/tr/com/teb/Nested.java" not in files


# ── Test 9: Güvenli olmayan dosya yolları ────────────────────────────────────

@pytest.mark.parametrize(
    "bad_path",
    [
        "../etc/passwd.java",
        "../../secret.java",
        "/absolute/path/Foo.java",
        "C:/Windows/Foo.java",
        "src/./hidden/Foo.java",
        "src//double//slash/Foo.java",
        "src/Foo.txt",               # .java uzantısı yok
        "",                          # boş yol
        "src/null\x00byte/Foo.java", # null byte
    ],
)
def test_unsafe_paths_rejected(bad_path: str):
    payload = {
        "java_files": [{"path": bad_path, "javaClass": "public class Foo {}"}]
    }
    res = client.post(URL, json=payload)
    assert res.status_code in (400, 422), (
        f"Beklenen 400/422, alınan {res.status_code} — yol: {bad_path!r}"
    )


# ── Test 10: ZIP içeriği orijinal javaClass ile birebir aynı olmalı ──────────

def test_zip_content_matches_original_java_class():
    java_code = (
        "package tr.com.teb.bff.next.report.controller;\n\n"
        "import java.util.List;\n\n"
        "@RestController\n"
        "public class OkulController {\n\n"
        "    @PostMapping(\"/list\")\n"
        "    public List<String> list() {\n"
        "        return List.of(\"a\", \"b\");\n"
        "    }\n"
        "}\n"
    )
    path = (
        "src/main/java/tr/com/teb/bff/next/report/controller/OkulController.java"
    )
    payload = {"java_files": [{"path": path, "javaClass": java_code}]}

    res = client.post(URL, json=payload)
    assert res.status_code == 200
    files = _read_zip(res.content)
    assert files[path] == java_code
