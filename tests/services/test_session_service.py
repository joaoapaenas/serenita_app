# tests/services/test_session_service.py
import pytest
from app.services.session_service import SqliteSessionService
from app.services.user_service import SqliteUserService
from app.services.exam_service import SqliteExamService
from app.services.cycle_service import SqliteCycleService
from app.services.master_subject_service import SqliteMasterSubjectService
from app.services.cycle_subject_service import SqliteCycleSubjectService
from app.models.session import QuestionPerformance


@pytest.fixture
def session_setup(mock_db_factory):
    user_service = SqliteUserService(mock_db_factory)
    exam_service = SqliteExamService(mock_db_factory)
    cycle_service = SqliteCycleService(mock_db_factory)
    master_subject_service = SqliteMasterSubjectService(mock_db_factory)
    cycle_subject_service = SqliteCycleSubjectService(mock_db_factory)
    user = user_service.create_user("Test User", "Beginner")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam")
    cycle_id = cycle_service.create("Test Cycle", 60, True, 2, exam_id, "Adaptive")
    subject_id = master_subject_service.add_master_subject("Test Subject")
    weights = {
        "relevance": 1,
        "volume": 1,
        "difficulty": 1,
        "is_active": True
    }
    calculated_data = {
        "final_weight": 1.0,
        "num_blocks": 1
    }
    cycle_subject_service.add_subject_to_cycle(
        cycle_id=cycle_id,
        subject_id=subject_id,
        weights=weights,
        calculated_data=calculated_data
    )
    return {
        "user_id": user.id, "exam_id": exam_id, "cycle_id": cycle_id,
        "subject_id": subject_id, "factory": mock_db_factory
    }


def test_start_and_finish_session(session_setup):
    service = SqliteSessionService(session_setup["factory"])

    session_id = service.start_session(
        user_id=session_setup["user_id"],
        subject_id=session_setup["subject_id"],
        cycle_id=session_setup["cycle_id"]
    )
    assert session_id is not None

    questions = [
        QuestionPerformance(id=0, session_id=0, topic_name="t1", difficulty_level=3, is_correct=True),
        QuestionPerformance(id=0, session_id=0, topic_name="t1", difficulty_level=4, is_correct=False),
    ]
    service.finish_session(session_id=session_id, description="Good session", questions=questions)

    conn = session_setup["factory"].get_connection()
    session_row = conn.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,)).fetchone()
    question_rows = conn.execute("SELECT * FROM question_performance WHERE session_id = ?", (session_id,)).fetchall()

    assert session_row is not None
    assert session_row['description'] == "Good session"
    assert len(question_rows) == 2


def test_get_history_for_cycle(session_setup):
    service = SqliteSessionService(session_setup["factory"])

    session_id_1 = service.start_session(session_setup["user_id"], session_setup["subject_id"], session_setup["cycle_id"])
    questions1 = [QuestionPerformance(id=0, session_id=0, topic_name="s1", difficulty_level=1, is_correct=True)]
    service.finish_session(session_id_1, questions=questions1)

    session_id_2 = service.start_session(session_setup["user_id"], session_setup["subject_id"], session_setup["cycle_id"])
    service.finish_session(session_id_2, questions=[])  # A session with no questions

    history = service.get_history_for_cycle(session_setup["cycle_id"])

    assert len(history) == 2
    session1 = next(s for s in history if s.id == session_id_1)
    assert len(session1.questions) == 1