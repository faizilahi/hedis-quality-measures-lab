-- Snowflake-shaped continuous enrollment for MY2024 CDC proxy (synthetic).
-- Days in year not covered by enrollment spans must be <= 45.

WITH spans AS (
  SELECT member_id, enroll_start::DATE AS enroll_start, enroll_end::DATE AS enroll_end
  FROM eligibility
),
calendar AS (
  SELECT DATEADD(day, SEQ4(), '2024-01-01'::DATE) AS dt
  FROM TABLE(GENERATOR(ROWCOUNT => 366))
  WHERE dt <= '2024-12-31'::DATE
),
covered AS (
  SELECT c.dt, s.member_id
  FROM calendar c
  JOIN spans s
    ON c.dt BETWEEN GREATEST(s.enroll_start, '2024-01-01'::DATE)
                AND LEAST(s.enroll_end, '2024-12-31'::DATE)
),
gap AS (
  SELECT m.member_id,
         366 - COUNT(DISTINCT c.dt) AS gap_days
  FROM members m
  CROSS JOIN calendar c
  LEFT JOIN covered x ON x.member_id = m.member_id AND x.dt = c.dt
  GROUP BY m.member_id
)
SELECT member_id, gap_days
FROM gap
WHERE gap_days <= 45;
