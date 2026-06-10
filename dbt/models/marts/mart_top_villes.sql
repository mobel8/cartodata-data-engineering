{{ config(materialized='table') }}
SELECT city AS ville, any_value(departement) AS departement, count(*) AS n
FROM {{ ref('fct_offres') }}
WHERE city IS NOT NULL
GROUP BY city ORDER BY n DESC LIMIT 20
