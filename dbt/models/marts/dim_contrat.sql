{{ config(materialized='table') }}
SELECT row_number() OVER (ORDER BY contract) AS contrat_key, contract
FROM (SELECT DISTINCT contract FROM {{ ref('int_offres_valides') }} WHERE contract IS NOT NULL)
