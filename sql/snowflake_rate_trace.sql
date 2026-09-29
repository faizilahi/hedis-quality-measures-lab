-- Trace a CDC rate contribution back to source row ids (Snowflake-shaped).
-- Bind :member_id e.g. 'M-000417'

WITH denom AS (
  SELECT member_id FROM member_level_denom WHERE member_id = :member_id
),
claim_hit AS (
  SELECT c.member_id, c.claim_id AS source_row_id, 'claims' AS source,
         c.procedure_code || ' on ' || c.service_date::STRING AS detail
  FROM claims c
  JOIN denom d ON d.member_id = c.member_id
  WHERE c.service_date BETWEEN '2024-01-01' AND '2024-12-31'
    AND c.procedure_code IN ('3074F','3075F','3078F','3079F')
  QUALIFY ROW_NUMBER() OVER (PARTITION BY c.member_id ORDER BY c.service_date) = 1
),
lab_hit AS (
  SELECT l.member_id, l.lab_id AS source_row_id, 'lab' AS source,
         'LOINC ' || l.loinc || ' SYS ' || l.systolic || '/DIA ' || l.diastolic AS detail
  FROM supplemental_lab l
  JOIN denom d ON d.member_id = l.member_id
  WHERE l.result_date BETWEEN '2024-01-01' AND '2024-12-31'
    AND l.loinc IN ('85354-9','8480-6','8462-4')
    AND l.systolic < 140 AND l.diastolic < 90
  QUALIFY ROW_NUMBER() OVER (PARTITION BY l.member_id ORDER BY l.result_date) = 1
)
SELECT
  d.member_id,
  COALESCE(c.source, l.source) AS numerator_source,
  COALESCE(c.source_row_id, l.source_row_id) AS source_row_id,
  COALESCE(c.detail, l.detail) AS detail
FROM denom d
LEFT JOIN claim_hit c ON c.member_id = d.member_id
LEFT JOIN lab_hit l ON l.member_id = d.member_id
WHERE c.member_id IS NOT NULL OR l.member_id IS NOT NULL;
