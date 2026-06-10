"""Réconciliation cross-source (entity resolution WTTJ <-> Indeed).

Une même offre peut exister sur les deux sites (~les "twins"). On ne veut pas
la compter deux fois. Deux mécanismes :

  1. `load_twin_urls` : charge la résolution déjà vérifiée (cross-site.json,
     produite par le matcher d'origine) -> set d'URLs Indeed à marquer is_twin.
     C'est la source autoritaire utilisée par le pipeline.

  2. `find_twins` : ré-implémentation autonome du fuzzy-match (Jaccard sur
     tokens de titre + match entreprise) servant de **test de non-régression**
     contre la résolution vérifiée. Seuil conservé tel quel :
       - Jaccard tokens titre >= 0.6 AVEC match entreprise/lieu, ou
       - Jaccard tokens titre >= 0.85 sans match de lieu.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from cartodata_de.config import JACCARD_TITLE_MIN, JACCARD_TITLE_MIN_NO_LOCATION
from cartodata_de.parsing.geo import slug

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP = {"de", "la", "le", "les", "des", "et", "en", "du", "un", "une", "h", "f", "x"}


def title_tokens(title: str | None) -> set[str]:
    if not title:
        return set()
    import unicodedata

    norm = unicodedata.normalize("NFD", title.lower())
    norm = "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")
    return {t for t in _TOKEN_RE.findall(norm) if t not in _STOP and len(t) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def load_twin_urls(cross_site_path: Path | None) -> set[str]:
    """URLs Indeed marquées comme doublons inter-sites (on garde la version WTTJ)."""
    if not cross_site_path or not Path(cross_site_path).exists():
        return set()
    data = json.loads(Path(cross_site_path).read_text(encoding="utf-8"))
    by_url = data.get("byUrl", data) if isinstance(data, dict) else {}
    return {u for u in by_url if isinstance(u, str) and re.search(r"indeed\.", u, re.IGNORECASE)}


def is_twin(o1: dict, o2: dict) -> bool:
    """Deux offres (champs title/company/city) sont-elles la même offre ?"""
    j = jaccard(title_tokens(o1.get("title")), title_tokens(o2.get("title")))
    same_company = bool(o1.get("company")) and slug(o1.get("company")) == slug(o2.get("company"))
    same_city = bool(o1.get("city")) and slug(o1.get("city")) == slug(o2.get("city"))
    if j >= JACCARD_TITLE_MIN and (same_company or same_city):
        return True
    return j >= JACCARD_TITLE_MIN_NO_LOCATION


def find_twins(wttj: list[dict], indeed: list[dict]) -> set[str]:
    """Ré-implémentation du matcher : renvoie les URLs Indeed jugées doublons."""
    twins: set[str] = set()
    for ind in indeed:
        for w in wttj:
            if is_twin(ind, w):
                if ind.get("url"):
                    twins.add(ind["url"])
                break
    return twins
