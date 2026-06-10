"""Schéma cible unifié (couche SILVER) validé par pydantic à l'ingestion.

Réconcilie deux schémas sources incompatibles (WTTJ structuré, Indeed texte
libre) en un contrat unique. La validation lève tôt sur un enregistrement
incohérent plutôt que de laisser passer une donnée sale en aval.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Source = Literal["WTTJ", "Indeed"]

# Champs où une chaîne vide source ("") signifie "absent" -> normalisé en NULL,
# pour que la complétude reflète les VRAIS trous (et non des "" comptés à tort).
_OPTIONAL_STR_FIELDS = (
    "title", "url", "apply_url", "company", "city", "profession", "kw",
    "experience", "education", "sal_source_period", "posted_date",
)


class OfferSilver(BaseModel):
    """Une offre conformée, prête pour le gold."""

    offer_id: str
    source: Source
    url: str | None = None
    apply_url: str | None = None
    title: str | None = None
    company: str | None = None
    city: str | None = None
    departement: str
    is_idf: bool = False

    profession: str | None = None
    kw: str | None = None
    contract: str = "Non précisé"
    experience: str | None = None
    education: str | None = None
    remote: str | None = None

    sal_min_eur: int | None = None
    sal_max_eur: int | None = None
    sal_source_period: str | None = None
    has_salary: bool = False

    posted_date: str | None = None
    date_is_precise: bool = False
    status: int | None = None
    is_twin: bool = False

    skills: list[str] = Field(default_factory=list)

    run_date: str
    ingested_at: str

    @field_validator(*_OPTIONAL_STR_FIELDS, mode="before")
    @classmethod
    def _empty_to_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @model_validator(mode="after")
    def _check_salary_coherence(self) -> OfferSilver:
        lo, hi = self.sal_min_eur, self.sal_max_eur
        if lo is not None and hi is not None and lo > hi:
            # On répare l'inversion plutôt que de rejeter (min<=max garanti en aval).
            self.sal_min_eur, self.sal_max_eur = hi, lo
        self.has_salary = self.sal_min_eur is not None
        return self
