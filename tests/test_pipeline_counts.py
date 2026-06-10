"""Test d'intégration : comptages de référence figés sur le dataset COMPLET.

Reproduit en pytest le garde-fou anti-hallucination du test dbt singulier.
Sauté automatiquement si seul l'échantillon est disponible (CI), car ces
nombres ne valent que sur les données complètes vérifiées sur disque.
"""

import pandas as pd
import pytest

from cartodata_de import bronze, config, pipeline

RUN = "2026-06-10"


def _full_dataset_available() -> bool:
    src = config.WTTJ_SOURCE
    return bool(src and src.exists() and "fixtures" not in str(src))


pytestmark = pytest.mark.skipif(
    not _full_dataset_available(),
    reason="dataset complet absent (CI tourne sur l'échantillon) — voir tests dbt fullonly",
)


@pytest.fixture(scope="module")
def silver_df() -> pd.DataFrame:
    bronze.ingest(RUN)
    pipeline.build_silver(RUN)
    return pd.read_parquet(config.SILVER_OFFERS)


def test_volumes_sources(silver_df):
    assert (silver_df["source"] == "WTTJ").sum() == 2171
    assert (silver_df["source"] == "Indeed").sum() == 5752


def test_wttj_status_200(silver_df):
    w = silver_df[silver_df["source"] == "WTTJ"]
    assert (w["status"] == 200).sum() == 2164


def test_contrats_wttj(silver_df):
    w = silver_df[silver_df["source"] == "WTTJ"]
    assert (w["contract"] == "CDI").sum() == 1417
    assert (w["contract"] == "Stage").sum() == 336
    assert (w["contract"] == "Alternance").sum() == 326


def test_paris(silver_df):
    w = silver_df[silver_df["source"] == "WTTJ"]
    assert (w["city"] == "Paris").sum() == 1216


def test_unicite_url(silver_df):
    urls = silver_df["url"].dropna()
    assert len(urls) == urls.nunique()
