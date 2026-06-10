-- Scorecard de complétude par champ (affiché EN CLAIR, pas masqué).
{{ config(materialized='table') }}
SELECT 'Salaire' AS champ, count(*) FILTER (WHERE has_salary) AS rempli, count(*) AS total,
       round(100.0 * count(*) FILTER (WHERE has_salary) / count(*), 1) AS pct FROM {{ ref('fct_offres') }}
UNION ALL SELECT 'Expérience', count(*) FILTER (WHERE experience IS NOT NULL), count(*),
       round(100.0 * count(*) FILTER (WHERE experience IS NOT NULL) / count(*), 1) FROM {{ ref('fct_offres') }}
UNION ALL SELECT 'Diplôme', count(*) FILTER (WHERE education IS NOT NULL), count(*),
       round(100.0 * count(*) FILTER (WHERE education IS NOT NULL) / count(*), 1) FROM {{ ref('fct_offres') }}
UNION ALL SELECT 'Ville', count(*) FILTER (WHERE city IS NOT NULL), count(*),
       round(100.0 * count(*) FILTER (WHERE city IS NOT NULL) / count(*), 1) FROM {{ ref('fct_offres') }}
UNION ALL SELECT 'Métier (profession.fr)', count(*) FILTER (WHERE profession IS NOT NULL), count(*),
       round(100.0 * count(*) FILTER (WHERE profession IS NOT NULL) / count(*), 1) FROM {{ ref('fct_offres') }}
UNION ALL SELECT 'Télétravail', count(*) FILTER (WHERE remote IS NOT NULL), count(*),
       round(100.0 * count(*) FILTER (WHERE remote IS NOT NULL) / count(*), 1) FROM {{ ref('fct_offres') }}
UNION ALL SELECT 'Date précise', count(*) FILTER (WHERE date_is_precise), count(*),
       round(100.0 * count(*) FILTER (WHERE date_is_precise) / count(*), 1) FROM {{ ref('fct_offres') }}
ORDER BY pct DESC
