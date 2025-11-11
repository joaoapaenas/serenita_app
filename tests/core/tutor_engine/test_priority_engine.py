# tests/core/tutor_engine/test_priority_engine.py
import pytest
from app.core.tutor_engine.priority_engine import PriorityEngine
from app.models.subject import CycleSubject


@pytest.fixture
def subject_template():
    def _subject_factory(state, points):
        return CycleSubject(id=1, cycle_id=1, subject_id=1, name="Sub",
                            relevance_weight=points, volume_weight=3, difficulty_weight=3,
                            is_active=True, final_weight_calc=0, num_blocks_in_cycle=0,
                            current_strategic_state=state)

    return _subject_factory


# --- FIX: Helper now includes ALL keys the engine might access ---
def make_diagnostics(mode, mastery=0.0, confidence=1.0, durability=0.0, time_hr=0.0, velocity=0.0):
    return {
        'strategic_mode': mode,
        'durable_mastery_score': mastery,
        'mastery_confidence_score': confidence,
        'durability_factor': durability,
        'total_time_invested_hr': time_hr,
        'learning_velocity': velocity
    }


def test_base_priority_calculation(subject_template):
    engine = PriorityEngine(cognitive_capacity_multiplier=1.0, all_discovery_subjects=[])

    discovery_sub = subject_template('DISCOVERY', 5)
    diag_discovery = make_diagnostics('DISCOVERY')
    p_discovery, _, _ = engine.run(discovery_sub, diag_discovery, None)

    deep_work_sub = subject_template('DEEP_WORK', 1)
    diag_deep_work = make_diagnostics('DEEP_WORK', mastery=0.2, confidence=0.8)
    p_deep_work, _, _ = engine.run(deep_work_sub, diag_deep_work, None)

    conquer_sub = subject_template('CONQUER', 3)
    # The 'conquer' path now has the required keys, even if they are 0
    diag_conquer = make_diagnostics('CONQUER', mastery=0.85, confidence=0.9, time_hr=10.0, velocity=0.1)
    p_conquer, _, _ = engine.run(conquer_sub, diag_conquer, None)

    assert p_conquer > p_discovery
    assert p_discovery > p_deep_work


def test_tactical_modifier_discovery_boost(subject_template):
    sub1 = subject_template('DISCOVERY', 4);
    sub1.id = 1
    sub2 = subject_template('DISCOVERY', 5);
    sub2.id = 2
    sub3 = subject_template('DISCOVERY', 3);
    sub3.id = 3

    engine = PriorityEngine(1.0, all_discovery_subjects=[sub1, sub2, sub3])
    diagnostics = make_diagnostics('DISCOVERY')

    priority_boosted, flags_boosted, _ = engine.run(sub2, diagnostics, None)
    priority_normal, flags_normal, _ = engine.run(sub3, diagnostics, None)

    assert flags_boosted.get('discovery_boost_applied') is True
    assert flags_normal.get('discovery_boost_applied') is None
    assert priority_boosted == pytest.approx(150.0)
    assert priority_normal == pytest.approx(80.0)