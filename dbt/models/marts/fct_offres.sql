-- Table de faits : 1 ligne = 1 offre retenue, reliée aux dimensions par clés.
{{ config(materialized='table') }}
SELECT
    s.*,
    dc.contrat_key,
    dr.remote_key,
    dm.metier_key,
    dl.lieu_key,
    de.entreprise_key,
    dex.exp_key,
    ded.edu_key
FROM {{ ref('int_offres_valides') }} s
LEFT JOIN {{ ref('dim_contrat') }}    dc  USING (contract)
LEFT JOIN {{ ref('dim_remote') }}     dr  USING (remote)
LEFT JOIN {{ ref('dim_metier') }}     dm  USING (profession)
LEFT JOIN {{ ref('dim_lieu') }}       dl  USING (city)
LEFT JOIN {{ ref('dim_entreprise') }} de  USING (company)
LEFT JOIN {{ ref('dim_experience') }} dex USING (exp_bucket)
LEFT JOIN {{ ref('dim_education') }}  ded USING (education)
