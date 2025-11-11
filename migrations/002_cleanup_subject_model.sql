-- Migration 0002: Remove the redundant strategic_state_id from the Subjects table.
-- The v20 engine now manages state per-cycle in the cycle_subjects table.

PRAGMA foreign_keys=off;

-- Create a new table with the correct schema
CREATE TABLE subjects_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    soft_delete BOOLEAN DEFAULT 0,
    deleted_at TIMESTAMP
);

-- Copy the data from the old table to the new one, excluding the removed column
INSERT INTO subjects_new (id, name, color, created_at, updated_at, soft_delete, deleted_at)
SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at
FROM subjects;

-- Drop the old table
DROP TABLE subjects;

-- Rename the new table to the original name
ALTER TABLE subjects_new RENAME TO subjects;

PRAGMA foreign_keys=on;