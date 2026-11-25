import io
import re
import zipfile

# Yapılandırılabilir güvenlik limitleri
MAX_FILES: int = 500
MAX_ZIP_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB


def _validate_path(path: str) -> None:
    """
    Dosya yolunu güvenlik ve doğruluk açısından kontrol eder.
    Hatalı durumda ValueError fırlatır.
    """
    if not path or not path.strip():
        raise ValueError("Dosya yolu boş olamaz.")

    if not path.endswith(".java"):
        raise ValueError(
            f"Dosya yolu '.java' uzantısıyla bitmelidir: '{path}'"
        )

    # Null byte kontrolü
    if "\0" in path:
        raise ValueError(f"Dosya yolunda geçersiz karakter (null byte): '{path}'")

    # \ → / normalleştirmesi
    normalized = path.replace("\\", "/")

    # Mutlak yol kontrolü: Unix tarzı /... veya Windows tarzı C:/...
    if normalized.startswith("/") or re.match(r"^[a-zA-Z]:/", normalized):
        raise ValueError(f"Mutlak yollar desteklenmemektedir: '{path}'")

    parts = normalized.split("/")

    # Path traversal kontrolü: .. veya . segment
    if ".." in parts or "." in parts:
        raise ValueError(f"Güvenli olmayan yol segmenti tespit edildi: '{path}'")

    # Boş segment kontrolü (örn: "a//b.java")
    if any(not part for part in parts):
        raise ValueError(f"Geçersiz dosya yolu formatı (boş segment): '{path}'")


def generate_java_zip(json_data: dict) -> io.BytesIO:
    """
    JSON içerisindeki kök java_files dizisini okuyarak 
    klasör hiyerarşisini koruyan ZIP dosyası oluşturur.
    ZIP bellekte oluşturulur; diske yazılmaz.
    """
    java_files: list = json_data.get("java_files", [])

    if len(java_files) > MAX_FILES:
        raise ValueError(
            f"Dosya sayısı sınırını aşıyor: {len(java_files)} > {MAX_FILES}"
        )

    seen_paths: set[str] = set()
    total_size: int = 0
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in java_files:
            path: str = item.get("path", "")
            java_class: str = item.get("javaClass", "")

            _validate_path(path)

            # Çakışan yollara _2, _3, ... suffix'i ekle
            if path in seen_paths:
                stem = path[:-5]  # ".java" kaldır
                counter = 2
                while True:
                    candidate = f"{stem}_{counter}.java"
                    if candidate not in seen_paths:
                        path = candidate
                        break
                    counter += 1
            seen_paths.add(path)

            encoded: bytes = java_class.encode("utf-8")
            total_size += len(encoded)

            if total_size > MAX_ZIP_SIZE_BYTES:
                raise ValueError(
                    f"ZIP boyutu sınırını aşıyor: "
                    f"{MAX_ZIP_SIZE_BYTES // (1024 * 1024)} MB"
                )

            zf.writestr(path, encoded)

    buffer.seek(0)
    return buffer
