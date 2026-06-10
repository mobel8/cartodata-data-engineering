# ENGINEERING_NOTES — décisions clés (à défendre à l'oral)

> Notes courtes réécrites **de mémoire** : chaque choix doit pouvoir être expliqué au tableau en 3 minutes. C'est l'assurance anti « code généré non défendable ».

## 1. Pourquoi l'idempotence par *rebuild from bronze* (et non un MERGE/upsert)
Le BRONZE est **immuable et partitionné par date de run** (`dt=YYYY-MM-DD`, append-only) : on n'écrase jamais une partition déjà ingérée. Le SILVER et le GOLD sont **entièrement reconstruits** depuis le bronze à chaque run. Conséquence : **rejouer le pipeline avec le même `RUN_DATE` redonne exactement le même GOLD** (les sorties ne dépendent pas de l'horloge — `ingested_at` est dérivé du `run_date`, pas de `now()`). Pour une volumétrie de quelques dizaines de milliers de lignes, *full refresh* > *incrémental* : plus simple, plus sûr, et l'historique des partitions bronze permet quand même de mesurer la tension du marché dans le temps. La clé de dédup logique reste **url + date** (upsert mental documenté), prête si l'on bascule en incrémental.

## 2. Pourquoi DuckDB plutôt que Spark
Des dizaines de milliers de lignes ne justifient **pas** un cluster. DuckDB est embarqué, lit/écrit Parquet nativement, fait du SQL analytique (window functions, `quantile_cont`, `unnest`) à pleine vitesse, zéro serveur, zéro coût. **Savoir ne pas sur-dimensionner est une compétence d'ingénieur.** Si le volume était ×1000, on porterait les mêmes modèles dbt sur un warehouse colonne (BigQuery/Snowflake) — l'archive medallion ne changerait pas.

## 3. Réconciliation cross-source : seuil Jaccard 0.6
Une offre peut exister sur WTTJ **et** Indeed (« twins »). On ne veut pas la compter deux fois. Le matcher (`dedup.py`) compare les **tokens de titre** (Jaccard) + un match entreprise/lieu :
- Jaccard ≥ **0.6** **avec** match entreprise ou lieu → twin ;
- Jaccard ≥ **0.85** seul (sans lieu) → twin.
Seuil **conservé tel quel** depuis le matcher d'origine. La résolution autoritaire (`cross-site.json`) marque les URLs Indeed `is_twin` ; on garde la version WTTJ (mieux structurée). `find_twins()` ré-implémente le matcher et sert de **test de non-régression**.

## 4. Salaires : le vrai travail data-quality
Indeed = **texte libre FR** (« De 45 000 € à 50 000 € par an », « De 492,22 € à 1 823,03 € par mois », espaces insécables, virgule décimale). WTTJ = structuré (salMin/salMax/salPer/salCur, parfois en chaîne). On ramène tout à une **fourchette annuelle EUR comparable** : mensuel ×12, **journalier (TJM) ×218 j ouvrés** (hypothèse explicite), USD→EUR à 0,92 (taux figé, documenté). **Hygiène** : toute borne annualisée hors **[8 000, 300 000]** est un parse erroné → mise à NULL et **tracée** dans `rejets_salaire.parquet` (jamais de rejet silencieux). Résultat : couverture salaire **24,1 %**, assumée en clair.

## 5. Dates Indeed : 100 % relatives → jamais un axe temporel
« il y a 30+ jours » est un **plafond**, pas une date. On les convertit en date approximative (`run_date − N`) mais on les marque `date_is_precise = false` et on les **exclut de `dim_date`** et de la série temporelle. Seules les dates **WTTJ absolues** alimentent l'axe temporel. Ne jamais présenter une tendance Indeed comme fiable.

## 6. Champs vides → NULL explicite (complétude honnête)
WTTJ encode l'absence par une **chaîne vide** `""`. Un validateur pydantic normalise `""` → `NULL` sur les champs optionnels, sinon la complétude serait **gonflée** (un `""` compté comme « rempli »). C'est pourquoi Expérience tombe à **11,6 %** et Diplôme à **9,1 %** — les vrais chiffres. La complétude est un **indicateur de qualité affiché**, pas un trou masqué.

## 7. Freshness = 6h, alignée sur le scraper
Le schedule Dagster (`0 */6 * * *`) rejoue **bronze→silver→gold** toutes les 6h, à la cadence de la tâche planifiée qui rafraîchit les sources. C'est le SLA de fraîcheur du data contract. Le **scraping lui-même reste hors CI** (tâche locale) ; la CI rejoue le **build** sur l'échantillon — claim formulé honnêtement.

## 8. Logique métier découplée de l'orchestrateur
Toute la logique vit dans `cartodata_de` (Python pur, importable, testé). Dagster ne fait qu'**envelopper** les mêmes fonctions en assets. On peut donc rejouer le pipeline via `python -m cartodata_de.pipeline` **ou** via `dagster dev` — l'orchestrateur n'est jamais un point de couplage dur. (Détail vécu : ne pas mettre `from __future__ import annotations` dans le fichier Dagster, sinon l'introspection du type `context` casse la validation.)

## 9. CI sur échantillon, comptages de référence sur données complètes
La CI tourne sur un **échantillon commité** (`tests/fixtures/`, ~650 lignes) pour ne pas redistribuer tout le corpus et rester rapide/déterministe. Les **comptages de référence** (2171 / 1417 / 5752 …) ne valent que sur le dataset complet : leur test dbt est tagué `fullonly` et **exclu en CI** (`--exclude tag:fullonly`), mais rejoué en local/prod. Truncation jamais silencieuse : documentée.
