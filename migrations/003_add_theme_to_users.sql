-- Migration 003: Add theme preference to the users table
-- This allows the application to remember the user's theme choice.

ALTER TABLE users ADD COLUMN theme TEXT NOT NULL DEFAULT 'Dark';