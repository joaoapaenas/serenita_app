# tests/services/test_exam_service.py
from app.services.exam_service import SqliteExamService
from app.services.user_service import SqliteUserService


def test_create_and_get_exam(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    service = SqliteExamService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam_id = service.create(user_id=user.id, name="Final Exam", area="Fiscal")
    retrieved_exam = service.get_by_id(exam_id)
    assert retrieved_exam is not None
    assert retrieved_exam.id == exam_id
    assert retrieved_exam.name == "Final Exam"


def test_get_all_for_user(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    service = SqliteExamService(mock_db_factory)
    user1 = user_service.create_user("User One", "Beginner")
    user2 = user_service.create_user("User Two", "Advanced")
    service.create(user_id=user1.id, name="User One Exam A")
    service.create(user_id=user2.id, name="User Two Exam")
    service.create(user_id=user1.id, name="User One Exam B")
    user1_exams = service.get_all_for_user(user1.id)
    assert len(user1_exams) == 2
    assert {e.name for e in user1_exams} == {"User One Exam A", "User One Exam B"}


def test_get_available_templates(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    service = SqliteExamService(mock_db_factory)
    system_user_id = 1
    user = user_service.create_user("Real User", "Beginner")

    # Arrange: Get initial count of templates from seeder
    initial_templates = service.get_available_templates()
    initial_count = len(initial_templates)

    # Act: Create new templates and a regular exam
    service.create(user_id=system_user_id, name="Test Fiscal Template", status="TEMPLATE")
    service.create(user_id=system_user_id, name="Test Police Template", status="TEMPLATE")
    service.create(user_id=user.id, name="My Real Exam", status="PREVISTO")

    templates = service.get_available_templates()

    # --- FIX: Assert based on initial count ---
    assert len(templates) == initial_count + 2
    template_names = {t.name for t in templates}
    assert "Test Fiscal Template" in template_names
    assert "Test Police Template" in template_names
    assert "My Real Exam" not in template_names