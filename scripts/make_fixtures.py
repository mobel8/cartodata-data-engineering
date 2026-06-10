"""Génère de petits échantillons commités (tests/fixtures/) à partir des sources.

But : permettre à la CI et à un clone public de rejouer un build VERT sans
redistribuer l'intégralité du corpus scrapé. Données = offres d'emploi
publiques (aucune information personnelle).

Usage : py scripts/make_fixtures.py
"""

from __future__ import annotations

import itertools
import json
import re

from cartodata_de import config

N_WTTJ, N_INDEED, N_CROSS = 250, 400, 60

# Anti-fuite RGPD : on caviarde toute PII tierce (téléphones/emails) éventuellement
# présente dans le texte des offres avant de commiter l'échantillon public.
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Bornes \w pour ne PAS caviarder les runs de chiffres dans les hash d'ID (jobId, etc.).
_PHONE_RE = re.compile(r"(?<!\w)(?:\+33|0)\s*\d(?:[\s.\-]?\d{2}){4}(?!\d)")


def _scrub(obj):
    if isinstance(obj, str):
        s = _EMAIL_RE.sub("[email]", obj)
        return _PHONE_RE.sub("[tel]", s)
    if isinstance(obj, list):
        return [_scrub(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items()}
    return obj


def _load(path):
    return _scrub(json.loads(path.read_text(encoding="utf-8")))


def main() -> None:
    config.FIXTURES.mkdir(parents=True, exist_ok=True)

    wttj = _load(config.WTTJ_SOURCE)
    wttj_sample = wttj[:N_WTTJ] if isinstance(wttj, list) else list(wttj.values())[:N_WTTJ]
    (config.FIXTURES / "sample_wttj.json").write_text(
        json.dumps(wttj_sample, ensure_ascii=False), encoding="utf-8"
    )

    indeed = _load(config.INDEED_SOURCE)
    # On conserve la forme objet-wrapper (clés de hash) pour tester l'unwrap.
    indeed_sample = dict(itertools.islice(indeed.items(), N_INDEED)) if isinstance(indeed, dict) else {
        str(i): r for i, r in enumerate(indeed[:N_INDEED])
    }
    (config.FIXTURES / "sample_indeed.json").write_text(
        json.dumps(indeed_sample, ensure_ascii=False), encoding="utf-8"
    )

    cross = _load(config.CROSS_SITE_SOURCE)
    by_url = cross.get("byUrl", cross) if isinstance(cross, dict) else {}
    cross_sample = {"byUrl": dict(itertools.islice(by_url.items(), N_CROSS))}
    (config.FIXTURES / "sample_cross_site.json").write_text(
        json.dumps(cross_sample, ensure_ascii=False), encoding="utf-8"
    )

    print(
        f"Fixtures écrites : WTTJ {len(wttj_sample)}, Indeed {len(indeed_sample)}, "
        f"cross-site {len(cross_sample['byUrl'])} -> {config.FIXTURES}"
    )


if __name__ == "__main__":
    main()
