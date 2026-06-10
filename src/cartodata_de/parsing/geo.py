"""Géo : commune -> département IDF + slug de normalisation.

Référentiel embarqué des communes IDF les plus fréquentes du dataset.
Un hook BAN (Base Adresse Nationale) optionnel permet le géocodage lat/lon
(non appelé dans le pipeline cœur : pas d'I/O réseau dans les transformations).
"""

from __future__ import annotations

import unicodedata

# commune (slug) -> code département
DEPT: dict[str, list[str]] = {
    "75": ["paris"],
    "92": [
        "nanterre", "montrouge", "boulogne-billancourt", "puteaux", "courbevoie",
        "issy-les-moulineaux", "levallois-perret", "neuilly-sur-seine", "clichy",
        "suresnes", "rueil-malmaison", "colombes", "asnieres-sur-seine", "bois-colombes",
        "gennevilliers", "clamart", "meudon", "antony", "bagneux", "chatillon", "sevres",
        "vanves", "la-garenne-colombes", "saint-cloud", "malakoff", "fontenay-aux-roses",
        "sceaux", "le-plessis-robinson", "chatenay-malabry", "bourg-la-reine", "garches",
        "chaville", "vaucresson",
    ],
    "93": [
        "saint-denis", "saint-ouen", "saint-ouen-sur-seine", "aubervilliers", "pantin",
        "montreuil", "bobigny", "noisy-le-grand", "rosny-sous-bois", "bagnolet",
        "le-bourget", "la-courneuve", "drancy", "aulnay-sous-bois", "epinay-sur-seine",
        "stains", "villepinte", "tremblay-en-france", "livry-gargan", "sevran",
        "romainville", "les-lilas", "noisy-le-sec", "le-blanc-mesnil", "bondy", "dugny",
    ],
    "94": [
        "creteil", "ivry-sur-seine", "vitry-sur-seine", "charenton-le-pont",
        "saint-maur-des-fosses", "vincennes", "fontenay-sous-bois", "maisons-alfort",
        "alfortville", "villejuif", "le-kremlin-bicetre", "kremlin-bicetre", "cachan",
        "arcueil", "gentilly", "rungis", "orly", "choisy-le-roi", "thiais",
        "nogent-sur-marne", "champigny-sur-marne", "fresnes", "chevilly-larue",
        "saint-mande", "bry-sur-marne", "joinville-le-pont",
    ],
    "78": [
        "versailles", "saint-quentin-en-yvelines", "montigny-le-bretonneux", "guyancourt",
        "velizy-villacoublay", "velizy", "poissy", "sartrouville", "mantes-la-jolie",
        "les-mureaux", "plaisir", "trappes", "elancourt", "rambouillet", "le-chesnay",
        "saint-germain-en-laye", "conflans-sainte-honorine", "chatou", "houilles",
        "carrieres-sur-seine", "buc", "voisins-le-bretonneux",
    ],
    "91": [
        "evry", "evry-courcouronnes", "massy", "palaiseau", "corbeil-essonnes",
        "savigny-sur-orge", "sainte-genevieve-des-bois", "viry-chatillon", "athis-mons",
        "les-ulis", "orsay", "gif-sur-yvette", "draveil", "longjumeau", "montgeron",
        "wissous", "saclay", "ris-orangis", "bretigny-sur-orge",
    ],
    "95": [
        "cergy", "pontoise", "argenteuil", "sarcelles", "garges-les-gonesse",
        "franconville", "ermont", "goussainville", "roissy-en-france", "roissy", "gonesse",
        "eaubonne", "herblay", "taverny", "montmorency", "osny", "bezons",
        "cormeilles-en-parisis", "sannois", "domont",
    ],
    "77": [
        "meaux", "melun", "chelles", "champs-sur-marne", "torcy", "pontault-combault",
        "savigny-le-temple", "bussy-saint-georges", "serris", "noisiel",
        "marne-la-vallee", "combs-la-ville", "roissy-en-brie", "villeparisis",
        "mitry-mory", "lieusaint", "lagny-sur-marne",
    ],
}

CITY2DEPT: dict[str, str] = {c: d for d, cities in DEPT.items() for c in cities}
IDF_SET: set[str] = {c for cities in DEPT.values() for c in cities} | {"ile-de-france"}


def slug(value: str | None) -> str:
    if not value:
        return ""
    norm = unicodedata.normalize("NFD", value.lower())
    norm = "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")
    out, prev_dash = [], False
    for ch in norm:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-")


def dept_of(city: str | None) -> str:
    s = slug(city)
    if s in CITY2DEPT:
        return CITY2DEPT[s]
    if s in IDF_SET:
        return "IDF"
    return "Hors référentiel" if s else "Non précisé"


def is_idf(city: str | None) -> bool:
    s = slug(city)
    return s in CITY2DEPT or s in IDF_SET
