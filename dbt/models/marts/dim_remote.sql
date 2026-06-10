{{ config(materialized='table') }}
SELECT row_number() OVER (ORDER BY remote) AS remote_key, remote
FROM (SELECT DISTINCT remote FROM {{ ref('int_offres_valides') }} WHERE remote IS NOT NULL)
