"""Orchestration Dagster : asset graph bronze -> silver -> gold.

Les assets enveloppent les MÊMES fonctions que le pipeline Python pur
(cartodata_de.pipeline) : la logique métier n'est pas dupliquée, Dagster ne fait
qu'ajouter scheduling, lineage visuel, retries et observabilité.

Lancer l'UI :   dagster dev            (charge workspace.yaml)
Matérialiser :  dagster asset materialize -m ... --select "*"
"""

# NB : pas de `from __future__ import annotations` ici — Dagster introspecte le
# type réel du paramètre `context` (une annotation stringifiée casse la validation).

from dagster import (
    AssetExecutionContext,
    Definitions,
    MetadataValue,
    RetryPolicy,
    ScheduleDefinition,
    asset,
    define_asset_job,
)

from cartodata_de import bronze, config, pipeline
from cartodata_de.sources import housing

GROUP = "observatoire_emploi"


@asset(group_name=GROUP, retry_policy=RetryPolicy(max_retries=2), compute_kind="python")
def bronze_offers(context: AssetExecutionContext) -> None:
    """Archive immuable et horodatée des sources brutes (WTTJ + Indeed + cross-site)."""
    manifest = bronze.ingest(config.RUN_DATE)
    present = {s["source"]: s["present"] for s in manifest["sources"]}
    context.add_output_metadata({"run_date": config.RUN_DATE, "sources_présentes": str(present)})


@asset(deps=[bronze_offers], group_name=GROUP, compute_kind="python")
def silver_offers(context: AssetExecutionContext) -> None:
    """Parse, valide (pydantic), réconcilie cross-source -> Parquet SILVER typé."""
    stats = pipeline.build_silver(config.RUN_DATE)
    context.add_output_metadata(
        {
            "offres": MetadataValue.int(stats["n_total"]),
            "wttj": MetadataValue.int(stats["n_wttj"]),
            "indeed": MetadataValue.int(stats["n_indeed"]),
            "twins_dédupliqués": MetadataValue.int(stats["n_twins_indeed"]),
            "couverture_salaire_%": MetadataValue.float(stats["pct_salary"]),
            "rejets_salaire": MetadataValue.int(stats["n_rejects_salaire"]),
        }
    )


@asset(deps=[silver_offers], group_name=GROUP, compute_kind="dbt")
def gold_marts(context: AssetExecutionContext) -> None:
    """Transformations dbt (staging -> étoile -> marts) + tests, puis export Parquet."""
    rc = pipeline.build_gold(config.RUN_DATE)
    if rc != 0:
        raise RuntimeError(f"dbt build a échoué (code {rc}) — voir logs dbt")
    exported = pipeline.export_gold_parquet()
    context.add_output_metadata({"tables_exportées": MetadataValue.int(len(exported))})


@asset(group_name="backlog_territoire", compute_kind="stub")
def housing_bronze(context: AssetExecutionContext) -> None:
    """STUB (backlog) : greffe territoire DVF/DPE/BAN — prouve la généricité de l'archi.

    Volontairement non implémenté : démontre que l'architecture medallion accueille
    un 2e domaine sans diluer le cœur emploi. Hors planification 6h.
    """
    info = housing.ingest_housing_bronze(config.RUN_DATE)
    context.add_output_metadata(
        {"status": info["status"], "sources_cibles": ", ".join(housing.SUPPORTED)}
    )


# Job + planification 6h (= SLA de fraîcheur) — cœur emploi UNIQUEMENT (housing exclu).
refresh_observatoire = define_asset_job(
    "refresh_observatoire",
    selection=["bronze_offers", "silver_offers", "gold_marts"],
)
schedule_6h = ScheduleDefinition(
    job=refresh_observatoire,
    cron_schedule="0 */6 * * *",
    execution_timezone="Europe/Paris",
)

defs = Definitions(
    assets=[bronze_offers, silver_offers, gold_marts, housing_bronze],
    jobs=[refresh_observatoire],
    schedules=[schedule_6h],
)
