"""Tests de la réconciliation cross-source (fuzzy-match Jaccard)."""

from cartodata_de.dedup import find_twins, is_twin, jaccard, title_tokens


def test_title_tokens_strip_stopwords():
    assert title_tokens("Data Engineer H/F") == {"data", "engineer"}


def test_jaccard_identique():
    a = {"data", "engineer"}
    assert jaccard(a, a) == 1.0


def test_jaccard_disjoint():
    assert jaccard({"data"}, {"vente"}) == 0.0


def test_twin_meme_titre_meme_entreprise():
    a = {"title": "Data Engineer H/F", "company": "acme", "city": "Paris"}
    b = {"title": "Data Engineer", "company": "acme", "city": "Paris"}
    assert is_twin(a, b) is True


def test_pas_twin_titres_eloignes():
    a = {"title": "Data Engineer", "company": "acme", "city": "Paris"}
    b = {"title": "Commercial sédentaire", "company": "beta", "city": "Lyon"}
    assert is_twin(a, b) is False


def test_twin_haute_similarite_sans_lieu():
    # Jaccard >= 0.85 suffit même sans match entreprise/lieu
    a = {"title": "Machine Learning Engineer NLP", "company": "x", "city": None}
    b = {"title": "Machine Learning Engineer NLP", "company": "y", "city": None}
    assert is_twin(a, b) is True


def test_find_twins_renvoie_urls_indeed():
    wttj = [{"title": "Data Scientist Senior", "company": "acme", "city": "Paris"}]
    indeed = [
        {"title": "Data Scientist", "company": "acme", "city": "Paris", "url": "https://indeed.com/1"},
        {"title": "Chauffeur livreur", "company": "zzz", "city": "Lille", "url": "https://indeed.com/2"},
    ]
    twins = find_twins(wttj, indeed)
    assert "https://indeed.com/1" in twins
    assert "https://indeed.com/2" not in twins
