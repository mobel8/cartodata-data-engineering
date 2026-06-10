-- Top compétences techniques demandées (extraites des titres/snippets).
{{ config(materialized='table') }}
SELECT skill AS competence, count(*) AS n
FROM (SELECT unnest(skills) AS skill FROM {{ ref('fct_offres') }})
WHERE skill IS NOT NULL
GROUP BY 1 ORDER BY n DESC LIMIT 30
