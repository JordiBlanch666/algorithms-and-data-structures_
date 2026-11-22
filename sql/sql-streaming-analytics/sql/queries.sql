-- =============================================================
-- Analytical queries — Streaming Platform
-- Each block starts with "-- name:" so run.py can execute it.
-- =============================================================

-- name: monthly_mrr
-- desc: Monthly recurring revenue (MRR) and active subscribers at the end of each month
SELECT m.month,
       COUNT(s.id)                AS active_subscribers,
       SUM(p.price_mxn)           AS mrr_mxn,
       ROUND(100.0 * (SUM(p.price_mxn) - LAG(SUM(p.price_mxn)) OVER (ORDER BY m.month))
             / LAG(SUM(p.price_mxn)) OVER (ORDER BY m.month), 1) AS growth_pct
FROM v_months m
JOIN subscriptions s ON s.start_date <= m.month_end AND (s.end_date IS NULL OR s.end_date > m.month_end)
JOIN plans p         ON p.id = s.plan_id
GROUP BY m.month
ORDER BY m.month;

-- name: monthly_churn
-- desc: Monthly churn rate: cancellations / subscribers active at the start of the month
WITH active_at_start AS (
    SELECT m.month, COUNT(s.id) AS active
    FROM v_months m
    LEFT JOIN subscriptions s
           ON s.start_date < m.month_start AND (s.end_date IS NULL OR s.end_date >= m.month_start)
    GROUP BY m.month
),
cancellations AS (
    SELECT strftime('%Y-%m', end_date) AS month, COUNT(*) AS cancelled
    FROM subscriptions
    WHERE cancel_reason IS NOT NULL AND cancel_reason <> 'plan change'
    GROUP BY month
)
SELECT a.month, a.active, COALESCE(c.cancelled, 0) AS cancelled,
       ROUND(100.0 * COALESCE(c.cancelled, 0) / NULLIF(a.active, 0), 1) AS churn_pct
FROM active_at_start a
LEFT JOIN cancellations c ON c.month = a.month
WHERE a.active > 0
ORDER BY a.month;

-- name: cancel_reasons
-- desc: Why users leave (plan changes excluded)
SELECT cancel_reason AS reason, COUNT(*) AS cancellations,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM subscriptions
WHERE cancel_reason IS NOT NULL AND cancel_reason <> 'plan change'
GROUP BY reason
ORDER BY cancellations DESC;

-- name: top_titles
-- desc: Top 10 titles by hours watched, grouping each series' episodes together
SELECT CASE WHEN kind = 'episode' THEN SUBSTR(title, 1, INSTR(title, ' - S') - 1)
            ELSE title END                        AS title,
       CASE WHEN kind = 'episode' THEN 'series' ELSE 'movie' END AS format,
       genre,
       COUNT(DISTINCT user_id)                    AS viewers,
       ROUND(SUM(minutes_watched) / 60.0, 1)      AS hours_watched
FROM v_plays
GROUP BY 1, 2, 3
ORDER BY hours_watched DESC
LIMIT 10;

-- name: completion_rate
-- desc: Share of plays watched to the end, by genre (what keeps people hooked?)
SELECT genre,
       COUNT(*)                                                         AS plays,
       ROUND(100.0 * SUM(minutes_watched = duration_min) / COUNT(*), 1) AS completed_pct,
       ROUND(AVG(pct_completed), 1)                                     AS avg_progress_pct
FROM v_plays
GROUP BY genre
ORDER BY completed_pct DESC;

-- name: devices
-- desc: Minutes watched per device and their share
SELECT device,
       SUM(minutes_watched)                                                         AS minutes,
       ROUND(100.0 * SUM(minutes_watched) / SUM(SUM(minutes_watched)) OVER (), 1)   AS share_pct
FROM plays
GROUP BY device
ORDER BY minutes DESC;

-- name: favorite_genre_by_country
-- desc: The most watched genre in each country (ROW_NUMBER per partition)
WITH ranking AS (
    SELECT country, genre, SUM(minutes_watched) AS minutes,
           ROW_NUMBER() OVER (PARTITION BY country ORDER BY SUM(minutes_watched) DESC) AS rn
    FROM v_plays
    GROUP BY country, genre
)
SELECT country, genre AS favorite_genre, ROUND(minutes / 60.0, 1) AS hours
FROM ranking
WHERE rn = 1
ORDER BY hours DESC;

-- name: cohort_retention
-- desc: Retention by signup cohort: % of users still watching 1, 2 and 3 months later
WITH activity AS (
    SELECT DISTINCT p.user_id,
           strftime('%Y-%m', u.signup_date) AS cohort,
           (CAST(strftime('%Y', p.played_at) AS INTEGER) * 12 + CAST(strftime('%m', p.played_at) AS INTEGER))
         - (CAST(strftime('%Y', u.signup_date) AS INTEGER) * 12
            + CAST(strftime('%m', u.signup_date) AS INTEGER)) AS month_n
    FROM plays p
    JOIN users u ON u.id = p.user_id
),
cohort_sizes AS (SELECT strftime('%Y-%m', signup_date) AS cohort, COUNT(*) AS users
                 FROM users GROUP BY cohort)
SELECT c.cohort, c.users,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.month_n = 1 THEN a.user_id END) / c.users) AS month_1_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.month_n = 2 THEN a.user_id END) / c.users) AS month_2_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.month_n = 3 THEN a.user_id END) / c.users) AS month_3_pct
FROM cohort_sizes c
LEFT JOIN activity a ON a.cohort = c.cohort
WHERE c.cohort <= '2026-06'
GROUP BY c.cohort
ORDER BY c.cohort;

-- name: top_rated
-- desc: Highest-rated titles with at least 5 ratings
SELECT t.name AS title, g.name AS genre, COUNT(*) AS ratings, ROUND(AVG(r.stars), 2) AS avg_stars
FROM ratings r
JOIN titles t ON t.id = r.title_id
JOIN genres g ON g.id = t.genre_id
GROUP BY t.id
HAVING COUNT(*) >= 5
ORDER BY avg_stars DESC, ratings DESC
LIMIT 10;

-- name: recommendations
-- desc: Simple recommender for user 1: popular titles in their favorite genre they haven't watched
WITH favorite AS (
    SELECT genre FROM v_plays WHERE user_id = 1
    GROUP BY genre ORDER BY SUM(minutes_watched) DESC LIMIT 1
),
watched AS (SELECT DISTINCT title_id FROM plays WHERE user_id = 1)
SELECT v.title, v.genre, COUNT(DISTINCT v.user_id) AS viewers
FROM v_plays v
WHERE v.genre = (SELECT genre FROM favorite)
  AND v.title_id NOT IN (SELECT title_id FROM watched)
GROUP BY v.title_id
ORDER BY viewers DESC
LIMIT 5;
