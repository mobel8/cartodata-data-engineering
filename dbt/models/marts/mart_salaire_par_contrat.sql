-- Distribution salaire par contrat (box-plot) — limité aux contrats à effectif suffisant (>=5).
{{ config(materialized='table') }}
SELECT
    contract AS contrat,
    count(*) AS n,
    round(median(sal_mid_eur)) AS median,
    round(quantile_cont(sal_mid_eur, 0.25)) AS q1,
    round(quantile_cont(sal_mid_eur, 0.75)) AS q3,
    round(min(sal_mid_eur)) AS mini,
    round(max(sal_mid_eur)) AS maxi
FROM {{ ref('fct_offres') }}
WHERE has_salary
GROUP BY 1 HAVING count(*) >= 5
ORDER BY median DESC
