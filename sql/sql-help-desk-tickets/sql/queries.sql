-- =============================================================
-- Analytical queries — Help Desk / Service Desk
-- Each block starts with "-- name:" so run.py can execute it.
-- =============================================================

-- name: status_summary
-- desc: Number of tickets in each status and their share of the total
SELECT status,
       COUNT(*)                                           AS tickets,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM tickets
GROUP BY status
ORDER BY tickets DESC;

-- name: sla_compliance
-- desc: Resolution SLA compliance % by priority
SELECT priority,
       sla_resolution                       AS sla_hours,
       COUNT(*)                             AS resolved,
       ROUND(AVG(resolution_hours), 1)      AS avg_hours,
       ROUND(100.0 * AVG(met_sla), 1)       AS compliance_pct
FROM v_tickets_sla
WHERE met_sla IS NOT NULL
GROUP BY priority
ORDER BY sla_resolution;

-- name: agent_performance
-- desc: Agents ranked by tickets resolved, MTTR, SLA compliance and CSAT (RANK)
SELECT agent,
       COUNT(*)                                   AS resolved,
       ROUND(AVG(resolution_hours), 1)            AS mttr_hours,
       ROUND(100.0 * AVG(met_sla), 1)             AS sla_pct,
       ROUND(AVG(satisfaction), 2)                AS csat,
       RANK() OVER (ORDER BY AVG(met_sla) DESC)   AS sla_rank
FROM v_tickets_sla
WHERE met_sla IS NOT NULL
GROUP BY agent
ORDER BY sla_rank;

-- name: current_backlog
-- desc: Pending tickets and how many days they have been open; unassigned ones first
WITH now AS (SELECT MAX(created_at) AS ref_time FROM tickets)
SELECT t.id, t.title, t.priority, t.status,
       COALESCE(a.full_name, '⚠ Unassigned')                        AS agent,
       ROUND(julianday(now.ref_time) - julianday(t.created_at), 1)  AS days_open
FROM tickets t
LEFT JOIN agents a ON a.id = t.agent_id
CROSS JOIN now
WHERE t.status IN ('Open', 'In progress', 'On hold')
ORDER BY (t.agent_id IS NOT NULL), days_open DESC;

-- name: top_categories
-- desc: Categories with the most tickets and their average resolution time
SELECT category,
       COUNT(*)                          AS tickets,
       ROUND(AVG(resolution_hours), 1)   AS avg_hours,
       ROUND(100.0 * AVG(met_sla), 1)    AS sla_pct
FROM v_tickets_sla
GROUP BY category
ORDER BY tickets DESC;

-- name: top_issues
-- desc: The 5 most repeated issues: candidates for automation or self-service docs
SELECT title, COUNT(*) AS occurrences,
       DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS position
FROM tickets
GROUP BY title
ORDER BY occurrences DESC
LIMIT 5;

-- name: repeat_users
-- desc: Users with the most tickets (may need training or new equipment)
SELECT u.full_name AS user, d.name AS department, COUNT(*) AS tickets,
       GROUP_CONCAT(DISTINCT c.name) AS categories
FROM tickets t
JOIN users u       ON u.id = t.user_id
JOIN departments d ON d.id = u.department_id
JOIN categories c  ON c.id = t.category_id
GROUP BY u.id
HAVING COUNT(*) >= 15
ORDER BY tickets DESC;

-- name: monthly_trend
-- desc: Tickets created per month, change vs. previous month (LAG) and 3-month moving average
WITH per_month AS (
    SELECT strftime('%Y-%m', created_at) AS month, COUNT(*) AS tickets
    FROM tickets GROUP BY month
)
SELECT month, tickets,
       tickets - LAG(tickets) OVER (ORDER BY month) AS change,
       ROUND(AVG(tickets) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1)
           AS moving_avg_3m
FROM per_month
ORDER BY month;

-- name: peak_hours
-- desc: Tickets by hour of the day (for shift planning)
SELECT CAST(strftime('%H', created_at) AS INTEGER) AS hour,
       COUNT(*)                                   AS tickets,
       SUBSTR('████████████████████████████████████████', 1, COUNT(*) / 3) AS chart
FROM tickets
GROUP BY hour
ORDER BY hour;
