-- ============================================================
--  TaskFlow — PostgreSQL Schema
--  Run: psql -U postgres -f schema.sql
-- ============================================================

-- Create database (run separately as superuser if needed)
-- CREATE DATABASE task_manager_db;

\c task_manager_db;

-- ── USERS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(80)  UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── TASKS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    priority    VARCHAR(20)  DEFAULT 'medium'  CHECK (priority IN ('low','medium','high')),
    status      VARCHAR(20)  DEFAULT 'pending' CHECK (status  IN ('pending','in_progress','completed')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast per-user lookups
CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
