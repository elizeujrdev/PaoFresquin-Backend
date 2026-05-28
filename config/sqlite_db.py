"""SQLite path for local dev vs serverless (Vercel/Lambda).

On serverless, only /tmp is writable. The bundled db.sqlite3 in the deploy
package is read-only, so we copy it to /tmp on cold start.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

TMP_DB_NAME = "paofresquim.sqlite3"


def is_serverless() -> bool:
    return bool(
        os.environ.get("VERCEL")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        or os.environ.get("AWS_EXECUTION_ENV")
        or os.environ.get("SQLITE_USE_TMP", "").lower() in ("1", "true", "yes")
    )


def resolve_sqlite_path(base_dir: Path) -> str:
    override = os.environ.get("SQLITE_PATH")
    if override:
        return override

    bundled = base_dir / "db.sqlite3"

    if not is_serverless():
        return str(bundled)

    tmp_dir = Path(os.environ.get("SQLITE_TMP_DIR", "/tmp"))
    tmp_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_dir / TMP_DB_NAME

    if not db_path.exists():
        if bundled.is_file():
            shutil.copy2(bundled, db_path)
            for suffix in ("-wal", "-shm"):
                extra = Path(f"{bundled}{suffix}")
                if extra.is_file():
                    shutil.copy2(extra, Path(f"{db_path}{suffix}"))
        else:
            db_path.touch()

    return str(db_path)


def resolve_media_root(base_dir: Path) -> Path:
    override = os.environ.get("MEDIA_ROOT")
    if override:
        return Path(override)

    if is_serverless():
        media = Path(os.environ.get("SQLITE_TMP_DIR", "/tmp")) / "paofresquim-media"
        media.mkdir(parents=True, exist_ok=True)
        return media

    return base_dir / "media"
