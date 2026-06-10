"""Normalisation des libellés hétérogènes (télétravail, contrat)."""

from __future__ import annotations

REMOTE = {
    "full": "Total",
    "fulltime": "Total",
    "total": "Total",
    "partial": "Partiel",
    "punctual": "Ponctuel",
    "none": "Non",
    "no": "Non",
    "unknown": "Non précisé",
    "": "Non précisé",
}


def normalize_remote(value: str | None) -> str | None:
    if value is None:
        return None
    key = str(value).lower()
    if key in REMOTE:
        return REMOTE[key]
    return str(value) if value else None


def infer_contract_indeed(job_types: list[str] | None) -> str:
    """Indeed n'expose pas le type de contrat de façon fiable.

    Seul "stage" est détectable dans jobTypes ; sinon 'Non précisé'
    (on n'invente pas un CDI qui n'est pas dans la donnée).
    """
    joined = "|".join(job_types or []).lower()
    if "stage" in joined:
        return "Stage"
    return "Non précisé"
