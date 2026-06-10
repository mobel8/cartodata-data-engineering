-- Test singulier "data contract" : les comptages doivent retomber sur les
-- nombres RE-VÉRIFIÉS sur disque. Si une transformation casse un total, ce test
-- échoue. Tagué 'fullonly' : il ne s'exécute que sur le dataset complet
-- (la CI tourne sur l'échantillon, où ces nombres ne s'appliquent pas).
{{ config(tags=['fullonly']) }}

WITH checks AS (
    SELECT 'wttj_total' AS verif,
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'WTTJ') AS obtenu,
           2171 AS attendu
    UNION ALL SELECT 'wttj_status_200',
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'WTTJ' AND status = 200), 2164
    UNION ALL SELECT 'cdi',
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'WTTJ' AND contract = 'CDI'), 1417
    UNION ALL SELECT 'stage',
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'WTTJ' AND contract = 'Stage'), 336
    UNION ALL SELECT 'alternance',
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'WTTJ' AND contract = 'Alternance'), 326
    UNION ALL SELECT 'paris',
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'WTTJ' AND city = 'Paris'), 1216
    UNION ALL SELECT 'indeed_total',
           (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'Indeed'), 5752
    UNION ALL SELECT 'salper_rempli',
           (SELECT count(*) FROM {{ ref('stg_offres') }}
            WHERE source = 'WTTJ' AND sal_source_period IS NOT NULL AND sal_source_period <> ''), 789
    UNION ALL SELECT 'url_doublons',
           (SELECT count(*) - count(DISTINCT url) FROM {{ ref('stg_offres') }} WHERE url IS NOT NULL), 0
)
SELECT * FROM checks WHERE obtenu <> attendu
