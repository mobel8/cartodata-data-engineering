{{ config(materialized='table') }}
SELECT departement, count(*) AS n
FROM {{ ref('fct_offres') }}
GROUP BY 1 ORDER BY n DESC
