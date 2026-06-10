"""Couche BRONZE : copie immuable et horodatée des sources brutes.

On ne transforme RIEN ici : on archive l'octet brut sous
`data/bronze/<source>/dt=<RUN_DATE>/data.json` (append-only). Garder
l'historique permet de mesurer la tension du marché dans le temps et de
rejouer n'importe quel run passé (reproductibilité).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from cartodata_de import config


def _ingest_one(src: Path | None, name: str, run_date: str) -> dict:
    dest_dir = config.BRONZE / name / f"dt={run_date}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "data.json"
    if src and Path(src).exists():
        # Immuable : on n'écrase pas un partitionnement déjà ingéré.
        if not dest.exists():
            shutil.copyfile(src, dest)
        return {"source": name, "path": str(dest), "origin": str(src), "present": True}
    return {"source": name, "path": str(dest), "origin": str(src), "present": False}


def ingest(run_date: str) -> dict:
    config.ensure_dirs()
    manifest = {
        "run_date": run_date,
        "sources": [
            _ingest_one(config.WTTJ_SOURCE, "wttj", run_date),
            _ingest_one(config.INDEED_SOURCE, "indeed", run_date),
            _ingest_one(config.CROSS_SITE_SOURCE, "cross_site", run_date),
        ],
    }
    (config.BRONZE / "_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest


def bronze_path(name: str, run_date: str) -> Path:
    return config.BRONZE / name / f"dt={run_date}" / "data.json"


def load_raw(path: Path) -> list[dict]:
    """Charge un JSON bronze en liste plate.

    Indeed est un objet-wrapper à clés de hash (et non un tableau racine) :
    on déballe via les valeurs. WTTJ est déjà un tableau.
    """
    if not Path(path).exists():
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return list(data.values())
    return []
