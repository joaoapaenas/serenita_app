```markdown
# Serenita: Your Intelligent Study Planner

Serenita is an intelligent desktop application designed to eliminate the guesswork from preparing for competitive exams. Instead of a static, rigid schedule, Serenita uses a cognitive tutor engine to analyze your performance, understand your personal challenges, and adapt your study plan in real-time.

The goal is to ensure you are always working on the most impactful subject at the right time, maximizing your learning efficiency and helping you achieve your goals with confidence and less stress.

## ✨ Key Features

*   **Intelligent Study Planning (V20 Tutor Engine):** The core of Serenita is its planning algorithm. It analyzes your study history, difficulties, and the relevance of subjects to generate an optimized and personalized daily study plan.
*   **Study Cycle Management:** Create, edit, and manage multiple study cycles. Set daily goals, the duration of study blocks, and customize the subjects included in each cycle.
*   **Performance Analysis:** Track your progress with detailed dashboards. Visualize your performance over time, identify your weak points by topic, and see a summary of your study time.
*   **Flexible Study Sessions:** Start a study session with a real-time stopwatch or manually log sessions you've already completed.
*   **Dynamic Rebalancing:** Based on your performance, Serenita suggests adjustments to the difficulty weights of subjects to optimize how often they appear in your plan.
*   **Subject and Topic Management:** Maintain a master list of all your subjects and organize them into topics and sub-topics for more granular planning.
*   **Customizable Interface:** Choose between light and dark themes for a more comfortable study experience.

## 🚀 Getting Started

To run the project, you will need Python 3.10 or higher installed.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/serenita.git
    cd serenita
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

With the virtual environment activated, run the following command in the project root:

```bash
python main.py
```

The first time you run it, a welcome wizard will guide you through creating your user profile.

### Development Mode

To populate the application with sample data for development and testing, you can use the following command-line arguments:

```bash
python main.py --dev --user alex
```

This will start the application with a pre-defined user profile named "alex", including study cycles, performance history, and subjects.

## 🛠️ Technologies Used

*   **Language:** Python
*   **GUI:** PyQt6
*   **Database:** SQLite
*   **Icons:** FontAwesome6 (via `qtawesome`)
*   **Charts:** Qt Charts
*   **ORM/DB Connection:** SQLAlchemy (for seeding and migrations)

## 📂 Project Structure

The project is organized with a modular architecture to separate concerns and facilitate maintenance.

```
├── app/
│   ├── common/         # Reusable widgets and components (subject editor, etc.)
│   ├── core/           # Main business logic, tutor engine, database
│   ├── features/       # UI feature modules (main screen, history, etc.)
│   ├── models/         # Dataclasses representing database entities
│   ├── services/       # Abstraction layer for database interactions
│   └── assets/         # Resources like fonts, styles (QSS), and SQL
├── migrations/         # Database migration scripts
└── main.py             # Application entry point
```

## 🔍 Code Quality and Refactoring Analysis

This project was developed with a focus on internal software quality to ensure it is clean, efficient, and easy to maintain. An analysis was conducted to identify "code smells" and refactoring opportunities based on software engineering principles.

### Single Responsibility Principle (SRP)

*   **Observation:** The `MainWindowController` class centralizes many responsibilities, acting as an orchestrator for multiple sub-components (`Navigator`, `SessionManager`, `PlanManager`).
*   **Improvement Action:** A delegation pattern was adopted, where `MainWindowController` initializes the managers, but specific logic is contained within each manager. For example, `PlanManager` is fully responsible for generating and caching the study plan, and `SessionManager` manages the lifecycle of a study session. This improves cohesion and clarity.

### Cohesion and Coupling

*   **Observation:** Coupling between UI components and business logic can become a challenge. Passing the entire main window instance to child classes is a practice that was avoided.
*   **Improvement Action:** The application makes extensive use of Qt's **signals and slots** mechanism for decoupled communication. A central signals hub (`app_signals`) is used to broadcast global events, such as `data_changed`, allowing different parts of the UI to react to changes without direct knowledge of each other.

### Code Duplication (DRY - Don't Repeat Yourself)

*   **Observation:** Creating standardized widgets (buttons, dialogs) and configuring tables can lead to code duplication.
*   **Improvement Action:** Reusable components like `ActionCardWidget` and `StandardPageView` were created to encapsulate common UI logic. Additionally, a `ViewControllerFactory` is used to centralize the creation and wiring of all major views and their controllers, ensuring a consistent pattern.

### Readability and "Magic Numbers/Strings"

*   **Observation:** Using literal strings and numbers directly in the code (e.g., for icon names, colors, or column indices) can make maintenance difficult.
*   **Improvement Action:**
    *   **Constants:** Values like margins and spacing are centralized in `app/core/constants.py`.
    *   **Icon Manager:** All icon names are mapped in `app/core/icon_manager.py`, allowing for easy updates and ensuring consistency.
    *   **Styles (QSS):** Application themes are loaded from external `.qss` files, completely separating styling from the code logic.
```
