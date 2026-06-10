{{ config(materialized='table') }}
SELECT profession AS metier, count(*) AS n
FROM {{ ref('fct_offres') }}
WHERE profession IS NOT NULL
GROUP BY 1 ORDER BY n DESC
