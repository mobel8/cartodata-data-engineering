"""Tests du référentiel géo commune -> département IDF."""

from cartodata_de.parsing.geo import dept_of, is_idf, slug


def test_slug_accents_et_espaces():
    assert slug("Boulogne-Billancourt") == "boulogne-billancourt"
    assert slug("Évry-Courcouronnes") == "evry-courcouronnes"
    assert slug("Saint-Ouen-sur-Seine") == "saint-ouen-sur-seine"


def test_dept_paris():
    assert dept_of("Paris") == "75"


def test_dept_communes_93():
    assert dept_of("Saint-Denis") == "93"
    assert dept_of("Le Bourget") == "93"


def test_dept_communes_92():
    assert dept_of("Nanterre") == "92"


def test_region_brute():
    assert dept_of("Île-de-France") == "IDF"


def test_hors_referentiel():
    assert dept_of("Lyon") == "Hors référentiel"


def test_non_precise():
    assert dept_of(None) == "Non précisé"
    assert dept_of("") == "Non précisé"


def test_is_idf():
    assert is_idf("Paris") is True
    assert is_idf("Le Bourget") is True
    assert is_idf("Lyon") is False
