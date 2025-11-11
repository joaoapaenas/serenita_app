# Running Serenita in Development Mode

This guide explains how to run the Serenita application in development mode using seeded user profiles. This is useful for testing features with pre-populated data without affecting your main application database.

## Prerequisites

Before you begin, ensure you have generated some user profiles. You can do this using the profile generator script:

```bash
python -m app.core.simulation.generator --count 3
```

This will create JSON profile files (e.g., `ana_1.json`, `bruno_2.json`) in the `tests/fixtures/profiles/` directory.

## Running in Development Mode

To run the application in development mode with a specific user profile, use the `--dev` and `--user` flags with `main.py`:

```bash
python main.py --dev --user <profile_name>
```

Replace `<profile_name>` with the name of a JSON profile file (without the `.json` extension) located in `tests/fixtures/profiles/`.

**Example:**

To run the application with the `ana_1` profile:

```bash
python main.py --dev --user ana_1
```

### What happens when you run in development mode?

When you use the `--dev` and `--user` flags:

1.  **Dedicated Database**: A new SQLite database file will be created in the `data/` directory (e.g., `data/ana_1.db`). This database is isolated from your main application database (`study_app.db`).
2.  **Profile Seeding**: The specified user profile (e.g., `ana_1.json`) will be used to populate this new database with a user, exam, active study cycle, subjects, and session history.
3.  **Fresh Start**: Each time you run the command with `--dev` and `--user`, the corresponding development database file is deleted (if it exists) and recreated from scratch. This ensures you always start with a clean, consistent state for your development session.
4.  **No Persistence**: Any changes you make within the application's UI while in development mode (e.g., completing tasks, adding new subjects) will **not** be saved across different runs of the `--dev` command, as the database is reset each time.

## Running in Normal Mode

To run the application using your regular, persistent database, simply omit the `--dev` and `--user` flags:

```bash
python main.py
```