-- Intermédiaire : périmètre des offres RETENUES pour le gold.
--   - Indeed : on retire les twins (doublons inter-sites) -> on garde la version WTTJ.
--   - WTTJ  : on ne garde que les offres effectivement récupérées (status = 200).
-- Cette règle de dédup/validité est la décision clé documentée dans ENGINEERING_NOTES.
{{ config(materialized='view') }}

SELECT *
FROM {{ ref('stg_offres') }}
WHERE (source = 'Indeed' AND NOT is_twin)
   OR (source = 'WTTJ' AND status = 200)
