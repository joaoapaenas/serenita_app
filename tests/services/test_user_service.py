# tests/services/test_user_service.py
from app.services.user_service import SqliteUserService


def test_create_and_get_user(mock_db_factory):
    service = SqliteUserService(mock_db_factory)
    created_user = service.create_user("John Doe", "Intermediate")
    assert created_user is not None
    assert created_user.name == "John Doe"
    retrieved_user = service.get_user(created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id


def test_get_first_user(mock_db_factory):
    service = SqliteUserService(mock_db_factory)
    service.create_user("First Real User", "Beginner")
    service.create_user("Second Real User", "Advanced")
    first_user = service.get_first_user()
    assert first_user is not None
    assert first_user.name == "First Real User"


def test_update_user(mock_db_factory):
    service = SqliteUserService(mock_db_factory)
    user = service.create_user("Original Name", "Beginner")
    updated_user = service.update_user(user.id, "Updated Name", "Advanced", "Dark")
    assert updated_user is not None
    assert updated_user.name == "Updated Name"
    refetched_user = service.get_user(user.id)
    assert refetched_user is not None
    assert refetched_user.name == "Updated Name"


def test_save_and_get_human_factors(mock_db_factory):
    service = SqliteUserService(mock_db_factory)
    user_id = 1  # System user from seeder
    service.save_human_factor(user_id, "2023-10-26", "High", "Low")
    service.save_human_factor(user_id, "2023-10-27", "Normal", "Normal")
    history = service.get_human_factor_history(user_id)
    assert len(history) == 2
    assert history[0].date == "2023-10-27"
