# Data and Storage

This page explains how and where Serenita stores its data.

## Database

*   **Type:** SQLite
*   **Location:** The application uses a local SQLite database file (`serenita.db`) to store all user data, including profiles, subjects, cycles, and session history.
*   **Persistence:** All data is stored locally on your machine. There is no cloud synchronization.

## Resetting Data

To start with a fresh database, you can use the `--reset-db` command-line argument. This is useful for testing or if you encounter data corruption.

```bash
python main.py --reset-db
```

## Seeding Data

For development and testing, you can seed the database with sample data using the `--seed-db` argument. This will populate the application with pre-defined profiles and study materials.

```bash
python main.py --seed-db
```
