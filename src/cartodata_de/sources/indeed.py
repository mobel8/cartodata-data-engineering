"""Indeed : source texte libre -> SILVER.

Schéma source (dict clé-par-jobId) : {jk, title, company, loc, city, state,
jobTypes[], salary (texte libre), date (relative), remote, sponsored,
snippet, url, kw}.

Le salaire est du texte libre FR : on le parse, on l'annualise, et on
**trace les chaînes non parsées** dans une table de rejet (transparence
data-quality, jamais de rejet silencieux).
"""

from __future__ import annotations

from cartodata_de.parsing.dates import relative_date
from cartodata_de.parsing.geo import dept_of, is_idf
from cartodata_de.parsing.salary import annualize, parse_salary_fr
from cartodata_de.parsing.skills import extract_skills
from cartodata_de.schemas import OfferSilver
from cartodata_de.sources.labels import infer_contract_indeed, normalize_remote


def to_silver(
    records: list[dict],
    twin_urls: set[str],
    run_date: str,
    ingested_at: str,
) -> tuple[list[dict], list[dict]]:
    out: list[dict] = []
    rejects: list[dict] = []
    for i, o in enumerate(records):
        salary_raw = o.get("salary")
        parsed = parse_salary_fr(salary_raw)
        if parsed:
            lo, hi = annualize(parsed["min"], parsed["max"], parsed["period"], "EUR")
        else:
            lo, hi = None, None
        # Salaire renseigné mais non exploitable -> rejet tracé
        if salary_raw and lo is None:
            rejects.append(
                {
                    "offer_id": f"IND_{o.get('jk') or i}",
                    "salary_raw": salary_raw,
                    "reason": "non parsé" if not parsed else "hors plage plausible après annualisation",
                    "run_date": run_date,
                }
            )
        posted, precise = relative_date(o.get("date"), run_date)
        city = o.get("city") or o.get("loc")
        url = o.get("url")
        offer = OfferSilver(
            offer_id=f"IND_{o.get('jk') or i}",
            source="Indeed",
            url=url,
            apply_url=url,
            title=o.get("title"),
            company=o.get("company"),
            city=city,
            departement=dept_of(city),
            is_idf=is_idf(city),
            profession=None,
            kw=o.get("kw"),
            contract=infer_contract_indeed(o.get("jobTypes")),
            experience=None,
            education=None,
            remote=normalize_remote(o.get("remote")),
            sal_min_eur=lo,
            sal_max_eur=hi,
            sal_source_period=parsed["period"] if parsed else None,
            posted_date=posted,
            date_is_precise=precise,
            status=200,
            is_twin=bool(url) and url in twin_urls,
            skills=extract_skills(
                f"{o.get('title') or ''} {o.get('snippet') or ''} {o.get('kw') or ''}"
            ),
            run_date=run_date,
            ingested_at=ingested_at,
        )
        out.append(offer.model_dump())
    return out, rejects
