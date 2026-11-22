-- =============================================================
-- Analytical queries — Nutrition Clinic
-- Each block starts with "-- name:" so run.py can execute it.
-- =============================================================

-- name: current_bmi
-- desc: Each patient's most recent BMI and WHO class (view with ROW_NUMBER)
SELECT patient, visit_date AS last_visit, weight_kg, bmi, who_class
FROM v_latest_measurement
ORDER BY bmi DESC
LIMIT 10;

-- name: bmi_distribution
-- desc: Number and percentage of patients in each BMI class
SELECT who_class,
       COUNT(*)                                            AS patients,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS percentage
FROM v_latest_measurement
GROUP BY who_class
ORDER BY patients DESC;

-- name: weight_progress
-- desc: One patient's weight over time, with change vs. previous visit (LAG)
SELECT patient, visit_date, weight_kg,
       ROUND(weight_kg - LAG(weight_kg) OVER (ORDER BY visit_date), 1)          AS change_kg,
       ROUND(weight_kg - FIRST_VALUE(weight_kg) OVER (ORDER BY visit_date), 1)  AS total_change_kg
FROM v_measurements_bmi
WHERE patient_id = (SELECT patient_id FROM v_measurements_bmi
                    GROUP BY patient_id ORDER BY COUNT(*) DESC, patient_id LIMIT 1)
ORDER BY visit_date;

-- name: top_weight_loss
-- desc: Top 5 patients by % weight lost between their first and latest visit
WITH bounds AS (
    SELECT patient_id, patient,
           FIRST_VALUE(weight_kg) OVER w AS start_weight,
           LAST_VALUE(weight_kg)  OVER w AS latest_weight,
           COUNT(*)               OVER w AS visits
    FROM v_measurements_bmi
    WINDOW w AS (PARTITION BY patient_id ORDER BY visit_date
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)
SELECT DISTINCT patient, visits, start_weight, latest_weight,
       ROUND(100.0 * (start_weight - latest_weight) / start_weight, 1) AS loss_pct
FROM bounds
WHERE visits >= 3
ORDER BY loss_pct DESC
LIMIT 5;

-- name: monthly_revenue
-- desc: Revenue per month with a year-to-date running total (SUM OVER with PARTITION)
SELECT strftime('%Y-%m', visit_date)              AS month,
       COUNT(*)                                   AS visits,
       SUM(fee)                                   AS revenue,
       SUM(SUM(fee)) OVER (PARTITION BY strftime('%Y', visit_date)
                           ORDER BY strftime('%Y-%m', visit_date)) AS ytd_revenue
FROM appointments
GROUP BY month
ORDER BY month;

-- name: inactive_patients
-- desc: Patients with no visit in the last 60 days (to call them back)
WITH today AS (SELECT MAX(visit_date) AS ref_date FROM appointments)
SELECT p.full_name AS patient, p.city, MAX(a.visit_date) AS last_visit,
       CAST(julianday(today.ref_date) - julianday(MAX(a.visit_date)) AS INTEGER) AS days_inactive
FROM patients p
JOIN appointments a ON a.patient_id = p.id
CROSS JOIN today
GROUP BY p.id
HAVING days_inactive > 60
ORDER BY days_inactive DESC
LIMIT 10;

-- name: retention
-- desc: Patients segmented by number of visits
SELECT CASE
           WHEN n = 1 THEN '1 visit (did not return)'
           WHEN n BETWEEN 2 AND 4 THEN '2 to 4 visits'
           ELSE '5 or more visits'
       END AS segment,
       COUNT(*) AS patients
FROM (SELECT patient_id, COUNT(*) AS n FROM appointments GROUP BY patient_id)
GROUP BY segment
ORDER BY MIN(n);

-- name: condition_prevalence
-- desc: Most common conditions and their average current BMI (LEFT JOIN + aggregation)
SELECT c.name                       AS condition,
       COUNT(pc.patient_id)         AS patients,
       ROUND(AVG(l.bmi), 1)         AS avg_bmi
FROM conditions c
LEFT JOIN patient_conditions   pc ON pc.condition_id = c.id
LEFT JOIN v_latest_measurement l  ON l.patient_id = pc.patient_id
GROUP BY c.id
ORDER BY patients DESC;

-- name: results_by_goal
-- desc: Average weight change by nutrition plan goal
WITH change AS (
    SELECT patient_id,
           MAX(CASE WHEN rn_desc = 1 THEN weight_kg END) -
           MAX(CASE WHEN rn_asc  = 1 THEN weight_kg END) AS delta_kg
    FROM (SELECT patient_id, weight_kg,
                 ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY visit_date)      AS rn_asc,
                 ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY visit_date DESC) AS rn_desc
          FROM v_measurements_bmi)
    GROUP BY patient_id
)
SELECT pl.goal, COUNT(*) AS patients, ROUND(AVG(c.delta_kg), 1) AS avg_change_kg
FROM plans pl
JOIN change c ON c.patient_id = pl.patient_id
GROUP BY pl.goal
ORDER BY avg_change_kg;
