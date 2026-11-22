-- =============================================================
-- Help Desk / Service Desk — Database schema (SQLite)
-- Support tickets, agents, users, categories and SLAs.
-- =============================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS status_history;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS sla;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    full_name     TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
    department_id INTEGER NOT NULL REFERENCES departments(id)
);

CREATE TABLE agents (
    id        INTEGER PRIMARY KEY,
    full_name TEXT    NOT NULL,
    tier      TEXT    NOT NULL CHECK (tier IN ('L1', 'L2', 'L3')),
    active    INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE categories (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Service level agreements per priority (in hours)
CREATE TABLE sla (
    priority         TEXT    PRIMARY KEY CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    response_hours   INTEGER NOT NULL CHECK (response_hours > 0),
    resolution_hours INTEGER NOT NULL CHECK (resolution_hours >= response_hours)
);

CREATE TABLE tickets (
    id                INTEGER PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id),
    agent_id          INTEGER          REFERENCES agents(id),      -- NULL = unassigned
    category_id       INTEGER NOT NULL REFERENCES categories(id),
    priority          TEXT    NOT NULL REFERENCES sla(priority),
    title             TEXT    NOT NULL,
    status            TEXT    NOT NULL DEFAULT 'Open'
                      CHECK (status IN ('Open', 'In progress', 'On hold', 'Resolved', 'Closed')),
    created_at        TEXT    NOT NULL,                            -- 'YYYY-MM-DD HH:MM:SS'
    first_response_at TEXT,
    resolved_at       TEXT,
    satisfaction      INTEGER CHECK (satisfaction BETWEEN 1 AND 5),
    CHECK (first_response_at IS NULL OR first_response_at >= created_at),
    CHECK (resolved_at IS NULL OR resolved_at >= created_at)
);

-- Audit trail: every status change is recorded automatically
CREATE TABLE status_history (
    id          INTEGER PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    old_status  TEXT    NOT NULL,
    new_status  TEXT    NOT NULL,
    changed_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_tickets_status   ON tickets (status);
CREATE INDEX idx_tickets_agent    ON tickets (agent_id, created_at);
CREATE INDEX idx_tickets_category ON tickets (category_id);

-- Audit trigger
CREATE TRIGGER trg_audit_status
AFTER UPDATE OF status ON tickets
FOR EACH ROW
WHEN OLD.status <> NEW.status
BEGIN
    INSERT INTO status_history (ticket_id, old_status, new_status)
    VALUES (NEW.id, OLD.status, NEW.status);
END;

-- When a ticket is marked Resolved without a date, the current time is recorded
CREATE TRIGGER trg_resolution_date
AFTER UPDATE OF status ON tickets
FOR EACH ROW
WHEN NEW.status = 'Resolved' AND NEW.resolved_at IS NULL
BEGIN
    UPDATE tickets SET resolved_at = datetime('now') WHERE id = NEW.id;
END;
