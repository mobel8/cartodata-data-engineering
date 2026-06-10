"""Normalisation des dates.

  - WTTJ : date absolue ISO (fiable) -> alimente dim_date.
  - Indeed : date 100% RELATIVE ("il y a 30+ jours", "il y a 3 jours",
    "Publié à l'instant"). Le "30+" est un PLAFOND : on le convertit en date
    approximative mais on ne le présente jamais comme un axe temporel fiable.

`date_is_precise` distingue les deux : seules les dates WTTJ précises servent
de série temporelle dans le gold.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
_JOURS_RE = re.compile(r"il y a (\d+)\+?\s*jour", re.IGNORECASE)
_HEURES_RE = re.compile(r"il y a (\d+)\+?\s*heure", re.IGNORECASE)
_RECENT_RE = re.compile(r"instant|aujourd'hui|moins de|24 heures", re.IGNORECASE)


def parse_wttj_date(value: str | None) -> tuple[str | None, bool]:
    """Date WTTJ ISO -> (YYYY-MM-DD, is_precise=True). Sinon (None, False)."""
    if value and _ISO_RE.match(value):
        return (value[:10], True)
    return (None, False)


def relative_date(text: str | None, run_date: str) -> tuple[str | None, bool]:
    """Date relative Indeed -> (date approx, is_precise=False).

    is_precise est TOUJOURS False : ces dates sont des approximations et ne
    doivent pas servir d'axe temporel (cf. ENGINEERING_NOTES).
    """
    if not text:
        return (None, False)
    base = datetime.strptime(run_date, "%Y-%m-%d").date()
    if _RECENT_RE.search(text):
        return (run_date, False)
    m = _JOURS_RE.search(text)
    if m:
        approx = base - timedelta(days=int(m.group(1)))
        return (approx.isoformat(), False)
    if _HEURES_RE.search(text):
        return (run_date, False)
    return (None, False)


def today_iso() -> str:
    return date.today().isoformat()
