{{ config(materialized='table') }}
SELECT remote, count(*) AS n
FROM {{ ref('fct_offres') }}
WHERE remote IS NOT NULL
GROUP BY 1 ORDER BY n DESC
