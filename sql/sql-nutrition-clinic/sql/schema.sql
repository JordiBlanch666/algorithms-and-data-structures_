-- =============================================================
-- Nutrition Clinic — Database schema (SQLite)
-- Normalized model (3NF) for patients, appointments,
-- body measurements, medical conditions and nutrition plans.
-- =============================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS plans;
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patient_conditions;
DROP TABLE IF EXISTS conditions;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    id          INTEGER PRIMARY KEY,
    full_name   TEXT    NOT NULL,
    sex         TEXT    NOT NULL CHECK (sex IN ('F', 'M')),
    birth_date  TEXT    NOT NULL,          -- ISO format: YYYY-MM-DD
    city        TEXT    NOT NULL,
    signup_date TEXT    NOT NULL
);

CREATE TABLE conditions (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Many-to-many: a patient can have several conditions
CREATE TABLE patient_conditions (
    patient_id   INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    condition_id INTEGER NOT NULL REFERENCES conditions(id),
    PRIMARY KEY (patient_id, condition_id)
);

CREATE TABLE appointments (
    id         INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_date TEXT    NOT NULL,
    visit_type TEXT    NOT NULL CHECK (visit_type IN ('first visit', 'follow-up')),
    fee        REAL    NOT NULL CHECK (fee >= 0)
);

-- One measurement per appointment (1:1)
CREATE TABLE measurements (
    id             INTEGER PRIMARY KEY,
    appointment_id INTEGER NOT NULL UNIQUE REFERENCES appointments(id) ON DELETE CASCADE,
    weight_kg      REAL    NOT NULL CHECK (weight_kg BETWEEN 30 AND 300),
    height_m       REAL    NOT NULL CHECK (height_m BETWEEN 1.20 AND 2.20),
    waist_cm       REAL             CHECK (waist_cm BETWEEN 40 AND 200),
    body_fat_pct   REAL             CHECK (body_fat_pct BETWEEN 3 AND 70)
);

CREATE TABLE plans (
    id              INTEGER PRIMARY KEY,
    patient_id      INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    start_date      TEXT    NOT NULL,
    goal            TEXT    NOT NULL CHECK (goal IN
                      ('weight loss', 'glucose control', 'muscle gain', 'maintenance')),
    target_calories INTEGER NOT NULL CHECK (target_calories BETWEEN 1000 AND 4000)
);

-- Indexes for the most frequent lookups
CREATE INDEX idx_appointments_patient_date ON appointments (patient_id, visit_date);
CREATE INDEX idx_plans_patient             ON plans (patient_id);

-- Business rule: an appointment cannot be earlier than the patient's signup date
CREATE TRIGGER trg_valid_visit_date
BEFORE INSERT ON appointments
FOR EACH ROW
WHEN NEW.visit_date < (SELECT signup_date FROM patients WHERE id = NEW.patient_id)
BEGIN
    SELECT RAISE(ABORT, 'Appointment date is earlier than the patient signup date');
END;
