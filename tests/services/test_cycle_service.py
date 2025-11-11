# tests/services/test_cycle_service.py
from app.services.cycle_service import SqliteCycleService
from app.services.exam_service import SqliteExamService
from app.services.user_service import SqliteUserService

def test_create_and_get_cycle(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    exam_service = SqliteExamService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam")
    service = SqliteCycleService(mock_db_factory)
    new_cycle_id = service.create("Spring Prep", 60, True, 3, exam_id, "Adaptive")
    retrieved_cycle = service.get_by_id(new_cycle_id)
    assert new_cycle_id is not None
    assert retrieved_cycle is not None
    assert retrieved_cycle.id == new_cycle_id
    assert retrieved_cycle.name == "Spring Prep"

def test_set_active_cycle(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    exam_service = SqliteExamService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam")
    service = SqliteCycleService(mock_db_factory)
    cycle1_id = service.create("Cycle 1", 60, True, 2, exam_id, "Fixed")
    cycle2_id = service.create("Cycle 2", 60, True, 2, exam_id, "Fixed")
    service.set_active(cycle1_id)
    active_cycle = service.get_active()
    assert active_cycle is not None
    assert active_cycle.id == cycle1_id

def test_get_all_for_exam(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    exam_service = SqliteExamService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam1_id = exam_service.create(user_id=user.id, name="Exam 1")
    exam2_id = exam_service.create(user_id=user.id, name="Exam 2")
    service = SqliteCycleService(mock_db_factory)
    service.create("Cycle A", 60, True, 2, exam1_id, "Fixed")
    service.create("Cycle B", 60, True, 2, exam1_id, "Fixed")
    service.create("Cycle C", 60, True, 2, exam2_id, "Fixed")
    exam1_cycles = service.get_all_for_exam(exam1_id)
    assert len(exam1_cycles) == 2

def test_soft_delete_and_restore(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    exam_service = SqliteExamService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam")
    service = SqliteCycleService(mock_db_factory)
    cycle_id = service.create("Deletable Cycle", 60, False, 1, exam_id, "Basic")
    service.soft_delete(cycle_id)
    assert service.get_by_id(cycle_id) is None
    service.restore_soft_deleted(cycle_id)
    assert service.get_by_id(cycle_id) is not None