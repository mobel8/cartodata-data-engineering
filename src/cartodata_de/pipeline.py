"""Orchestrateur ELT medallion : bronze -> silver -> gold.

La logique métier vit ici, en Python pur et importable, indépendamment de
l'orchestrateur. Dagster (orchestration/definitions.py) se contente d'envelopper
ces mêmes fonctions en assets — on peut donc rejouer le pipeline aussi bien via
`python -m cartodata_de.pipeline` que via `dagster dev`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from cartodata_de import bronze, config
from cartodata_de.dedup import load_twin_urls
from cartodata_de.sources import indeed as indeed_src
from cartodata_de.sources import wttj as wttj_src

# Console Windows en cp1252 -> on force l'UTF-8 pour éviter les UnicodeEncodeError.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass

SILVER_COLUMNS = [
    "offer_id", "source", "url", "apply_url", "title", "company", "city",
    "departement", "is_idf", "profession", "kw", "contract", "experience",
    "education", "remote", "sal_min_eur", "sal_max_eur", "sal_source_period",
    "has_salary", "posted_date", "date_is_precise", "status", "is_twin",
    "skills", "run_date", "ingested_at",
]


def build_silver(run_date: str) -> dict:
    """Bronze -> Silver : parse, valide (pydantic), réconcilie, écrit Parquet."""
    config.ensure_dirs()
    # ingested_at logique (dérivé du run_date) => Parquet reproductible.
    ingested_at = f"{run_date}T00:00:00Z"

    wttj_raw = bronze.load_raw(bronze.bronze_path("wttj", run_date))
    indeed_raw = bronze.load_raw(bronze.bronze_path("indeed", run_date))
    cross_path = bronze.bronze_path("cross_site", run_date)
    twin_urls = load_twin_urls(cross_path)

    wttj_rows = wttj_src.to_silver(wttj_raw, run_date, ingested_at)
    indeed_rows, rejects = indeed_src.to_silver(indeed_raw, twin_urls, run_date, ingested_at)
    rows = wttj_rows + indeed_rows

    df = pd.DataFrame(rows, columns=SILVER_COLUMNS)
    df.to_parquet(config.SILVER_OFFERS, index=False)
    pd.DataFrame(rejects, columns=["offer_id", "salary_raw", "reason", "run_date"]).to_parquet(
        config.SILVER_REJECTS, index=False
    )

    n_twins = int(df["is_twin"].sum())
    n_salary = int(df["has_salary"].sum())
    stats = {
        "run_date": run_date,
        "n_total": len(df),
        "n_wttj": int((df["source"] == "WTTJ").sum()),
        "n_indeed": int((df["source"] == "Indeed").sum()),
        "n_twins_indeed": n_twins,
        "n_salary": n_salary,
        "pct_salary": round(100.0 * n_salary / len(df), 1) if len(df) else 0.0,
        "n_rejects_salaire": len(rejects),
        "silver_path": str(config.SILVER_OFFERS),
    }
    (config.SILVER / "_stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return stats


def build_gold(run_date: str, select: str | None = None, exclude: str | None = None) -> int:
    """Silver -> Gold : exécute `dbt build` (modèles staging/marts + tests)."""
    cmd = [
        sys.executable, "-m", "dbt.cli.main", "build",
        "--project-dir", str(config.DBT_DIR),
        "--profiles-dir", str(config.DBT_DIR),
        "--vars", json.dumps({
            "silver_path": str(config.SILVER_OFFERS).replace("\\", "/"),
            "run_date": run_date,
        }),
    ]
    if select:
        cmd += ["--select", select]
    if exclude:
        cmd += ["--exclude", exclude]
    print("-> dbt:", " ".join(cmd))
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.call(cmd, cwd=str(config.DBT_DIR), env=env)


def export_gold_parquet() -> list[str]:
    """Exporte les marts du warehouse vers data/gold/*.parquet (artefact partageable)."""
    from cartodata_de import warehouse

    config.ensure_dirs()
    exported = []
    for table in warehouse.list_marts() + ["fct_offres"]:
        out = config.GOLD / f"{table}.parquet"
        con = warehouse.connect(read_only=True)
        try:
            con.execute(f"COPY {table} TO '{str(out).replace(chr(92), '/')}' (FORMAT PARQUET)")
            exported.append(table)
        finally:
            con.close()
    return exported


def run(run_date: str, skip_dbt: bool = False, export: bool = True, exclude: str | None = None) -> dict:
    print(f"== Pipeline CartoData DE — run_date={run_date} ==")
    manifest = bronze.ingest(run_date)
    present = {s["source"]: s["present"] for s in manifest["sources"]}
    print(f"  bronze ingéré : {present}")
    stats = build_silver(run_date)
    print(
        f"  silver : {stats['n_total']} offres "
        f"(WTTJ {stats['n_wttj']} + Indeed {stats['n_indeed']}, "
        f"twins {stats['n_twins_indeed']}, salaire {stats['pct_salary']}%)"
    )
    if not skip_dbt:
        rc = build_gold(run_date, exclude=exclude)
        stats["dbt_returncode"] = rc
        if rc == 0 and export:
            stats["gold_exported"] = export_gold_parquet()
            print(f"  gold exporté : {len(stats['gold_exported'])} tables -> data/gold/")
        if rc != 0:
            print("  ⚠ dbt build a échoué (voir logs dbt ci-dessus)")
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Pipeline ELT CartoData Data Engineering")
    ap.add_argument("--run-date", default=config.RUN_DATE)
    ap.add_argument("--skip-dbt", action="store_true", help="bronze+silver seulement")
    ap.add_argument("--no-export", action="store_true", help="ne pas exporter le gold en Parquet")
    ap.add_argument(
        "--ci", action="store_true",
        help="mode CI/échantillon : exclut les tests 'fullonly' (comptages de référence)",
    )
    args = ap.parse_args()
    exclude = "tag:fullonly" if args.ci else None
    stats = run(args.run_date, skip_dbt=args.skip_dbt, export=not args.no_export, exclude=exclude)
    Path(config.DATA / "_last_run.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    rc = stats.get("dbt_returncode", 0)
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
