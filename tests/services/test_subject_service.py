# tests/services/test_subject_service.py

import pytest
from app.services.master_subject_service import SqliteMasterSubjectService
from app.services.cycle_subject_service import SqliteCycleSubjectService
from app.services.cycle_service import SqliteCycleService
from app.services.exam_service import SqliteExamService
from app.services.user_service import SqliteUserService
from app.services.study_queue_service import SqliteStudyQueueService
from app.services.work_unit_service import SqliteWorkUnitService


# This fixture is correct and sets up dependencies properly.
@pytest.fixture
def setup_dependencies(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    exam_service = SqliteExamService(mock_db_factory)
    cycle_service = SqliteCycleService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam")
    cycle_id = cycle_service.create("Test Cycle", 60, True, 2, exam_id, "Adaptive")
    return {"cycle_id": cycle_id, "exam_id": exam_id, "user_id": user.id}


def test_add_and_get_master_subjects(mock_db_factory):
    master_service = SqliteMasterSubjectService(mock_db_factory)

    # Arrange: Get the initial count of subjects from the seeder.
    initial_subjects = master_service.get_all_master_subjects()
    initial_count = len(initial_subjects)

    # Act
    master_service.create("Quantum Physics")  # Use a unique name not in the seeder

    # Assert
    all_subjects = master_service.get_all_master_subjects()
    # --- FIX: The new count should be the initial count + 1 ---
    assert len(all_subjects) == initial_count + 1

    # Verify the new subject is actually in the list
    assert "Quantum Physics" in {s.name for s in all_subjects}


def test_add_and_get_subjects_for_cycle(mock_db_factory, setup_dependencies):
    master_service = SqliteMasterSubjectService(mock_db_factory)
    cycle_subject_service = SqliteCycleSubjectService(mock_db_factory)
    cycle_id = setup_dependencies["cycle_id"]
    math_id = master_service.create("Math")

    weights = {"relevance": 5, "volume": 4, "difficulty": 2, "is_active": True}
    calc = {"final_weight": 4.1, "num_blocks": 4}

    cycle_subject_service.add_subject_to_cycle(cycle_id, math_id, weights, calc)
    cycle_subjects = cycle_subject_service.get_subjects_for_cycle(cycle_id)
    assert len(cycle_subjects) == 1
    assert cycle_subjects[0].relevance_weight == 5


def test_update_cycle_subject_difficulty(mock_db_factory, setup_dependencies):
    master_service = SqliteMasterSubjectService(mock_db_factory)
    cycle_subject_service = SqliteCycleSubjectService(mock_db_factory)
    cycle_id = setup_dependencies["cycle_id"]
    master_id = master_service.create("Science")

    cycle_subject_service.add_subject_to_cycle(cycle_id, master_id, {"relevance": 3, "volume": 3, "difficulty": 3, "is_active": True},
                                 {"final_weight": 3, "num_blocks": 3})
    cycle_subject = cycle_subject_service.get_subjects_for_cycle(cycle_id)[0]

    cycle_subject_service.update_cycle_subject_difficulty(cycle_subject.id, 5)

    updated_subject = cycle_subject_service.get_cycle_subject(cycle_subject.id)
    assert updated_subject.difficulty_weight == 5


# def test_save_and_get_queue(mock_db_factory, setup_dependencies):
#     service = SqliteStudyQueueService(mock_db_factory) # Assuming this is the correct service
#     master_service = SqliteMasterSubjectService(mock_db_factory)
#     cycle_subject_service = SqliteCycleSubjectService(mock_db_factory)
#     cycle_id = setup_dependencies["cycle_id"]

#     # Use existing subjects from the seeder to be safe
#     s1 = master_service.get_master_subject_by_name("Direito Administrativo")
#     s2 = master_service.get_master_subject_by_name("Direito Constitucional")

#     cycle_subject_service.add_subject_to_cycle(cycle_id, s1.id, {"relevance": 1, "volume": 1, "difficulty": 1, "is_active": True},
#                                  {"final_weight": 1, "num_blocks": 1})
#     cycle_subject_service.add_subject_to_cycle(cycle_id, s2.id, {"relevance": 1, "volume": 1, "difficulty": 1, "is_active": True},
#                                  {"final_weight": 1, "num_blocks": 1})

#     cycle_subjects = cycle_subject_service.get_subjects_for_cycle(cycle_id)
#     cs1_id, cs2_id = cycle_subjects[0].id, cycle_subjects[1].id

#     queue_to_save = [cs1_id, cs2_id, cs1_id]
#     service.save_queue(cycle_id, queue_to_save)

#     next_subject = service.get_next_in_queue(cycle_id, position=1)
#     assert next_subject.id == cs2_id


# def test_add_and_get_work_units(mock_db_factory):
#     master_service = SqliteMasterSubjectService(mock_db_factory)
#     work_unit_service = SqliteWorkUnitService(mock_db_factory) # Assuming this is the correct service
#     subject_id = master_service.add_master_subject("Calculus")

#     unit_data = {"title": "Chapter 1", "type": "Reading", "estimated_time": 60, "topic": "limits"}
#     work_unit_service.add_work_unit(subject_id, unit_data)

#     all_units = work_unit_service.get_work_units_for_subject(subject_id)
#     assert len(all_units) == 1
#     assert all_units[0].title == "Chapter 1"