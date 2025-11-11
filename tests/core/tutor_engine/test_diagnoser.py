# tests/core/tutor_engine/test_diagnoser.py
import pytest
from datetime import datetime, timedelta, timezone
from app.core.tutor_engine.diagnoser import Diagnoser
from app.models.subject import CycleSubject
from app.models.session import StudySession, QuestionPerformance


@pytest.fixture
def base_subject():
    """A base subject for tests."""
    return CycleSubject(
        id=1, cycle_id=1, subject_id=1, name="Test Subject",
        relevance_weight=3, volume_weight=3, difficulty_weight=3,
        is_active=True, final_weight_calc=0, num_blocks_in_cycle=0,
        current_strategic_state='DISCOVERY'
    )


def test_diagnoser_no_history(base_subject):
    """Test diagnoser with no study history for the subject."""
    diagnoser = Diagnoser(base_subject, [])
    diagnostics = diagnoser.run()

    assert diagnostics['strategic_mode'] == 'DISCOVERY'
    assert diagnostics['mastery_confidence_score'] == 0.0
    assert diagnostics['durable_mastery_score'] == 0.0
    assert diagnostics['total_questions'] == 0


def test_diagnoser_with_recent_history(base_subject):
    """Test with a simple, recent study history."""
    today = datetime.now(timezone.utc)
    session = StudySession(
        id=1, subject_id=1, start_time=today.isoformat(),
        liquid_duration_sec=3600,
        questions=[
            QuestionPerformance(id=1, session_id=1, topic_name="t1", difficulty_level=3, is_correct=True),
            QuestionPerformance(id=2, session_id=1, topic_name="t1", difficulty_level=3, is_correct=True),
            QuestionPerformance(id=3, session_id=1, topic_name="t2", difficulty_level=3, is_correct=False),
            QuestionPerformance(id=4, session_id=1, topic_name="t2", difficulty_level=3, is_correct=True),
        ],
        user_id=1, cycle_id=1, topic_id=None, end_time=None, total_duration_sec=0, total_pause_duration_sec=0,
        description=None, study_method=None, soft_delete=False, deleted_at=None
    )
    history = [session]
    diagnoser = Diagnoser(base_subject, history)
    diagnostics = diagnoser.run()

    assert diagnostics['strategic_mode'] == 'DEEP_WORK'
    assert diagnostics['durable_mastery_score'] == pytest.approx(0.75)
    assert diagnostics['total_questions'] == 4
    assert diagnostics['mastery_by_topic']['t1'] == 1.0
    assert diagnostics['mastery_by_topic']['t2'] == 0.5


def test_diagnoser_propose_mode_logic():
    """Test the mode proposal logic in isolation."""
    # Dummy diagnoser instance to access the private method for testing
    diagnoser = Diagnoser(None, [])

    # Discovery
    assert diagnoser._propose_mode(durable_mastery=0.05, time_hr=0.5) == 'DISCOVERY'
    # Deep Work
    assert diagnoser._propose_mode(durable_mastery=0.7) == 'DEEP_WORK'
    # Conquer
    assert diagnoser._propose_mode(durable_mastery=0.85) == 'CONQUER'
    # Cement
    assert diagnoser._propose_mode(durable_mastery=0.92, durability_factor=0.6) == 'CEMENT'
    # Maintain
    assert diagnoser._propose_mode(durable_mastery=0.95, durability_factor=0.8) == 'MAINTAIN'