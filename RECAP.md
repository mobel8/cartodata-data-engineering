# 🗂️ RÉCAP — Lakehouse ELT orchestré & DataOps (module Data Engineering)

> Fiche de récapitulation **exhaustive** : quoi, pourquoi, comment, chiffres, décisions, état, lancement/publication. (À jour au 2026-06-10.)

## 1. En une phrase
**Module #01 — le SOCLE** de la plateforme CartoData IDF : un **lakehouse ELT medallion** (bronze → silver → gold) qui industrialise les scrapers d'offres Data/IA d'Île-de-France en un pipeline **orchestré (Dagster) · transformé+testé (dbt-duckdb) · conteneurisé (Docker) · exposé (FastAPI) · cloud-ready (sync S3/R2)**, produisant le **dataset GOLD** que tous les autres modules consomment.

## 2. Objectif & usage
Projet portfolio pour la famille **Data Engineering / Cloud / Automatisation**, pour **compenser le manque d'expérience** par une preuve d'ingénierie de production et candidater aux postes du même domaine (Data Engineer, AI/Data Engineer Data Factory, Automation Data Engineer, ingénieur ETL/ELT, Analytics Engineer dbt, Cloud Data Engineer, DataOps, Data Engineer/Data Analyst, Chargé CRM & automatisation). Récit méta : *« voici la tuyauterie qui produit l'observatoire de VOTRE propre marché concurrentiel »*.

## 3. État : ✅ CONSTRUIT, EXÉCUTÉ & VÉRIFIÉ
- Pipeline complet exécuté de bout en bout sur les **données réelles** (7 923 lignes silver → 7 643 gold).
- **dbt : 56/56 tests PASS** (modèles + qualité + data contract figé). **pytest : 44/44 PASS**. **ruff : clean**.
- **Dagster** : asset graph validé et **matérialisé en live** (bronze + silver + gold, dbt exécuté dans l'asset gold).
- **FastAPI** : endpoints vérifiés (TestClient). **CI sur échantillon : verte** (PASS=55, fullonly exclu).
- Stack **réelle** Python 3.11 + DuckDB + dbt-duckdb + Dagster + FastAPI (Docker non lancé localement — non installé — mais Dockerfile/compose fournis).
- Dépôt **public-safe** : aucune information personnelle.

## 4. Stack technique
Python 3.11 · **pydantic** (validation schéma) · pandas/pyarrow · **DuckDB** (entrepôt embarqué) · **dbt-duckdb** (étoile + tests + docs/lineage) · **Dagster** (orchestration, schedule 6h, freshness) · **FastAPI** (API GOLD read-only) · **boto3** (sync objet S3/R2) · **pytest** + **ruff** · **GitHub Actions** (CI) · **Docker** + compose · Mermaid (archi).

## 5. Arborescence
```
01-data-engineering/
├── src/cartodata_de/
│   ├── parsing/{salary,dates,geo,skills}.py   fonctions pures (testées)
│   ├── sources/{wttj,indeed,labels,housing}.py
│   ├── schemas.py        schéma SILVER unifié (pydantic)
│   ├── dedup.py          réconciliation cross-source (Jaccard ≥0.6/0.85)
│   ├── bronze.py         ingestion immuable horodatée
│   ├── pipeline.py       orchestrateur ELT (entrypoint)
│   ├── warehouse.py      accès lecture DuckDB
│   └── api.py            API FastAPI GOLD
├── dbt/                  dbt-duckdb : sources.yml · staging · intermediate · marts · tests · contract figé
├── orchestration/        definitions.py (4 assets Dagster) + workspace.yaml
├── tests/                7 fichiers pytest + fixtures/ (échantillon 250+400+60)
├── contracts/gold_offre.yml      data contract (schéma, SLA, garanties, limites)
├── scripts/{make_fixtures,sync_cloud}.py
├── data/{bronze,silver,gold}/    (générés, gitignored) · warehouse/ (gitignored)
├── Dockerfile · docker-compose.yml · .github/workflows/ci.yml
├── README.md · ENGINEERING_NOTES.md · RECAP.md · pyproject.toml · requirements.txt · .gitignore
```

## 6. Pipeline (ELT medallion) — étapes
1. **BRONZE** : copie immuable horodatée des 2 sources + cross-site (`data/bronze/<source>/dt=…`, append-only).
2. **SILVER** (Python+pydantic) : parsing salaires FR + annualisation (mensuel×12, TJM×218, USD→EUR, hygiène 8k–300k) ; dates relatives Indeed → approx (marquées imprécises) ; vides → NULL ; dédup twins (cross-site) ; écriture **Parquet typé** + table de **rejets**.
3. **GOLD** (dbt-duckdb) : `stg_offres` → `int_offres_valides` (dédup/validité) → **étoile** (`fct_offres` + 8 `dim_*`) → **13 marts**. Tests dbt + contract figé. Export Parquet GOLD + warehouse DuckDB.
4. **Orchestration** : Dagster matérialise bronze→silver→gold (schedule 6h). **API** FastAPI lecture seule. **Sync** Parquet GOLD → bucket objet (si credentials).

## 7. Modèle en étoile (GOLD)
`fct_offres` + `dim_contrat`, `dim_remote`, `dim_metier` (profession.fr), `dim_lieu` (commune+département), `dim_entreprise`, `dim_experience`, `dim_education`, `dim_date` (WTTJ fiable). Détails & enums : `contracts/gold_offre.yml`.

## 8. Marts produits (13)
kpis · par_contrat · par_metier · par_departement · top_villes · salaire_par_contrat (box-plot, effectif≥5) · salaire_par_metier (≥8) · par_remote · par_experience · tension (métier×dépt) · top_competences · timeseries (WTTJ) · completude.

## 9. Chiffres clés (rafraîchis 2026-06-10)
- **7 643 offres** = WTTJ **2 164** + Indeed **5 479** − **273 twins**. Silver brut : 7 923.
- **2 290 entreprises** · **364 communes** · 86,5 % IDF identifié.
- **Salaire médian : 49 000 €** (Q1 29 664 · Q3 65 000). Médianes/contrat : Freelance 109 k · CDI 52,5 k · CDD 38 k · Stage 15 k.
- **152 rejets** de salaire Indeed (tracés).
- Top compétences : ML 586 · Python 297 · LLM 116 · Power BI 81 · ETL 79 · Azure 72 · SQL 71.
- Complétude : Ville 99,9 % · Métier/Télétravail/Date 28,3 % · **Salaire 24,1 %** · **Exp 11,6 %** · **Diplôme 9,1 %**.
- **Tests : dbt 56/56 · pytest 44/44 · ruff 0 erreur · CI échantillon verte.**

## 10. Décisions d'ingénierie (détail dans ENGINEERING_NOTES.md)
Idempotence par *rebuild from bronze* (immuable, `ingested_at` dérivé du run_date) · DuckDB plutôt que Spark · Jaccard ≥0.6 (cross-source) · salaires annualisés à hypothèses explicites + hygiène + rejets tracés · dates Indeed relatives exclues de l'axe temporel · `""`→NULL (complétude honnête) · freshness 6h · logique découplée de Dagster · CI sur échantillon, comptages de référence `fullonly` sur données complètes.

## 11. Lancer / Publier
```powershell
py -m pip install -r requirements.txt; py -m pip install -e .
py -m cartodata_de.pipeline            # full
py -m cartodata_de.pipeline --ci       # échantillon (CI)
dagster dev -f orchestration/definitions.py     # UI lineage :3000
uvicorn cartodata_de.api:app --reload           # API :8000/docs
py -m ruff check . ; py -m pytest
docker compose up                                # pipeline + API + Dagster
```
CI : `.github/workflows/ci.yml` (ruff + pytest + pipeline échantillon + dbt build + doc dbt en artefact).

## 12. Postes visés
Data Engineer (F/H, alternance) · AI/Data Engineer Data Factory · Automation Data Engineer · Ingénieur ETL/ELT · Analytics Engineer (dbt) · Cloud Data Engineer · Ingénieur DataOps · Data Engineer/Data Analyst · Chargé CRM & automatisation · Data Engineering Intern.

## 13. Limites assumées & next steps
Dates Indeed relatives ; contrat Indeed `Non précisé` ; géocodage lat/lon (BAN) non fait → granularité dépt (next) ; greffe territoire DVF/DPE/BAN **stubée** (`housing_bronze`) ; Docker non exécuté localement (non installé) ; scraping hors CI (tâche locale, la CI rejoue le build).

## 14. Confidentialité
Dépôt **public-safe** : **aucune information personnelle** (nom/email/téléphone/adresse/ville de domicile). « Le Bourget » n'apparaît que comme **commune d'offres** dans le référentiel géo (donnée marché), jamais comme information personnelle.

## 15. Place dans la plateforme
Module **#01 (SOCLE)** du monorepo **[CartoData IDF](../README.md)**. Produit le GOLD consommé par le module **#02 (Observatoire BI)** déjà construit, et par les modules ML / Gouvernance / GenAI à venir. *Une donnée maîtrisée, amortie sur plusieurs familles de postes.*
