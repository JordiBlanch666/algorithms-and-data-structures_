-- =============================================================
-- Reusable views
-- =============================================================
DROP VIEW IF EXISTS v_latest_measurement;
DROP VIEW IF EXISTS v_measurements_bmi;

-- Every measurement with its BMI and the WHO classification
CREATE VIEW v_measurements_bmi AS
SELECT
    p.id                                             AS patient_id,
    p.full_name                                      AS patient,
    a.visit_date,
    m.weight_kg,
    m.height_m,
    ROUND(m.weight_kg / (m.height_m * m.height_m), 1) AS bmi,
    CASE
        WHEN m.weight_kg / (m.height_m * m.height_m) < 18.5 THEN 'Underweight'
        WHEN m.weight_kg / (m.height_m * m.height_m) < 25   THEN 'Normal'
        WHEN m.weight_kg / (m.height_m * m.height_m) < 30   THEN 'Overweight'
        WHEN m.weight_kg / (m.height_m * m.height_m) < 35   THEN 'Obesity I'
        WHEN m.weight_kg / (m.height_m * m.height_m) < 40   THEN 'Obesity II'
        ELSE 'Obesity III'
    END                                              AS who_class,
    m.waist_cm,
    m.body_fat_pct
FROM measurements m
JOIN appointments a ON a.id = m.appointment_id
JOIN patients     p ON p.id = a.patient_id;

-- Each patient's most recent measurement (ROW_NUMBER)
CREATE VIEW v_latest_measurement AS
SELECT patient_id, patient, visit_date, weight_kg, bmi, who_class, waist_cm, body_fat_pct
FROM (
    SELECT v.*,
           ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY visit_date DESC) AS rn
    FROM v_measurements_bmi v
)
WHERE rn = 1;
