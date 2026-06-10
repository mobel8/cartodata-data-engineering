{{ config(materialized='table') }}
SELECT row_number() OVER (ORDER BY exp_bucket) AS exp_key, exp_bucket
FROM (SELECT DISTINCT exp_bucket FROM {{ ref('int_offres_valides') }})
