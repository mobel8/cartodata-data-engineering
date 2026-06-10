-- Lieu : commune + département IDF résolu. (lat/lon BAN = backlog géocodage.)
{{ config(materialized='table') }}
SELECT
    row_number() OVER (ORDER BY city) AS lieu_key,
    city,
    any_value(departement) AS departement,
    bool_or(is_idf) AS is_idf
FROM {{ ref('int_offres_valides') }}
WHERE city IS NOT NULL
GROUP BY city
