# Pytest-Qt Integration Test Plan

This document outlines a plan for creating a suite of integration tests for the Serenita application using the `pytest-qt` framework. The goal is to simulate user workflows from end-to-end, ensuring all components work together as expected.

## 1. Testing Strategy

The integration tests will focus on user-centric scenarios. We will use the `qtbot` fixture extensively to interact with the UI, trigger events, and wait for asynchronous operations to complete. The tests will be organized by application feature.

We will leverage advanced `pytest-qt` features documented in this directory:
*   **`qtbot.waitSignal`**: To pause tests until a specific signal (like `finished` or `dataChanged`) is emitted, which is crucial for testing threaded operations or long-running tasks.
*   **`qtbot.waitUntil`**: To wait for arbitrary UI conditions to be met, such as a widget becoming visible or a label's text changing. This helps prevent flaky tests caused by the asynchronous nature of GUI updates.
*   **`qtlog`**: To capture and inspect Qt's logging output (`qWarning`, `qCritical`). This allows us to fail tests if unexpected errors or warnings occur in the application's backend during UI operations.
*   **Fixtures**: To create a consistent and clean state for each test, such as creating mock user profiles, pre-populating the database with test data, or launching specific windows.

## 2. Test Suites

### 2.1. Onboarding and User Profile

**Objective:** Ensure a new user can create a profile and that existing users can log in.

*   **Test Case 1.1: First Launch and Profile Creation**
    1.  Launch the application with a clean database.
    2.  **`waitUntil`** the `OnboardingView` is visible.
    3.  Enter user details into the input fields.
    4.  Click the "Create Profile" button.
    5.  **`waitSignal`** for a `profileCreated` signal from the controller.
    6.  **`waitUntil`** the main window (`MainWindow`) is visible.
    7.  Assert that the database now contains the new user.

*   **Test Case 1.2: Existing User Login**
    1.  Use a fixture to pre-populate the database with a user.
    2.  Launch the application.
    3.  **`waitUntil`** the `WelcomeView` is visible, showing the existing user's profile.
    4.  Click the user profile button.
    5.  **`waitUntil`** the `MainWindow` is visible.

### 2.2. Cycle and Subject Management

**Objective:** Verify that users can create, edit, and manage their study cycles and subjects.

*   **Test Case 2.1: Create a New Study Cycle**
    1.  Start from the `MainWindow`.
    2.  Navigate to the "Cycles" section.
    3.  Click the "New Cycle" button.
    4.  **`waitUntil`** the `CycleEditorView` is visible.
    5.  Fill in the cycle details and add a few subjects with different weights.
    6.  Click "Save".
    7.  **`waitSignal`** for the `cycleSaved` signal.
    8.  Assert that the new cycle appears in the cycle list view.

### 2.3. Study Session Workflow

**Objective:** Test the entire process of starting, completing, and saving a study session.

*   **Test Case 3.1: Complete a Study Session**
    1.  Use a fixture to set up a cycle with subjects in the study queue.
    2.  From the `MainWindow`, click "Start Studying".
    3.  **`waitUntil`** the `StudySessionView` is active.
    4.  Simulate the timer finishing or click the "Finish Session" button.
    5.  **`waitSignal`** for the `sessionCompleted` signal, which should carry the session data.
    6.  Use `check_params_cb` with the signal to verify the session data (e.g., duration, subject) is correct.
    7.  Assert that the study queue is updated.

### 2.4. Analytics and Performance Review

**Objective:** Ensure that completed sessions are correctly reflected in the performance dashboard.

*   **Test Case 4.1: Verify Analytics Update**
    1.  Run the "Complete a Study Session" test (Test Case 3.1).
    2.  Navigate to the "Analytics" or "Performance" view.
    3.  **`waitUntil`** the chart or graph widgets have been updated. This is a good use case for `qtbot.waitUntil` with a callback that checks if a chart has data points.
    4.  Assert that the new session data is correctly visualized.

### 2.5. Application Health

**Objective:** Monitor the application for unexpected errors during UI tests.

*   **Test Case 5.1: No Critical Errors During Workflow**
    1.  Inject the `qtlog` fixture into a complex test (e.g., creating a cycle and running a session).
    2.  Configure `pytest.ini` or use a mark (`@pytest.mark.qt_log_level_fail("WARNING")`) to automatically fail the test if any `qWarning` or `qCritical` messages are emitted.
    3.  Run the test workflow.
    4.  The test should pass only if no captured log messages meet the failure criteria, ensuring the UI operations did not trigger underlying Qt errors.
