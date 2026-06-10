"""Parsing et annualisation des salaires.

Deux sources hétérogènes :
  - WTTJ : champs structurés salMin / salMax / salPer / salCur.
  - Indeed : texte libre FR très varié, ex. "De 45 000 € à 50 000 € par an",
    "À partir de 60 000 € par an", "De 492,22 € à 1 823,03 € par mois"
    (espaces insécables, virgule décimale, base mensuelle/journalière).

On ramène tout à une fourchette **annuelle EUR comparable** avec des
hypothèses ETP explicites (mensuel x12, journalier x218 j ouvrés) et une
hygiène qui rejette les valeurs implausibles (parses erronés).
"""

from __future__ import annotations

import re

from cartodata_de.config import (
    ANNUAL_MULT,
    SALARY_MAX_PLAUSIBLE,
    SALARY_MIN_PLAUSIBLE,
    USD_EUR,
)

# Espaces insécables rencontrés dans les montants Indeed
_NBSP = {" ": " ", " ": " ", " ": " "}
_NUM_RE = re.compile(r"\d[\d \.]*(?:,\d+)?")


def _detect_period(text: str) -> str | None:
    t = text.lower()
    if re.search(r"par an|/an|annuel", t):
        return "yearly"
    if re.search(r"par mois|mensuel|/mois", t):
        return "monthly"
    if re.search(r"par jour|/jour|tjm", t):
        return "daily"
    if re.search(r"de l'heure|par heure|/h\b", t):
        return "hourly"
    return None


def parse_salary_fr(text: str | None) -> dict | None:
    """Texte libre FR -> {min, max, period} ou None si non parsable.

    Renvoie None quand la périodicité est absente (on n'annualise jamais
    sans hypothèse explicite de période).
    """
    if not text:
        return None
    t = text
    for bad, good in _NBSP.items():
        t = t.replace(bad, good)
    period = _detect_period(t)
    if not period:
        return None
    nums = []
    for raw in _NUM_RE.findall(t):
        cleaned = raw.replace(" ", "").replace(".", "").replace(",", ".")
        try:
            val = float(cleaned)
        except ValueError:
            continue
        if val >= 100:  # écarte les "35h", codes postaux courts, etc.
            nums.append(val)
    if not nums:
        return None
    return {"min": min(nums), "max": max(nums), "period": period}


def _plausible(v: float | None) -> bool:
    return v is not None and SALARY_MIN_PLAUSIBLE <= v <= SALARY_MAX_PLAUSIBLE


def _num(v) -> float | None:
    """Coerce une valeur source (int/float/str ou None) en float, ou None.

    WTTJ renvoie parfois salMin/salMax en chaîne ("45000", "45 000").
    """
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(" ", "").replace(" ", "").replace(",", "."))
    except (ValueError, TypeError):
        return None


def annualize(
    min_v: float | None,
    max_v: float | None,
    period: str | None,
    currency: str | None,
) -> tuple[int | None, int | None]:
    """Fourchette brute (période/devise) -> fourchette annuelle EUR (arrondie).

    Applique l'hygiène de plausibilité : une borne hors [8k, 300k] est
    considérée comme un parse erroné et mise à NULL (pas masquée : tracée).
    """
    mult = ANNUAL_MULT.get(period or "")
    if not mult:
        return (None, None)
    min_v, max_v = _num(min_v), _num(max_v)
    factor = (USD_EUR if currency == "USD" else 1.0) * mult
    a = round(min_v * factor) if (min_v is not None and min_v > 0) else None
    b = round(max_v * factor) if (max_v is not None and max_v > 0) else None
    if not _plausible(a):
        a = None
    if not _plausible(b):
        b = None
    if a is None and b is None:
        return (None, None)
    return (a if a is not None else b, b if b is not None else a)
