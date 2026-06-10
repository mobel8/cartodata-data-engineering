"""Extraction de compétences techniques par dictionnaire regex.

Volontairement simple et transparent (pas de ML) : chaque compétence est une
regex sur le titre + snippet + mots-clés. Le résultat alimente le mart
top_competences. Dictionnaire défendable et auditable à l'oral.
"""

from __future__ import annotations

import re
import unicodedata

SKILLS: list[tuple[str, re.Pattern]] = [
    ("Python", re.compile(r"\bpython\b")),
    ("SQL", re.compile(r"\bsql\b")),
    ("Java", re.compile(r"\bjava\b(?!script)")),
    ("Scala", re.compile(r"\bscala\b")),
    ("Spark", re.compile(r"\bspark\b")),
    ("Hadoop", re.compile(r"\bhadoop\b")),
    ("Kafka", re.compile(r"\bkafka\b")),
    ("Airflow", re.compile(r"\bairflow\b")),
    ("dbt", re.compile(r"\bdbt\b")),
    ("Snowflake", re.compile(r"\bsnowflake\b")),
    ("BigQuery", re.compile(r"\bbigquery\b")),
    ("Databricks", re.compile(r"\bdatabricks\b")),
    ("AWS", re.compile(r"\baws\b")),
    ("Azure", re.compile(r"\bazure\b")),
    ("GCP", re.compile(r"\b(gcp|google cloud)\b")),
    ("Docker", re.compile(r"\bdocker\b")),
    ("Kubernetes", re.compile(r"\b(kubernetes|k8s)\b")),
    ("Power BI", re.compile(r"\bpower ?bi\b")),
    ("Tableau", re.compile(r"\btableau\b")),
    ("Looker", re.compile(r"\blooker\b")),
    ("Qlik", re.compile(r"\bqlik\b")),
    ("Excel", re.compile(r"\bexcel\b")),
    ("ETL", re.compile(r"\betl\b")),
    ("Machine Learning", re.compile(r"\bmachine learning\b")),
    ("Deep Learning", re.compile(r"\bdeep learning\b")),
    ("NLP", re.compile(r"\bnlp\b|langage naturel")),
    ("LLM", re.compile(r"\bllm\b")),
    ("RAG", re.compile(r"\brag\b")),
    ("Computer Vision", re.compile(r"\bcomputer vision\b|vision par ordinateur")),
    ("PyTorch", re.compile(r"\bpytorch\b")),
    ("TensorFlow", re.compile(r"\btensorflow\b")),
    ("scikit-learn", re.compile(r"\bscikit|sklearn\b")),
    ("Pandas", re.compile(r"\bpandas\b")),
    ("Power Query", re.compile(r"\bpower query\b")),
    ("VBA", re.compile(r"\bvba\b")),
    ("Git", re.compile(r"\bgit\b")),
    ("Linux", re.compile(r"\blinux\b")),
    ("Statistiques", re.compile(r"\bstatisti")),
]


def extract_skills(text: str | None) -> list[str]:
    if not text:
        return []
    norm = unicodedata.normalize("NFD", text.lower())
    norm = "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")
    return [label for label, pattern in SKILLS if pattern.search(norm)]
