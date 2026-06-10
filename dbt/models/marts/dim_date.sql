-- dim_date FIABLE = dates WTTJ absolues uniquement (les dates Indeed sont relatives/imprécises).
{{ config(materialized='table') }}
SELECT
    row_number() OVER (ORDER BY d) AS date_key,
    d AS jour,
    strftime(d, '%Y-%m') AS mois,
    year(d) AS annee
FROM (
    SELECT DISTINCT CAST(posted_date AS DATE) AS d
    FROM {{ ref('int_offres_valides') }}
    WHERE date_is_precise AND posted_date IS NOT NULL
)
