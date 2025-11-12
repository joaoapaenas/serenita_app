# Troubleshooting

This section provides solutions to common issues.

## Application Fails to Start

*   **Check Dependencies:** Ensure all required packages are installed by running `uv pip sync`.
*   **Check Python Version:** Verify you are using a compatible Python version (e.g., 3.10+).

## Data Corruption or Errors

*   **Logs:** Check the application logs located in the `logs` directory for specific error messages.
*   **Database Reset:** If you suspect a data issue, you can reset the database by running the application with the `--reset-db` flag. **Warning:** This will delete all existing user data.

```bash
python main.py --reset-db
```

## Reporting Issues

If you encounter a bug, please [open an issue](https://github.com/your-repo/serenita/issues) on GitHub and include the relevant logs.
