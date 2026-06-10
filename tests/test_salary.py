"""Tests du parser de salaire texte libre + annualisation.

Fixtures = vrais échantillons rencontrés dans indeed-catinfo.json.
"""

from cartodata_de.parsing.salary import annualize, parse_salary_fr


def test_fourchette_annuelle():
    assert parse_salary_fr("De 45 000 € à 50 000 € par an") == {
        "min": 45000.0,
        "max": 50000.0,
        "period": "yearly",
    }


def test_montant_unique_annuel():
    assert parse_salary_fr("70 000 € par an") == {"min": 70000.0, "max": 70000.0, "period": "yearly"}


def test_a_partir_de():
    r = parse_salary_fr("À partir de 60 000 € par an")
    assert r["period"] == "yearly" and r["min"] == 60000.0


def test_mensuel_virgule_et_espace_insecable():
    r = parse_salary_fr("De 492,22 € à 1 823,03 € par mois")
    assert r["period"] == "monthly"
    assert round(r["max"]) == 1823


def test_sans_periode_renvoie_none():
    # Pas de période -> on n'annualise jamais sans hypothèse explicite
    assert parse_salary_fr("50 000 €") is None


def test_vide_renvoie_none():
    assert parse_salary_fr("") is None
    assert parse_salary_fr(None) is None


def test_annualisation_mensuelle():
    # 4000 €/mois -> 48 000 €/an
    assert annualize(4000, 4000, "monthly", "EUR") == (48000, 48000)


def test_annualisation_tjm():
    # TJM 500 € x 218 j = 109 000 €/an
    assert annualize(500, 500, "daily", "EUR") == (109000, 109000)


def test_hygiene_rejette_implausible_haut():
    # 610 000 €/an = parse erroné -> rejeté (NULL)
    assert annualize(610000, 610000, "yearly", "EUR") == (None, None)


def test_hygiene_rejette_implausible_bas():
    # 200 €/an -> rejeté
    assert annualize(200, 200, "yearly", "EUR") == (None, None)


def test_conversion_usd():
    # 100 000 USD/an -> ~92 000 € (taux figé 0.92)
    lo, hi = annualize(100000, 100000, "yearly", "USD")
    assert lo == 92000


def test_periode_inconnue():
    assert annualize(40000, 50000, None, "EUR") == (None, None)
