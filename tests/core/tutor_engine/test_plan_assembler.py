import pytest
from unittest.mock import MagicMock, patch
from app.core.tutor_engine.plan_assembler import PlanAssembler, _create_plan_from_allocation
from app.models.subject import CycleSubject, WorkUnit


@pytest.fixture
def mock_processed_subjects():
    """Fixture for mock processed subjects data."""
    return [
        {
            'subject_id': 1, 'subject_name': 'Math', 'final_priority': 10.0,
            'reasoning': 'High priority',
            'diagnostics': {'strategic_mode': 'DEEP_WORK', 'durability_factor': 0.7}
        },
        {
            'subject_id': 2, 'subject_name': 'Physics', 'final_priority': 5.0,
            'reasoning': 'Medium priority',
            'diagnostics': {'strategic_mode': 'DISCOVERY', 'durability_factor': 0.5}
        },
        {
            'subject_id': 3, 'subject_name': 'History', 'final_priority': 2.0,
            'reasoning': 'Low priority',
            'diagnostics': {'strategic_mode': 'MAINTAIN', 'durability_factor': 0.9}
        },
        {
            'subject_id': 4, 'subject_name': 'Chemistry', 'final_priority': 8.0,
            'reasoning': 'Cement priority',
            'diagnostics': {'strategic_mode': 'CEMENT', 'durability_factor': 0.4}
        },
    ]


@pytest.fixture
def mock_cycle_config():
    """Fixture for mock cycle configuration data."""
    return {
        'timing_strategy': 'Adaptive',
        'block_duration_min': 60,
        'available_time_minutes': 180,
        'cycle_duration_days': 7,
        'subjects': [
            CycleSubject(
                id=1, cycle_id=1, subject_id=1, relevance_weight=1, volume_weight=1, difficulty_weight=1,
                is_active=True, final_weight_calc=1.0, num_blocks_in_cycle=1, name="Math", color="blue",
                date_added="2023-01-01", current_strategic_state="DEEP_WORK", state_hysteresis_data={},
                work_units=[
                    WorkUnit(id=101, subject_id=1, unit_id="wu_1_1", title="Math WU1", type="reading",
                             estimated_time_minutes=30, is_completed=False, related_questions_topic="Algebra",
                             sequence_order=1),
                    WorkUnit(id=102, subject_id=1, unit_id="wu_1_2", title="Math WU2", type="problem",
                             estimated_time_minutes=40, is_completed=False, related_questions_topic="Geometry",
                             sequence_order=2),
                ]
            ),
            CycleSubject(
                id=2, cycle_id=1, subject_id=2, relevance_weight=1, volume_weight=1, difficulty_weight=1,
                is_active=True, final_weight_calc=1.0, num_blocks_in_cycle=1, name="Physics", color="red",
                date_added="2023-01-01", current_strategic_state="DISCOVERY", state_hysteresis_data={},
                work_units=[
                    WorkUnit(id=201, subject_id=2, unit_id="wu_2_1", title="Physics WU1", type="reading",
                             estimated_time_minutes=20, is_completed=False, related_questions_topic="Mechanics",
                             sequence_order=1),
                ]
            ),
            CycleSubject(
                id=4, cycle_id=1, subject_id=4, relevance_weight=1, volume_weight=1, difficulty_weight=1,
                is_active=True, final_weight_calc=1.0, num_blocks_in_cycle=1, name="Chemistry", color="green",
                date_added="2023-01-01", current_strategic_state="CEMENT", state_hysteresis_data={},
                work_units=[
                    WorkUnit(id=401, subject_id=4, unit_id="wu_4_1", title="Chem WU1", type="reading",
                             estimated_time_minutes=50, is_completed=False, related_questions_topic="Organic",
                             sequence_order=1),
                ]
            ),
        ]
    }


def test_init_separates_maintain_subjects(mock_processed_subjects, mock_cycle_config):
    """Test that __init__ correctly separates processed and maintain subjects."""
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    assert len(assembler.processed_subjects) == 3
    assert all(s['diagnostics']['strategic_mode'] != 'MAINTAIN' for s in assembler.processed_subjects)
    assert len(assembler.maintain_subjects) == 1
    assert assembler.maintain_subjects[0]['subject_name'] == 'History'


@patch.object(PlanAssembler, '_allocate_time_fixed')
@patch.object(PlanAssembler, '_allocate_time_basic')
@patch.object(PlanAssembler, '_allocate_time_adaptive')
def test_dispatch_time_allocation(mock_adaptive, mock_basic, mock_fixed, mock_processed_subjects, mock_cycle_config):
    """Test that _dispatch_time_allocation calls the correct strategy."""
    # Test Fixed strategy
    mock_cycle_config['timing_strategy'] = 'Fixed'
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    assembler._dispatch_time_allocation()
    mock_fixed.assert_called_once()
    mock_basic.assert_not_called()
    mock_adaptive.assert_not_called()
    mock_fixed.reset_mock()
    mock_basic.reset_mock()
    mock_adaptive.reset_mock()

    # Test Basic strategy
    mock_cycle_config['timing_strategy'] = 'Basic'
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    assembler._dispatch_time_allocation()
    mock_basic.assert_called_once()
    mock_fixed.assert_not_called()
    mock_adaptive.assert_not_called()
    mock_fixed.reset_mock()
    mock_basic.reset_mock()
    mock_adaptive.reset_mock()

    # Test Adaptive strategy (default)
    mock_cycle_config['timing_strategy'] = 'Unknown' # Should default to Adaptive
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    assembler._dispatch_time_allocation()
    mock_adaptive.assert_called_once()
    mock_fixed.assert_not_called()
    mock_basic.assert_not_called()


def test_allocate_time_fixed(mock_processed_subjects, mock_cycle_config):
    """Test fixed time allocation."""
    mock_cycle_config['timing_strategy'] = 'Fixed'
    mock_cycle_config['block_duration_min'] = 45
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    result = assembler._allocate_time_fixed()
    assert result == {1: 45.0, 2: 45.0, 4: 45.0} # Only processed subjects


def test_allocate_time_basic(mock_processed_subjects, mock_cycle_config):
    """Test basic time allocation based on priority tiers."""
    mock_cycle_config['timing_strategy'] = 'Basic'
    # Processed subjects: Math (10.0), Physics (5.0), Chemistry (8.0)
    # Min_p = 5.0, Max_p = 10.0, Range_p = 5.0
    # Tier 1 threshold: 5.0 + 5.0 * 0.33 = 6.65 (Physics) -> 45 min
    # Tier 2 threshold: 5.0 + 5.0 * 0.66 = 8.3 (Chemistry) -> 60 min
    # Above 8.3 (Math) -> 90 min
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    result = assembler._allocate_time_basic()
    assert result == {1: 90.0, 2: 45.0, 4: 60.0}


def test_allocate_time_basic_all_same_priority(mock_processed_subjects, mock_cycle_config):
    """Test basic time allocation when all priorities are the same."""
    mock_cycle_config['timing_strategy'] = 'Basic'
    processed_subjects_same_priority = [
        {
            'subject_id': 1, 'subject_name': 'Math', 'final_priority': 5.0,
            'reasoning': 'High priority',
            'diagnostics': {'strategic_mode': 'DEEP_WORK', 'durability_factor': 0.7}
        },
        {
            'subject_id': 2, 'subject_name': 'Physics', 'final_priority': 5.0,
            'reasoning': 'Medium priority',
            'diagnostics': {'strategic_mode': 'DISCOVERY', 'durability_factor': 0.5}
        },
    ]
    assembler = PlanAssembler(processed_subjects_same_priority, mock_cycle_config)
    result = assembler._allocate_time_basic()
    assert result == {1: 60.0, 2: 60.0}


def test_allocate_time_adaptive(mock_processed_subjects, mock_cycle_config):
    """Test adaptive time allocation."""
    mock_cycle_config['timing_strategy'] = 'Adaptive'
    mock_cycle_config['available_time_minutes'] = 180 # Total time
    # Processed subjects: Math (10.0), Physics (5.0), Chemistry (8.0)
    # Total priority = 10 + 5 + 8 = 23
    # Math: (10/23) * 180 = 78.26 -> round to 80, clamp to 80
    # Physics: (5/23) * 180 = 39.13 -> round to 40, clamp to 40
    # Chemistry: (8/23) * 180 = 69.56 -> round to 70, clamp to 70
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    result = assembler._allocate_time_adaptive()
    assert result == {1: 80.0, 2: 40.0, 4: 60.0}


def test_allocate_time_adaptive_zero_priority(mock_processed_subjects, mock_cycle_config):
    """Test adaptive time allocation when total priority is zero."""
    mock_cycle_config['timing_strategy'] = 'Adaptive'
    mock_cycle_config['available_time_minutes'] = 180
    processed_subjects_zero_priority = [
        {
            'subject_id': 1, 'subject_name': 'Math', 'final_priority': 0.0,
            'reasoning': 'High priority',
            'diagnostics': {'strategic_mode': 'DEEP_WORK', 'durability_factor': 0.7}
        },
    ]
    assembler = PlanAssembler(processed_subjects_zero_priority, mock_cycle_config)
    result = assembler._allocate_time_adaptive()
    assert result == {1: 40.0} # Should default to minimum


@patch('app.core.tutor_engine.plan_assembler._create_plan_from_allocation')
@patch.object(PlanAssembler, '_generate_deep_work_plan')
@patch.object(PlanAssembler, '_generate_review_reinforce_plan')
def test_generate_strategic_view(mock_review, mock_deep_work, mock_create_plan, mock_processed_subjects, mock_cycle_config):
    """Test generation of strategic view."""
    mock_create_plan.return_value = {"focus_mode": "Balanced", "sessions": []}
    mock_deep_work.return_value = {"focus_mode": "Deep Work", "sessions": []}
    mock_review.return_value = {"focus_mode": "Review & Reinforce", "sessions": []}

    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    allocated_time_map = assembler._dispatch_time_allocation()
    plan_scaffold, _ = assembler.generate_strategic_view()

    mock_create_plan.assert_called_once_with(allocated_time_map, "Balanced",
                                            assembler.processed_subjects, assembler.maintain_subjects)
    mock_deep_work.assert_called_once_with(allocated_time_map)
    mock_review.assert_called_once_with(allocated_time_map)
    assert "recommended_plan" in plan_scaffold
    assert "alternative_plans" in plan_scaffold
    assert len(plan_scaffold["alternative_plans"]) == 2


def test_generate_deep_work_plan(mock_processed_subjects, mock_cycle_config):
    """Test generation of deep work plan."""
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    base_allocated_time_map = assembler._dispatch_time_allocation() # Get the base allocation map
    # Math (DEEP_WORK, 10.0), Physics (DISCOVERY, 5.0), Chemistry (CEMENT, 8.0)
    # Candidates: Math
    # Focus subjects: Math (10.0)
    # Other subjects: Physics (5.0), Chemistry (8.0)
    # Available time = 180
    # Time for focus = 180 * 0.7 = 126
    # Time for others = 180 * 0.3 = 54
    # Focus priority total = 10
    # Others priority total = 13
    # Math allocation: (10/10) * 126 = 126
    # Physics allocation: (5/13) * 54 = 20.76 -> 21
    # Chemistry allocation: (8/13) * 54 = 33.23 -> 33
    result = assembler._generate_deep_work_plan(base_allocated_time_map)
    assert result is not None
    assert result['focus_mode'] == 'Deep Work'
    sessions = {s['subject_id']: s['allocated_minutes'] for s in result['sessions']}
    assert sessions[1] == 126 # Math
    assert sessions[4] == 33 # Chemistry
    assert sessions[2] == 21 # Physics


def test_generate_deep_work_plan_no_candidates(mock_processed_subjects, mock_cycle_config):
    """Test deep work plan generation when no candidates are available."""
    processed_subjects_no_deep_work = [
        {
            'subject_id': 2, 'subject_name': 'Physics', 'final_priority': 5.0,
            'reasoning': 'Medium priority',
            'diagnostics': {'strategic_mode': 'DISCOVERY', 'durability_factor': 0.5}
        },
    ]
    assembler = PlanAssembler(processed_subjects_no_deep_work, mock_cycle_config)
    base_allocated_time_map = assembler._dispatch_time_allocation()
    result = assembler._generate_deep_work_plan(base_allocated_time_map)
    assert result is None


def test_generate_review_reinforce_plan(mock_processed_subjects, mock_cycle_config):
    """Test generation of review & reinforce plan."""
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    base_allocated_time_map = assembler._dispatch_time_allocation() # Get the base allocation map
    # Processed subjects: Math (DEEP_WORK, 10.0), Physics (DISCOVERY, 5.0), Chemistry (CEMENT, 8.0)
    # Allocated time map (from adaptive): {1: 80.0, 2: 40.0, 4: 60.0}
    # Candidates for review: Physics (DISCOVERY, durability 0.5), Chemistry (CEMENT, durability 0.4)
    # Non-candidates: Math
    # Math time halved: 80 / 2 = 40
    # Physics time remains: 40
    # Chemistry time remains: 60
    result = assembler._generate_review_reinforce_plan(base_allocated_time_map)
    assert result is not None
    assert result['focus_mode'] == 'Review & Reinforce'
    sessions = {s['subject_id']: s['allocated_minutes'] for s in result['sessions']}
    assert sessions[1] == 40 # Math
    assert sessions[2] == 40 # Physics
    assert sessions[4] == 60 # Chemistry


def test_generate_review_reinforce_plan_no_candidates(mock_processed_subjects, mock_cycle_config):
    """Test review & reinforce plan generation when no candidates are available."""
    processed_subjects_no_review = [
        {
            'subject_id': 1, 'subject_name': 'Math', 'final_priority': 10.0,
            'reasoning': 'High priority',
            'diagnostics': {'strategic_mode': 'DEEP_WORK', 'durability_factor': 0.7}
        },
    ]
    assembler = PlanAssembler(processed_subjects_no_review, mock_cycle_config)
    base_allocated_time_map = assembler._dispatch_time_allocation()
    result = assembler._generate_review_reinforce_plan(base_allocated_time_map)
    assert result is None


def test_create_plan_from_allocation(mock_processed_subjects, mock_cycle_config):
    """Test helper to create a plan structure."""
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    allocation_map = {1: 60.0, 2: 30.0, 3: 30.0, 4: 45.0} # Include maintain subject
    focus_mode = "Custom Focus"
    result = _create_plan_from_allocation(allocation_map, focus_mode,
                                         assembler.processed_subjects, assembler.maintain_subjects)

    assert result['focus_mode'] == focus_mode
    assert result['description'] == "A custom focus-focus plan for this cycle."
    assert len(result['sessions']) == 4 # Math, Physics, Chemistry, History (maintain)
    # Check sorting (descending allocated_minutes)
    assert result['sessions'][0]['subject_name'] == 'Math'
    assert result['sessions'][0]['allocated_minutes'] == 60
    assert result['sessions'][1]['subject_name'] == 'Chemistry'
    assert result['sessions'][1]['allocated_minutes'] == 45
    assert result['sessions'][2]['subject_name'] == 'Physics'
    assert result['sessions'][2]['allocated_minutes'] == 30
    assert result['sessions'][3]['subject_name'] == 'History'
    assert result['sessions'][3]['allocated_minutes'] == 30


def test_generate_tactical_view(mock_processed_subjects, mock_cycle_config):
    """Test generation of tactical view with work units."""
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    allocated_time_map = assembler._dispatch_time_allocation()
    # Allocated time map (from adaptive): {1: 80.0, 2: 40.0, 4: 60.0}
    # Math (WU1: 30min, WU2: 40min) -> total 70min, allocated 80min. Both should be scheduled.
    # Physics (WU1: 20min) -> total 20min, allocated 40min. Should be scheduled.
    # Chemistry (WU1: 50min) -> total 50min, allocated 60min. Should be scheduled.
    result = assembler.generate_tactical_view(allocated_time_map)

    assert len(result) == 4 # Math WU1, Math WU2, Physics WU1, Chemistry WU1
    # Check day indexing
    assert result[0]['day_index'] == 0
    assert result[1]['day_index'] == 1
    assert result[2]['day_index'] == 2
    assert result[3]['day_index'] == 3

    # Check content of a task
    math_wu1 = next(t for t in result if t['work_unit_id'] == 'wu_1_1')
    assert math_wu1['subject_name'] == 'Math'
    assert math_wu1['allocated_minutes'] == 30
    assert math_wu1['is_completed'] is False


def test_generate_tactical_view_no_work_units(mock_processed_subjects, mock_cycle_config):
    """Test tactical view generation when subjects have no work units."""
    # Remove work units from cycle_config subjects
    for sub in mock_cycle_config['subjects']:
        sub.work_units = []
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    allocated_time_map = assembler._dispatch_time_allocation()
    result = assembler.generate_tactical_view(allocated_time_map)
    assert result == []


def test_generate_tactical_view_work_units_exceed_time(mock_processed_subjects, mock_cycle_config):
    """Test tactical view generation when work units exceed allocated time."""
    # Reduce allocated time for Math to 20 minutes
    mock_cycle_config['available_time_minutes'] = 20 # This will make Math's allocated time 20
    # Math (WU1: 30min, WU2: 40min) -> only WU1 should be considered, but it exceeds 20min. So none.
    # Physics (WU1: 20min) -> allocated time will be ~10min. None.
    # Chemistry (WU1: 50min) -> allocated time will be ~15min. None.
    assembler = PlanAssembler(mock_processed_subjects, mock_cycle_config)
    allocated_time_map = assembler._dispatch_time_allocation()
    result = assembler.generate_tactical_view(allocated_time_map)
    expected_tasks = [
        {
            'subject_name': 'Math', 'subject_id': 1, 'work_unit_id': 'wu_1_1',
            'work_unit_title': 'Math WU1', 'allocated_minutes': 30,
            'reasoning': 'High priority', 'is_completed': False, 'day_index': 0
        },
        {
            'subject_name': 'Physics', 'subject_id': 2, 'work_unit_id': 'wu_2_1',
            'work_unit_title': 'Physics WU1', 'allocated_minutes': 20,
            'reasoning': 'Medium priority', 'is_completed': False, 'day_index': 1
        },
    ]
    assert result == expected_tasks