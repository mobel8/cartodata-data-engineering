"""WTTJ (Welcome to the Jungle) : source structurée -> SILVER.

Schéma source : {url, name, contract, remote, date, city, exp, edu,
profession{fr/en/es/cs/sk}, salMin, salMax, salPer, salCur, ats, status}.
"""

from __future__ import annotations

import re

from cartodata_de.parsing.dates import parse_wttj_date
from cartodata_de.parsing.geo import dept_of, is_idf
from cartodata_de.parsing.salary import annualize
from cartodata_de.parsing.skills import extract_skills
from cartodata_de.schemas import OfferSilver
from cartodata_de.sources.labels import normalize_remote

_COMPANY_RE = re.compile(r"/companies/([^/]+)")


def _company(url: str | None) -> str | None:
    if not url:
        return None
    m = _COMPANY_RE.search(url)
    return m.group(1) if m else None


def to_silver(records: list[dict], run_date: str, ingested_at: str) -> list[dict]:
    out: list[dict] = []
    for i, o in enumerate(records):
        lo, hi = annualize(o.get("salMin"), o.get("salMax"), o.get("salPer"), o.get("salCur"))
        posted, precise = parse_wttj_date(o.get("date"))
        profession = (o.get("profession") or {}).get("fr") if isinstance(o.get("profession"), dict) else None
        offer = OfferSilver(
            offer_id=f"WTTJ_{i}",
            source="WTTJ",
            url=o.get("url"),
            apply_url=o.get("applyUrl"),
            title=o.get("name"),
            company=_company(o.get("url")),
            city=o.get("city"),
            departement=dept_of(o.get("city")),
            is_idf=is_idf(o.get("city")),
            profession=profession,
            kw=None,
            contract=o.get("contract") or "Non précisé",
            experience=o.get("exp"),
            education=o.get("edu"),
            remote=normalize_remote(o.get("remote")),
            sal_min_eur=lo,
            sal_max_eur=hi,
            sal_source_period=o.get("salPer"),
            posted_date=posted,
            date_is_precise=precise,
            status=o.get("status"),
            is_twin=False,
            skills=extract_skills(o.get("name")),
            run_date=run_date,
            ingested_at=ingested_at,
        )
        out.append(offer.model_dump())
    return out
