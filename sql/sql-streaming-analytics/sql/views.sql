-- =============================================================
-- Reusable views
-- =============================================================
DROP VIEW IF EXISTS v_plays;
DROP VIEW IF EXISTS v_months;

-- Plays enriched with title, genre and % completed
CREATE VIEW v_plays AS
SELECT p.id, p.user_id, u.country, p.played_at, strftime('%Y-%m', p.played_at) AS month,
       t.id AS title_id, t.name AS title, t.kind, g.name AS genre,
       p.minutes_watched, t.duration_min,
       ROUND(100.0 * p.minutes_watched / t.duration_min, 1) AS pct_completed,
       p.device
FROM plays p
JOIN titles t ON t.id = p.title_id
JOIN genres g ON g.id = t.genre_id
JOIN users  u ON u.id = p.user_id;

-- Calendar of months built with a recursive CTE (first to last subscription)
CREATE VIEW v_months AS
WITH RECURSIVE months(month_start) AS (
    SELECT date(MIN(start_date), 'start of month') FROM subscriptions
    UNION ALL
    SELECT date(month_start, '+1 month') FROM months
    WHERE month_start < (SELECT date(MAX(COALESCE(end_date, start_date)), 'start of month')
                         FROM subscriptions)
)
SELECT month_start,
       date(month_start, '+1 month', '-1 day') AS month_end,
       strftime('%Y-%m', month_start)          AS month
FROM months;
