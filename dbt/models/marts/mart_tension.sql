-- Tension : volume d'offres par métier x département (heatmap des opportunités).
{{ config(materialized='table') }}
SELECT profession AS metier, departement, count(*) AS n
FROM {{ ref('fct_offres') }}
WHERE profession IS NOT NULL
  AND departement NOT IN ('Non précisé', 'Hors référentiel')
GROUP BY 1, 2
