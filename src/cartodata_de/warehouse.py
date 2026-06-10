"""Accès lecture au warehouse DuckDB (couche GOLD matérialisée par dbt)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from cartodata_de import config


def connect(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    path = str(config.DUCKDB_PATH)
    if read_only and not Path(path).exists():
        raise FileNotFoundError(
            f"Warehouse absent : {path}. Lancez d'abord le pipeline (dbt build)."
        )
    return duckdb.connect(path, read_only=read_only)


def query(sql: str, params: list[Any] | None = None) -> list[dict]:
    con = connect(read_only=True)
    try:
        rel = con.execute(sql, params or [])
        cols = [d[0] for d in rel.description]
        return [dict(zip(cols, row, strict=True)) for row in rel.fetchall()]
    finally:
        con.close()


def list_marts() -> list[str]:
    rows = query(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_name LIKE 'mart_%' ORDER BY table_name"
    )
    return [r["table_name"] for r in rows]
