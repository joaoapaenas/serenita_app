# tests/conftest.py
import pytest
import os
import sqlite3
from app.core.database import SqliteConnectionFactory
from app.core.migrations import run_migrations_on_connection
from app.models.user import User
from app.models.cycle import Cycle
from app.models.subject import CycleSubject
from app.core.simulation.seeder import seed_profile

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture(scope="function")
def db_connection():
    """
    Creates and yields a single, schema-populated in-memory SQLite connection
    for the duration of a test function. The connection is managed by the fixture.
    """
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    run_migrations_on_connection(connection, BASE_PATH)
    yield connection
    connection.close()

@pytest.fixture
def mock_db_factory(mocker, db_connection):
    """
    Mocks the SqliteConnectionFactory to always return the single,
    shared in-memory db_connection provided by the 'db_connection' fixture.
    This forces all service calls within a single test to use the same open connection.
    """
    factory = mocker.MagicMock(spec=SqliteConnectionFactory)
    factory.get_connection.return_value = db_connection
    return factory

@pytest.fixture(scope="session")
def session_db_connection():
    """
    Creates and yields a single, schema-populated in-memory SQLite connection
    for the duration of the test session. The connection is managed by the fixture.
    """
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    run_migrations_on_connection(connection, BASE_PATH)
    yield connection
    connection.close()

@pytest.fixture(scope="session")
def session_mocker(session_db_connection): # session_db_connection is not used, but it ensures session scope
    """
    Provides a session-scoped mocker fixture.
    """
    from pytest_mock import MockerFixture
    mocker = MockerFixture(session_db_connection) # Pass a dummy object for request
    yield mocker
    mocker.stopall()

@pytest.fixture(scope="session")
def session_mock_db_factory(session_mocker, session_db_connection):
    """
    Mocks the SqliteConnectionFactory to always return the single,
    shared in-memory session_db_connection provided by the 'session_db_connection' fixture.
    This forces all service calls within a single test to use the same open connection.
    """
    factory = session_mocker.MagicMock(spec=SqliteConnectionFactory)
    factory.get_connection.return_value = session_db_connection
    return factory

@pytest.fixture
def sample_user() -> User:
    return User(id=1, name="Test User", study_level="Intermediate", description=None, created_at="2023-01-01T00:00:00")

@pytest.fixture
def sample_cycle() -> Cycle:
    return Cycle(id=1, name="Test Cycle", exam_id=1, block_duration_min=60, current_queue_position=0, is_active=True, is_continuous=True, daily_goal_blocks=3, phase='Initial', created_at='2023-01-01T10:00:00', updated_at='2023-01-01T10:00:00', soft_delete=False, deleted_at=None, timing_strategy="Adaptive")

@pytest.fixture
def sample_cycle_subject() -> CycleSubject:
    return CycleSubject(id=101, cycle_id=1, subject_id=2, name="Constitutional Law", relevance_weight=5, volume_weight=4, difficulty_weight=3, is_active=True, final_weight_calc=0, num_blocks_in_cycle=0)

@pytest.fixture
def seeded_engine(request):
    """
    A pytest fixture that creates a fresh, in-memory SQLite database and
    populates it with data from a user profile JSON file.

    The fixture is parametrized indirectly via pytest_generate_tests, allowing
    tests to run against multiple user profiles automatically.

    Yields:
        tuple: A tuple containing (profile_name, sqlalchemy.engine.Engine).
    """
    profile_name = request.param
    profile_path = f"tests/fixtures/profiles/{profile_name}.json"

    engine = seed_profile(profile_path, target=":memory:")

    yield profile_name, engine

    engine.dispose()

def pytest_addoption(parser):
    """Adds the --profile command-line option to pytest."""
    parser.addoption(
        "--profile", action="store", default=None, help="Run tests for a specific profile name (e.g., 'alex')"
    )

def pytest_generate_tests(metafunc):
    """
    Dynamically parametrizes tests that use the 'seeded_engine' fixture.
    If --profile is specified, it runs only for that profile.
    Otherwise, it discovers all profiles in the fixtures directory.
    """
    if "seeded_engine" in metafunc.fixturenames:
        profile_option = metafunc.config.getoption("profile")

        profile_dir = "tests/fixtures/profiles"
        all_profiles = [
            f.replace(".json", "") for f in os.listdir(profile_dir) if f.endswith(".json")
        ]

        if profile_option:
            if profile_option in all_profiles:
                metafunc.parametrize("seeded_engine", [profile_option], indirect=True)
            else:
                pytest.fail(f"Profile '{profile_option}' not found in {profile_dir}")
        else:
            metafunc.parametrize("seeded_engine", all_profiles, indirect=True)