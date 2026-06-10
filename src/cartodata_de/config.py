"""Configuration centrale : chemins du lakehouse, constantes, résolution des sources.

RUN_DATE est injecté par l'environnement (et non lu via une horloge implicite)
pour que chaque exécution soit **reproductible** : rejouer le pipeline avec le
même RUN_DATE sur le même bronze redonne exactement le même gold (idempotence).
"""

from __future__ import annotations

import os
from pathlib import Path

# Racine du projet (…/01-data-engineering)
ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
BRONZE = DATA / "bronze"
SILVER = DATA / "silver"
GOLD = DATA / "gold"
WAREHOUSE = ROOT / "warehouse"
DBT_DIR = ROOT / "dbt"
FIXTURES = ROOT / "tests" / "fixtures"

DUCKDB_PATH = WAREHOUSE / "observatoire.duckdb"
SILVER_OFFERS = SILVER / "offres.parquet"
SILVER_REJECTS = SILVER / "rejets_salaire.parquet"

# Date de run logique (idempotence). Override : $env:RUN_DATE = "2026-06-10"
RUN_DATE = os.environ.get("RUN_DATE", "2026-06-10")

# Taux de change figé et documenté (pas d'appel réseau dans le pipeline).
USD_EUR = float(os.environ.get("USD_EUR", "0.92"))

# Hypothèses d'annualisation ETP (documentées dans ENGINEERING_NOTES.md)
ANNUAL_MULT = {"yearly": 1, "monthly": 12, "daily": 218, "hourly": 1820}

# Garde-fou : on rejette les salaires annualisés implausibles (parses erronés / TJM mal annualisés)
SALARY_MIN_PLAUSIBLE = 8_000
SALARY_MAX_PLAUSIBLE = 300_000

# Seuil du fuzzy-match cross-source (tel quel dans le matcher d'origine cross-site-match.mjs)
JACCARD_TITLE_MIN = 0.6
JACCARD_TITLE_MIN_NO_LOCATION = 0.85


def _first_existing(*candidates: Path) -> Path | None:
    for c in candidates:
        if c and c.exists():
            return c
    return None


def resolve_source(env_var: str, *fallbacks: Path) -> Path | None:
    """Résout le chemin d'une source : variable d'env prioritaire, puis repli.

    Permet trois modes :
      1. $env:WTTJ_SRC = "...\\catinfo2.json"  (run complet local)
      2. emplacement réel sibling du dépôt scraping (machine d'origine)
      3. échantillon commité tests/fixtures/ (clone public, CI) — toujours présent
    """
    env_path = os.environ.get(env_var)
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
    return _first_existing(*fallbacks)


# Emplacements réels sur la machine d'origine (siblings du dépôt de scraping).
# Absents d'un clone public -> on retombe sur l'échantillon tests/fixtures/.
_CANDIDATURES = ROOT.parents[2] if len(ROOT.parents) >= 3 else ROOT

WTTJ_SOURCE = resolve_source(
    "WTTJ_SRC",
    _CANDIDATURES / "Welcome-to-the-Jungle" / "data" / "catinfo2.json",
    FIXTURES / "sample_wttj.json",
)
INDEED_SOURCE = resolve_source(
    "INDEED_SRC",
    _CANDIDATURES / "Indeed" / "data" / "indeed-catinfo.json",
    FIXTURES / "sample_indeed.json",
)
CROSS_SITE_SOURCE = resolve_source(
    "CROSS_SRC",
    _CANDIDATURES / "_cross-site" / "cross-site.json",
    FIXTURES / "sample_cross_site.json",
)


def ensure_dirs() -> None:
    for d in (BRONZE, SILVER, GOLD, WAREHOUSE):
        d.mkdir(parents=True, exist_ok=True)
