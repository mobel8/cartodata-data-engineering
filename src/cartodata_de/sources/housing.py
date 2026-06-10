"""Connecteur BRONZE additionnel — Logement/Énergie IDF (BACKLOG, stub assumé).

Greffe territoriale (DVF + DPE + BAN + RTE/Enedis) qui démontre que
l'architecture est GÉNÉRIQUE (multi-domaine) et alimentera le module ML
"riche" / Vision du portfolio. Volontairement non implémenté ici : on ne
construit pas le domaine énergie tant que le cœur emploi n'est pas stable
(garde-fou anti-scope-creep, cf. ENGINEERING_NOTES).
"""

from __future__ import annotations

# Sources cibles (toutes open data, gratuites).
SUPPORTED = ["dvf", "dpe", "ban", "rte", "enedis"]

STATUS = "stub/backlog"


def ingest_housing_bronze(run_date: str, sources: list[str] | None = None) -> dict:
    """Point d'entrée prévu pour la greffe territoire. Non implémenté (backlog)."""
    return {
        "status": STATUS,
        "run_date": run_date,
        "sources_cibles": sources or SUPPORTED,
        "note": "Connecteur territoire prévu — matérialisable quand le cœur emploi est figé.",
    }
