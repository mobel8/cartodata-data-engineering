"""Tests de la normalisation des dates (WTTJ absolue vs Indeed relative)."""

from cartodata_de.parsing.dates import parse_wttj_date, relative_date

RUN = "2026-06-10"


def test_wttj_iso_precise():
    assert parse_wttj_date("2026-05-21T10:00:00Z") == ("2026-05-21", True)


def test_wttj_non_iso():
    assert parse_wttj_date("hier") == (None, False)
    assert parse_wttj_date(None) == (None, False)


def test_indeed_il_y_a_jours():
    d, precise = relative_date("il y a 3 jours", RUN)
    assert d == "2026-06-07"
    assert precise is False  # JAMAIS précise : approximation


def test_indeed_plafond_30_plus():
    d, precise = relative_date("il y a 30+ jours", RUN)
    assert d == "2026-05-11"
    assert precise is False


def test_indeed_instant():
    assert relative_date("Publié à l'instant", RUN) == (RUN, False)


def test_indeed_heures():
    assert relative_date("il y a 5 heures", RUN) == (RUN, False)


def test_indeed_vide():
    assert relative_date("", RUN) == (None, False)
