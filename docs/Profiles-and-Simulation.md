# Profiles and Simulation

This page details the use of different user profiles and data simulation for testing purposes.

## Development Profiles

You can run the application with pre-defined user profiles to test different scenarios without affecting your own data.

*   Use the `--user <profile_name>` argument to load a specific profile.
*   Example profiles might include `new_user`, `advanced_user`, etc.

```bash
python main.py --dev --user test_profile_1
```

## Simulation

The `--seed-db` command is the primary way to generate a complete set of simulated data for testing. It creates a realistic set of users, subjects, and study history, which is invaluable for debugging analytics and the tutor engine.
