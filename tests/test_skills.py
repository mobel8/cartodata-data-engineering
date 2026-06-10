"""Tests de l'extraction de compétences par dictionnaire regex."""

from cartodata_de.parsing.skills import extract_skills


def test_detecte_stack_data_eng():
    s = extract_skills("Data Engineer Python / SQL / Airflow / dbt sur AWS")
    assert {"Python", "SQL", "Airflow", "dbt", "AWS"} <= set(s)


def test_java_pas_javascript():
    assert "Java" not in extract_skills("Développeur JavaScript React")
    assert "Java" in extract_skills("Ingénieur Java Spring")


def test_power_bi_variantes():
    assert "Power BI" in extract_skills("Consultant PowerBI et Power Query")
    assert "Power Query" in extract_skills("Consultant PowerBI et Power Query")


def test_insensible_accents_casse():
    assert "Statistiques" in extract_skills("Maîtrise des STATISTIQUES appliquées")


def test_vide():
    assert extract_skills("") == []
    assert extract_skills(None) == []
