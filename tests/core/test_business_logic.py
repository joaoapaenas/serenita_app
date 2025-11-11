# tests/core/test_business_logic.py
import pytest
from app.core import business_logic
from app.models.subject import CycleSubject
from app.models.session import SubjectPerformance

def test_calculate_final_weight():
    """Tests the weighted average calculation."""
    # Arrange
    relevance = 5
    volume = 2
    difficulty = 4
    # Act
    weight = business_logic.calculate_final_weight(relevance, volume, difficulty)
    # Assert (0.5*5 + 0.2*2 + 0.3*4 = 2.5 + 0.4 + 1.2 = 4.1)
    assert weight == 4.1

def test_calculate_num_blocks():
    """Tests rounding for block calculation."""
    assert business_logic.calculate_num_blocks(3.4) == 3
    assert business_logic.calculate_num_blocks(3.5) == 4
    assert business_logic.calculate_num_blocks(3.8) == 4
    assert business_logic.calculate_num_blocks(0.0) == 0

def test_generate_study_queue():
    """Tests that the queue contains the correct number of blocks per subject."""
    # Arrange
    sub1 = CycleSubject(id=101, num_blocks_in_cycle=3, name="Subject A", subject_id=1, cycle_id=1, relevance_weight=1, volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=0, color="blue", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    sub2 = CycleSubject(id=102, num_blocks_in_cycle=2, name="Subject B", subject_id=2, cycle_id=1, relevance_weight=1, volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=0, color="red", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    sub3 = CycleSubject(id=103, num_blocks_in_cycle=0, name="Subject C", subject_id=3, cycle_id=1, relevance_weight=1, volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=0, color="green", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    subjects = [sub1, sub2, sub3]

    # Act
    queue = business_logic.generate_study_queue(subjects)

    # Assert
    assert len(queue) == 5
    assert queue.count(101) == 3
    assert queue.count(102) == 2
    assert 103 not in queue

def test_suggest_rebalance_low_accuracy():
    """Tests the low accuracy rebalance suggestion."""
    # Arrange
    cycle_subject = CycleSubject(id=1, name="Math", difficulty_weight=3, subject_id=1, cycle_id=1, relevance_weight=1, volume_weight=1, is_active=True, final_weight_calc=0, num_blocks_in_cycle=0, color="blue", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    performance = SubjectPerformance(subject_name="Math", total_questions=30, total_correct=20) # 66.7%

    # Act
    suggestions = business_logic.suggest_rebalance([cycle_subject], [performance])

    # Assert
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion["cycle_subject_id"] == 1
    assert suggestion["old_difficulty"] == 3
    assert suggestion["new_difficulty"] == 4
    assert "Low Accuracy" in suggestion["reason"]

def test_suggest_rebalance_high_accuracy():
    """Tests the high accuracy rebalance suggestion."""
    # Arrange
    cycle_subject = CycleSubject(id=2, name="History", difficulty_weight=2, subject_id=1, cycle_id=1, relevance_weight=1, volume_weight=1, is_active=True, final_weight_calc=0, num_blocks_in_cycle=0, color="red", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    performance = SubjectPerformance(subject_name="History", total_questions=50, total_correct=48) # 96%

    # Act
    suggestions = business_logic.suggest_rebalance([cycle_subject], [performance])

    # Assert
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion["cycle_subject_id"] == 2
    assert suggestion["old_difficulty"] == 2
    assert suggestion["new_difficulty"] == 1
    assert "High Accuracy" in suggestion["reason"]

def test_suggest_rebalance_no_suggestion():
    """Tests cases where no suggestion should be generated."""
    # Case 1: Not enough questions
    cs1 = CycleSubject(id=3, name="Physics", difficulty_weight=4, subject_id=1, cycle_id=1, relevance_weight=1, volume_weight=1, is_active=True, final_weight_calc=0, num_blocks_in_cycle=0, color="green", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    p1 = SubjectPerformance(subject_name="Physics", total_questions=10, total_correct=5)
    # Case 2: Accuracy is in the normal range
    cs2 = CycleSubject(id=4, name="Chemistry", difficulty_weight=3, subject_id=1, cycle_id=1, relevance_weight=1, volume_weight=1, is_active=True, final_weight_calc=0, num_blocks_in_cycle=0, color="yellow", date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[])
    p2 = SubjectPerformance(subject_name="Chemistry", total_questions=100, total_correct=85)

    suggestions = business_logic.suggest_rebalance([cs1, cs2], [p1, p2])
    assert len(suggestions) == 0