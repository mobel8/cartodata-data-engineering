-- Série temporelle = dates WTTJ fiables uniquement (Indeed exclu : dates relatives).
{{ config(materialized='table') }}
SELECT strftime(CAST(posted_date AS DATE), '%Y-%m') AS mois, count(*) AS n
FROM {{ ref('fct_offres') }}
WHERE date_is_precise AND posted_date IS NOT NULL
GROUP BY 1 ORDER BY 1
