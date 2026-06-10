-- Métier = profession.fr (taxonomie WTTJ, canonisée FR). Indeed n'a pas ce champ.
{{ config(materialized='table') }}
SELECT row_number() OVER (ORDER BY profession) AS metier_key, profession
FROM (SELECT DISTINCT profession FROM {{ ref('int_offres_valides') }} WHERE profession IS NOT NULL)
