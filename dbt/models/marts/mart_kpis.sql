{{ config(materialized='table') }}
SELECT
    (SELECT count(*) FROM {{ ref('fct_offres') }}) AS n_offres,
    (SELECT count(*) FROM {{ ref('fct_offres') }} WHERE source = 'WTTJ') AS n_wttj,
    (SELECT count(*) FROM {{ ref('fct_offres') }} WHERE source = 'Indeed') AS n_indeed,
    (SELECT count(*) FROM {{ ref('stg_offres') }} WHERE source = 'Indeed' AND is_twin) AS n_twins_dedup,
    (SELECT count(*) FROM {{ ref('fct_offres') }} WHERE has_salary) AS n_salaire,
    (SELECT round(100.0 * count(*) FILTER (WHERE has_salary) / count(*), 1) FROM {{ ref('fct_offres') }}) AS pct_salaire,
    (SELECT count(DISTINCT company) FROM {{ ref('fct_offres') }} WHERE company IS NOT NULL) AS n_entreprises,
    (SELECT count(DISTINCT city) FROM {{ ref('fct_offres') }} WHERE city IS NOT NULL) AS n_villes,
    (SELECT count(*) FROM {{ ref('fct_offres') }} WHERE is_idf) AS n_idf,
    (SELECT round(median(sal_mid_eur)) FROM {{ ref('fct_offres') }} WHERE has_salary) AS salaire_median,
    (SELECT round(quantile_cont(sal_mid_eur, 0.25)) FROM {{ ref('fct_offres') }} WHERE has_salary) AS salaire_q1,
    (SELECT round(quantile_cont(sal_mid_eur, 0.75)) FROM {{ ref('fct_offres') }} WHERE has_salary) AS salaire_q3
