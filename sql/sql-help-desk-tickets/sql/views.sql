-- =============================================================
-- Reusable views
-- =============================================================
DROP VIEW IF EXISTS v_tickets_sla;

-- Every ticket with its times in hours and whether it met the SLA
CREATE VIEW v_tickets_sla AS
SELECT
    t.id,
    t.title,
    t.priority,
    t.status,
    c.name                                                        AS category,
    a.full_name                                                   AS agent,
    d.name                                                        AS department,
    t.created_at,
    ROUND((julianday(t.first_response_at) - julianday(t.created_at)) * 24, 1) AS response_hours,
    ROUND((julianday(t.resolved_at)       - julianday(t.created_at)) * 24, 1) AS resolution_hours,
    s.response_hours                                              AS sla_response,
    s.resolution_hours                                            AS sla_resolution,
    CASE
        WHEN t.resolved_at IS NULL THEN NULL
        WHEN (julianday(t.resolved_at) - julianday(t.created_at)) * 24 <= s.resolution_hours THEN 1
        ELSE 0
    END                                                           AS met_sla,
    t.satisfaction
FROM tickets t
JOIN sla         s ON s.priority = t.priority
JOIN categories  c ON c.id = t.category_id
JOIN users       u ON u.id = t.user_id
JOIN departments d ON d.id = u.department_id
LEFT JOIN agents a ON a.id = t.agent_id;
