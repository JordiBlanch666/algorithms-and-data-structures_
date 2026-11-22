-- =============================================================
-- Streaming Platform — Database schema (SQLite)
-- Users, plans, subscriptions, catalog, plays and ratings.
-- =============================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS plays;
DROP TABLE IF EXISTS titles;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS plans;

CREATE TABLE plans (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE,
    price_mxn   REAL    NOT NULL CHECK (price_mxn > 0),
    screens     INTEGER NOT NULL CHECK (screens BETWEEN 1 AND 4),
    quality     TEXT    NOT NULL CHECK (quality IN ('HD', 'Full HD', '4K'))
);

CREATE TABLE users (
    id          INTEGER PRIMARY KEY,
    email       TEXT    NOT NULL UNIQUE,
    country     TEXT    NOT NULL,
    signup_date TEXT    NOT NULL
);

CREATE TABLE subscriptions (
    id            INTEGER PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id       INTEGER NOT NULL REFERENCES plans(id),
    start_date    TEXT    NOT NULL,
    end_date      TEXT,                         -- NULL = active subscription
    cancel_reason TEXT CHECK (cancel_reason IN
                      ('price', 'not enough content', 'technical issues', 'plan change', 'other')),
    CHECK (end_date IS NULL OR end_date >= start_date),
    CHECK ((end_date IS NULL) = (cancel_reason IS NULL))
);

-- Partial unique index: a user can only have ONE active subscription
CREATE UNIQUE INDEX ux_one_active_subscription
    ON subscriptions (user_id) WHERE end_date IS NULL;

CREATE TABLE genres (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE titles (
    id           INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL,
    kind         TEXT    NOT NULL CHECK (kind IN ('movie', 'episode')),
    genre_id     INTEGER NOT NULL REFERENCES genres(id),
    duration_min INTEGER NOT NULL CHECK (duration_min > 0),
    release_date TEXT    NOT NULL
);

CREATE TABLE plays (
    id              INTEGER PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title_id        INTEGER NOT NULL REFERENCES titles(id),
    played_at       TEXT    NOT NULL,
    minutes_watched INTEGER NOT NULL CHECK (minutes_watched > 0),
    device          TEXT    NOT NULL CHECK (device IN ('TV', 'Phone', 'Computer', 'Tablet'))
);

CREATE TABLE ratings (
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title_id INTEGER NOT NULL REFERENCES titles(id),
    stars    INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    PRIMARY KEY (user_id, title_id)
);

CREATE INDEX idx_plays_user  ON plays (user_id, played_at);
CREATE INDEX idx_plays_title ON plays (title_id);

-- Minutes watched cannot exceed the title's duration
CREATE TRIGGER trg_valid_minutes
BEFORE INSERT ON plays
FOR EACH ROW
WHEN NEW.minutes_watched > (SELECT duration_min FROM titles WHERE id = NEW.title_id)
BEGIN
    SELECT RAISE(ABORT, 'minutes_watched exceeds the title duration');
END;
