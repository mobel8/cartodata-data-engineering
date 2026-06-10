-- Salaire médian par métier — seuil d'effectif (>=8) pour rester statistiquement honnête.
{{ config(materialized='table') }}
SELECT
    profession AS metier,
    count(*) AS n,
    round(median(sal_mid_eur)) AS median,
    round(quantile_cont(sal_mid_eur, 0.25)) AS q1,
    round(quantile_cont(sal_mid_eur, 0.75)) AS q3
FROM {{ ref('fct_offres') }}
WHERE has_salary AND profession IS NOT NULL
GROUP BY 1 HAVING count(*) >= 8
ORDER BY median DESC
