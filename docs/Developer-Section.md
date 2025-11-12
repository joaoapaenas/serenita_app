# Developer Section

This area is for developers contributing to Serenita.

## Codebase Overview

*   **`main.py`**: Application entry point.
*   **`app/`**: Core application source code.
    *   **`core/`**: Business logic, database interaction, and the tutor engine.
    *   **`models/`**: SQLAlchemy data models.
    *   **`features/`**: UI views and controllers for different application features.
    *   **`services/`**: Service layer abstracting database operations.
*   **`tests/`**: Pytest unit and integration tests.
*   **`migrations/`**: Alembic database migration scripts.

## Architecture

Serenita uses a layered architecture:

1.  **View/Controller (`features/`)**: Manages the user interface and user input.
2.  **Service Layer (`services/`)**: Provides an API for the UI to interact with application data.
3.  **Business Logic (`core/`)**: Contains the core algorithms and rules of the application (e.g., the tutor engine).
4.  **Data Access (`models/`, `core/database.py`)**: Defines the database schema and handles all database interactions.
