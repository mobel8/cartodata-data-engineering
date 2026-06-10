-- Staging : caste + dérive les colonnes propres depuis la source SILVER.
-- exp_bucket : 6 paliers d'expérience hétérogènes -> 4 niveaux lisibles.
-- sal_mid_eur : milieu de fourchette annualisée (pour les agrégats de distribution).
{{ config(materialized='view') }}

SELECT
    offer_id,
    source,
    url,
    apply_url,
    title,
    company,
    city,
    departement,
    is_idf,
    profession,
    kw,
    contract,
    experience,
    CASE
        WHEN experience IS NULL THEN 'Non précisé'
        WHEN regexp_matches(lower(experience), 'less|moins|_6m|6_month|0_|debut|intern') THEN 'Junior (< 3 ans)'
        WHEN regexp_matches(lower(experience), '1_to_2|2_to_3|1_2|2_3|one_to|two_to|under_3') THEN 'Junior (< 3 ans)'
        WHEN regexp_matches(lower(experience), '3_to_5|3_4|3_5|three_to|four') THEN 'Confirmé (3-5 ans)'
        WHEN regexp_matches(lower(experience), '5_|7_|10|more|senior|plus|expert') THEN 'Senior (5+ ans)'
        ELSE 'Autre'
    END AS exp_bucket,
    education,
    remote,
    sal_min_eur,
    sal_max_eur,
    CASE
        WHEN has_salary
        THEN round((coalesce(sal_min_eur, sal_max_eur) + coalesce(sal_max_eur, sal_min_eur)) / 2.0)
    END AS sal_mid_eur,
    sal_source_period,
    has_salary,
    posted_date,
    date_is_precise,
    status,
    is_twin,
    skills
FROM {{ source('silver', 'offres') }}
