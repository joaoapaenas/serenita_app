# Serena App Test Plan

## Objective

To create a robust, automated testing framework for the Serena desktop app. This system will simulate diverse user behavior patterns by programmatically generating and populating isolated SQLite databases. It will enable fast, reproducible, and deterministic testing of application logic, particularly analytics, data services, and the cognitive tutor engine.

---

## Phase 1 — Profile Definition

We will define synthetic user profiles using a structured JSON format that directly mirrors the application's core data hierarchy (`User` \-\> `Exam` \-\> `Cycle` \-\> `Subjects` & `Sessions`). This ensures that our test data is valid and accurately represents the state the application logic expects.

**Location:** All profile files will be stored in `tests/fixtures/profiles/`.

### Refined JSON Profile Structure

Each JSON file defines a complete, self-contained user scenario.

**File:** `tests/fixtures/profiles/alex.json`

{

  "user": {

    "name": "alex",

    "study\_level": "Intermediate"

  },

  "exam": {

    "name": "CNU \- Bloco 4",

    "area": "Trabalho e Previdência"

  },

  "cycle": {

    "name": "Junho \- Reta Final",

    "is\_active": true,

    "daily\_goal\_blocks": 4,

    "subjects": \[

      {

        "name": "Direito Constitucional",

        "relevance\_weight": 5,

        "volume\_weight": 4,

        "difficulty\_weight": 2,

        "current\_strategic\_state": "MAINTAIN"

      },

      {

        "name": "Administração Financeira e Orçamentária (AFO)",

        "relevance\_weight": 4,

        "volume\_weight": 5,

        "difficulty\_weight": 4,

        "current\_strategic\_state": "DEEP\_WORK"

      }

    \],

    "sessions": \[

      {

        "subject\_name": "Direito Constitucional",

        "start\_time": "2024-05-15T20:00:00Z",

        "liquid\_duration\_sec": 6000,

        "questions": \[

          {"topic\_name": "poder\_judiciario", "is\_correct": true},

          {"topic\_name": "poder\_judiciario", "is\_correct": true},

          {"topic\_name": "poder\_judiciario", "is\_correct": false}

        \]

      },

      {

        "subject\_name": "Administração Financeira e Orçamentária (AFO)",

        "start\_time": "2024-05-16T08:00:00Z",

        "liquid\_duration\_sec": 6300,

        "questions": \[

          {"topic\_name": "receita\_publica", "is\_correct": true},

          {"topic\_name": "receita\_publica", "is\_correct": false},

          {"topic\_name": "receita\_publica", "is\_correct": true}

        \]

      }

    \]

  }

}

---

## Phase 2 — Seeder Engine

The Seeder Engine is a Python module responsible for parsing a JSON profile and populating a fresh SQLite database. It will be located in a new, non-conflicting directory to distinguish it from the application's initial data seeder.

**File:** `app/core/simulation/seeder.py`

**Purpose:** Load a profile, build a complete and valid SQLite database snapshot by inserting all required hierarchical data, and return a database engine for use in tests.

**Steps:**

1. Start from a clean, migrated schema.
2. Read the refined JSON profile.
3. Insert the `user` record.
4. Insert the `exam` record, linked to the user.
5. Insert the `cycle` record, linked to the exam.
6. For each subject in the profile, find its ID in the master `subjects` table (creating it if necessary for the test) and insert a record into the `cycle_subjects` junction table with the specified weights and state.
7. For each session, insert a record into `study_sessions`, linking it to the user, cycle, and subject.
8. For each question in a session, insert a corresponding record into `question_performance`.
9. Return the SQLAlchemy `engine` for the test harness to use.

### Seeder Entry Point (`app/core/simulation/seeder.py`)

This implementation uses direct SQL statements via an SQLAlchemy `engine` connection, aligning with the application's existing data access patterns in the service layer.

import json

import random

import os

from datetime import datetime, timedelta, timezone

from sqlalchemy import create\_engine, text

from app.core.migrations import run\_migrations\_on\_connection

\# Define the base path relative to this file's location

BASE\_PATH \= os.path.abspath(os.path.join(os.path.dirname(\_\_file\_\_), "..", "..", ".."))

def seed\_profile(profile\_path: str, target: str \= ":memory:"):

    """Seeds a complete user profile from a JSON file into a SQLite database."""

    engine \= create\_engine(f"sqlite:///{target}")

    \# Best Practice: Run actual migrations on the test database to ensure schema parity.

    with engine.connect() as conn:

        run\_migrations\_on\_connection(conn, BASE\_PATH)

    with open(profile\_path) as f:

        profile \= json.load(f)

    with engine.begin() as conn:

        \# 1\. Create User

        user\_res \= conn.execute(text("INSERT INTO users (name, study\_level) VALUES (:name, :level) RETURNING id"),

                                {"name": profile\['user'\]\['name'\], "level": profile\['user'\]\['study\_level'\]})

        user\_id \= user\_res.scalar\_one()

        \# 2\. Create Exam

        exam\_res \= conn.execute(text("INSERT INTO exams (user\_id, name, area) VALUES (:uid, :name, :area) RETURNING id"),

                                {"uid": user\_id, "name": profile\['exam'\]\['name'\], "area": profile\['exam'\]\['area'\]})

        exam\_id \= exam\_res.scalar\_one()

        \# 3\. Create Cycle

        cycle\_res \= conn.execute(text("INSERT INTO study\_cycles (exam\_id, name, is\_active, daily\_goal\_blocks) VALUES (:eid, :name, :active, :goal) RETURNING id"),

                                 {"eid": exam\_id, "name": profile\['cycle'\]\['name'\], "active": profile\['cycle'\]\['is\_active'\], "goal": profile\['cycle'\]\['daily\_goal\_blocks'\]})

        cycle\_id \= cycle\_res.scalar\_one()

        \# 4\. Create Subjects and CycleSubjects

        subject\_map \= {} \# Cache subject name to master subject ID

        for s\_prof in profile\['cycle'\]\['subjects'\]:

            \# Get master subject ID (assumes subjects are pre-seeded by migrations)

            sub\_res \= conn.execute(text("SELECT id FROM subjects WHERE name \= :name"), {"name": s\_prof\['name'\]}).scalar\_one\_or\_none()

            if not sub\_res:

                \# If a subject isn't in the initial seed, create it for the test.

                sub\_res \= conn.execute(text("INSERT INTO subjects (name) VALUES (:name) RETURNING id"), {"name": s\_prof\['name'\]}).scalar\_one()

            subject\_id \= sub\_res

            subject\_map\[s\_prof\['name'\]\] \= subject\_id



            \# Insert into the junction table

            conn.execute(text("""

                INSERT INTO cycle\_subjects (cycle\_id, subject\_id, relevance\_weight, volume\_weight, difficulty\_weight, current\_strategic\_state)

                VALUES (:cid, :sid, :r, :v, :d, :state)

            """), {"cid": cycle\_id, "sid": subject\_id, "r": s\_prof\['relevance\_weight'\], "v": s\_prof\['volume\_weight'\], "d": s\_prof\['difficulty\_weight'\], "state": s\_prof\['current\_strategic\_state'\]})



        \# 5\. Create Sessions and QuestionPerformance

        for sess\_prof in profile\['cycle'\]\['sessions'\]:

            subject\_id \= subject\_map\[sess\_prof\['subject\_name'\]\]

            start\_time \= datetime.fromisoformat(sess\_prof\['start\_time'\])

            end\_time \= start\_time \+ timedelta(seconds=sess\_prof\['liquid\_duration\_sec'\])



            sess\_res \= conn.execute(text("""

                INSERT INTO study\_sessions (user\_id, cycle\_id, subject\_id, start\_time, end\_time, liquid\_duration\_sec)

                VALUES (:uid, :cid, :sid, :start, :end, :duration) RETURNING id

            """), {"uid": user\_id, "cid": cycle\_id, "sid": subject\_id, "start": start\_time.isoformat(), "end": end\_time.isoformat(), "duration": sess\_prof\['liquid\_duration\_sec'\]})

            session\_id \= sess\_res.scalar\_one()

            for q\_prof in sess\_prof\['questions'\]:

                conn.execute(text("""

                    INSERT INTO question\_performance (session\_id, topic\_name, difficulty\_level, is\_correct)

                    VALUES (:sid, :topic, :diff, :correct)

                """), {"sid": session\_id, "topic": q\_prof\['topic\_name'\], "diff": random.randint(1, 5), "correct": q\_prof\['is\_correct'\]})

    return engine

---

## Phase 3 — In-Memory Testing Harness (Pytest)

We will use a `pytest` fixture to automatically create a fresh, seeded, in-memory database for each test function. This ensures complete test isolation and high performance.

**File:** `tests/conftest.py`

import pytest

from app.core.simulation.seeder import seed\_profile

@pytest.fixture

def seeded\_engine(request):

    """

    A pytest fixture that creates a fresh, in-memory SQLite database and

    populates it with data from a user profile JSON file.



    The fixture is parametrized indirectly via pytest\_generate\_tests, allowing

    tests to run against multiple user profiles automatically.



    Yields:

        tuple: A tuple containing (profile\_name, sqlalchemy.engine.Engine).

    """

    profile\_name \= request.param

    profile\_path \= f"tests/fixtures/profiles/{profile\_name}.json"



    engine \= seed\_profile(profile\_path, target=":memory:")



    yield profile\_name, engine



    engine.dispose()

---

## Phase 4 — Test Integration

With the harness in place, tests can be written to validate specific business logic by requesting the `seeded_engine` fixture.

#### Example Test (`tests/test_analytics.py`)

This test validates that the `SqliteAnalyticsService` correctly calculates daily performance statistics based on the data seeded from a known JSON profile.

\# tests/test\_analytics.py

import json

from app.services.analytics\_service import SqliteAnalyticsService

from app.core.database import SqliteConnectionFactory

def test\_daily\_performance\_calculation(seeded\_engine):

    """

    Given a seeded database engine from a known user profile,

    When the analytics service calculates daily performance,

    Then the results should match the aggregates from the source profile.

    """

    profile\_name, engine \= seeded\_engine

    \# 1\. Arrange: Instantiate the service with our test engine.

    \# We mock the connection factory to return connections from our in-memory engine.

    class MockConnectionFactory(SqliteConnectionFactory):

        def get\_connection(self):

            return engine.connect()

    analytics\_service \= SqliteAnalyticsService(MockConnectionFactory(db\_path=":memory:"))

    \# In a real scenario, we would query the DB for the cycle\_id created by the seeder.

    \# For simplicity, we assume it's the first one.

    cycle\_id \= 1



    \# 2\. Act: Call the method under test.

    daily\_data \= analytics\_service.get\_daily\_performance(cycle\_id=cycle\_id)

    \# 3\. Assert: Verify the output against the source JSON data.

    with open(f"tests/fixtures/profiles/{profile\_name}.json") as f:

        profile \= json.load(f)

    \# Group questions by date from the profile to get expected results

    expected\_perf \= {}

    for session in profile\['cycle'\]\['sessions'\]:

        date\_key \= datetime.fromisoformat(session\['start\_time'\]).strftime('%Y-%m-%d')

        if date\_key not in expected\_perf:

            expected\_perf\[date\_key\] \= {'total': 0, 'correct': 0}



        expected\_perf\[date\_key\]\['total'\] \+= len(session\['questions'\])

        expected\_perf\[date\_key\]\['correct'\] \+= sum(1 for q in session\['questions'\] if q\['is\_correct'\])

    assert len(daily\_data) \== len(expected\_perf)

    for perf\_day in daily\_data:

        assert perf\_day.date in expected\_perf

        assert perf\_day.questions\_done \== expected\_perf\[perf\_day.date\]\['total'\]

        assert perf\_day.questions\_correct \== expected\_perf\[perf\_day.date\]\['correct'\]

---

## Phase 5 — Expansion and Advanced Usage

The framework is designed to be extensible for more advanced testing scenarios.

* **Command-Line Seeder** A CLI can be added to the seeder to generate physical database files for manual inspection or for use in the development environment.

  * **Implementation:** Add an `if __name__ == "__main__"` block to `app/core/simulation/seeder.py` that uses `argparse`.
  * **Usage:** `python -m app.core.simulation.seeder --profile alex --output data/alex.db`


* **Randomized Profile Generator** A script can be created to generate a large number of randomized user profiles for stress testing and identifying edge cases.

  * **Implementation:** Create `app/core/simulation/generator.py`. This script will programmatically build dictionaries matching the refined JSON structure and save them as files.
  * **Usage:** `python -m app.core.simulation.generator --count 50 --output-dir tests/fixtures/profiles`


* **Targeted Pytest Runs** Pytest can be configured to run tests against a single specified user profile, which is invaluable for debugging a failing test case.

  * **Implementation:** Add the following hooks to `tests/conftest.py`.


  \# tests/conftest.py


  def pytest\_addoption(parser):


      """Adds the \--profile command-line option to pytest."""


      parser.addoption(


          "--profile", action="store", default=None, help="Run tests for a specific profile name (e.g., 'alex')"


      )


  def pytest\_generate\_tests(metafunc):


      """


      Dynamically parametrizes tests that use the 'seeded\_engine' fixture.


      If \--profile is specified, it runs only for that profile.


      Otherwise, it discovers all profiles in the fixtures directory.


      """


      if "seeded\_engine" in metafunc.fixturenames:


          profile\_option \= metafunc.config.getoption("profile")





          profile\_dir \= "tests/fixtures/profiles"


          all\_profiles \= \[


              f.replace(".json", "") for f in os.listdir(profile\_dir) if f.endswith(".json")


          \]





          if profile\_option:


              if profile\_option in all\_profiles:


                  metafunc.parametrize("seeded\_engine", \[profile\_option\], indirect=True)


              else:


                  pytest.fail(f"Profile '{profile\_option}' not found in {profile\_dir}")


          else:


              metafunc.parametrize("seeded\_engine", all\_profiles, indirect=True)


  * **Usage:**
    * `pytest tests/test_analytics.py` (Runs tests for all profiles)
    * `pytest tests/test_analytics.py --profile alex` (Runs tests only for `alex.json`)

---

## Outcome

This refined system provides a comprehensive, practical, and scalable testing solution for the Serena application:

1. **Deterministic Test Data:** JSON profiles provide a version-controllable, human-readable source of truth for test data.
2. **Realistic State Simulation:** The refined data structure allows for modeling the complete application state, from a new user to an advanced one with a complex history.
3. **High Performance and Isolation:** In-memory databases ensure tests run quickly and are completely independent, allowing for parallel execution.
4. **Architectural Consistency:** The seeder and test implementations follow the application's existing data access patterns, making them easy to understand and maintain.
5. **Extensible Framework:** The system is designed with clear hooks for adding a CLI, generating more complex data, and improving the developer workflow with targeted test runs.
