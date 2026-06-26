"""
log_db.py — Pipeline sonuçlarını PostgreSQL'e kaydeden LangGraph agent'ı.

Bağımlılık : psycopg[binary] (psycopg3)
Ortam değ. : DATABASE_URL  (örn. postgresql://user:pass@host:5432/dbname)

Not: Windows'ta ProactorEventLoop kullanıldığından psycopg async API
     desteklenmiyor. Sync bağlantı asyncio.to_thread ile thread'de çalıştırılır.
"""

import os
import asyncio
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from state import State

load_dotenv()

_DSN: str = os.getenv("DATABASE_URL", "")

# ── DDL ───────────────────────────────────────────────────────────────────────
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS generations (
    id                  SERIAL        PRIMARY KEY,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    prompt              TEXT          NOT NULL,
    layout              VARCHAR(16)   NOT NULL,
    output_file         TEXT,
    line_count          INTEGER,
    status              VARCHAR(8)    NOT NULL CHECK (status IN ('ok','error')),
    error_message       TEXT,
    matched_components  TEXT[],
    logs                TEXT[]
);
"""

_INSERT = """
INSERT INTO generations
    (prompt, layout, output_file, line_count, status, error_message,
     matched_components, logs)
VALUES
    (%(prompt)s, %(layout)s, %(output_file)s, %(line_count)s, %(status)s,
     %(error_message)s, %(matched_components)s, %(logs)s)
RETURNING id;
"""


# ── Sync DB işlemi (thread'de çalışır) ───────────────────────────────────────
def _write_to_db(row: dict) -> int | None:
    with psycopg.connect(_DSN, row_factory=dict_row) as conn:
        conn.execute(_CREATE_TABLE)
        result = conn.execute(_INSERT, row)
        record = result.fetchone()
        conn.commit()
        return record["id"] if record else None


# ── db_logger ─────────────────────────────────────────────────────────────────────
async def db_logger(state: State) -> dict:
    """
    LangGraph agent'ı.

    logger node'u logları state'e yazdıktan sonra bu agent devreye girer;
    tüm pipeline çıktısını (prompt, layout, kod, loglar, durum) PostgreSQL
    generations tablosuna kaydeder.

    Hata oluşursa pipeline'ı kesmez, yalnızca konsola yazar.
    """
    if not _DSN:
        print("[db_logger] DATABASE_URL tanımlı değil, atlanıyor.")
        return {}

    print("[db_logger] Veritabanına kaydediliyor...")

    error       = state.get("error", "")
    output_file = state.get("output_file", "")
    code        = state.get("generated_code", "")
    line_count  = len(code.splitlines()) if code else None
    filename    = os.path.basename(output_file) if output_file else None

    row = {
        "prompt":             state.get("prompt", ""),
        "layout":             state.get("layout", "vertical"),
        "output_file":        filename,
        "line_count":         line_count,
        "status":             "error" if error else "ok",
        "error_message":      error or None,
        "matched_components": state.get("matched_components") or [],
        "logs":               state.get("logs") or [],
    }

    try:
        inserted_id = await asyncio.to_thread(_write_to_db, row)
        print(f"[db_logger] Kayit eklendi - generations.id = {inserted_id}")
    except Exception as exc:
        print(f"[db_logger] DB yazma hatası: {exc}")

    return {}
