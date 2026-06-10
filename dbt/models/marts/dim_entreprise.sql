{{ config(materialized='table') }}
SELECT row_number() OVER (ORDER BY company) AS entreprise_key, company
FROM (SELECT DISTINCT company FROM {{ ref('int_offres_valides') }} WHERE company IS NOT NULL)
