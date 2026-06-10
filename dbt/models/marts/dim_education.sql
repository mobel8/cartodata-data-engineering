{{ config(materialized='table') }}
SELECT row_number() OVER (ORDER BY education) AS edu_key, education
FROM (SELECT DISTINCT education FROM {{ ref('int_offres_valides') }} WHERE education IS NOT NULL)
