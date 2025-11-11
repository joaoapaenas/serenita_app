import pytest
from unittest.mock import MagicMock
from app.core.tutor_engine.human_factor_smoother import HumanFactorSmoother


@pytest.fixture
def smoother():
    """Fixture for HumanFactorSmoother instance."""
    return HumanFactorSmoother()


@pytest.fixture
def mock_human_factor_history():
    """Helper to create mock HumanFactor objects for history."""
    def _make_history(energy_levels: list, stress_levels: list):
        history = []
        for e, s in zip(energy_levels, stress_levels):
            mock_hf = MagicMock()
            mock_hf.energy_level = e
            mock_hf.stress_level = s
            history.append(mock_hf)
        return history
    return _make_history


def test_run_empty_history(smoother):
    """Test calculation with empty history."""
    current_hf = {'energy_level': 'Normal', 'stress_level': 'Normal'}
    result = smoother.run(current_hf, [])
    # (0.6 * 1.0) + (0.4 * 1.0) = 1.0 for both energy and stress
    # (1.0 + 1.0) / 2.0 = 1.0
    assert result == pytest.approx(1.0)


def test_run_normal_conditions(smoother, mock_human_factor_history):
    """Test calculation with normal current and historical conditions."""
    current_hf = {'energy_level': 'Normal', 'stress_level': 'Normal'}
    history = mock_human_factor_history(['Normal', 'Normal'], ['Normal', 'Normal'])
    result = smoother.run(current_hf, history)
    assert result == pytest.approx(1.0)


def test_run_high_energy_low_stress(smoother, mock_human_factor_history):
    """Test calculation with high energy and low stress."""
    current_hf = {'energy_level': 'High', 'stress_level': 'Low'}
    history = mock_human_factor_history(['High', 'Low'], ['Low', 'High']) # Mixed history
    result = smoother.run(current_hf, history)

    # Current: Energy=1.2, Stress=1.1
    # History: Energy_avg = (1.2 + 0.8) / 2 = 1.0
    #          Stress_avg = (1.1 + 0.8) / 2 = 0.95
    # Smoothed Energy = (0.6 * 1.2) + (0.4 * 1.0) = 0.72 + 0.4 = 1.12
    # Smoothed Stress = (0.6 * 1.1) + (0.4 * 0.95) = 0.66 + 0.38 = 1.04
    # Multiplier = (1.12 + 1.04) / 2 = 2.16 / 2 = 1.08
    assert result == pytest.approx(1.08)


def test_run_low_energy_high_stress(smoother, mock_human_factor_history):
    """Test calculation with low energy and high stress."""
    current_hf = {'energy_level': 'Low', 'stress_level': 'High'}
    history = mock_human_factor_history(['Low', 'Normal'], ['High', 'Normal'])
    result = smoother.run(current_hf, history)

    # Current: Energy=0.8, Stress=0.8
    # History: Energy_avg = (0.8 + 1.0) / 2 = 0.9
    #          Stress_avg = (0.8 + 1.0) / 2 = 0.9
    # Smoothed Energy = (0.6 * 0.8) + (0.4 * 0.9) = 0.48 + 0.36 = 0.84
    # Smoothed Stress = (0.6 * 0.8) + (0.4 * 0.9) = 0.48 + 0.36 = 0.84
    # Multiplier = (0.84 + 0.84) / 2 = 0.84
    assert result == pytest.approx(0.84)


def test_run_unknown_levels_defaults_to_normal(smoother):
    """Test that unknown levels default to 'Normal' values (1.0)."""
    current_hf = {'energy_level': 'Unknown', 'stress_level': 'Invalid'}
    result = smoother.run(current_hf, [])
    # Should default to Normal (1.0) for both
    assert result == pytest.approx(1.0)


def test_run_mixed_history_and_current(smoother, mock_human_factor_history):
    """Test with a more complex mix of current and historical data."""
    current_hf = {'energy_level': 'High', 'stress_level': 'Normal'}
    history = mock_human_factor_history(['Low', 'High', 'Normal'], ['High', 'Low', 'Normal'])
    result = smoother.run(current_hf, history)

    # Current: Energy=1.2, Stress=1.0
    # History: Energy_avg = (0.8 + 1.2 + 1.0) / 3 = 3.0 / 3 = 1.0
    #          Stress_avg = (0.8 + 1.1 + 1.0) / 3 = 2.9 / 3 = 0.9666...
    # Smoothed Energy = (0.6 * 1.2) + (0.4 * 1.0) = 0.72 + 0.4 = 1.12
    # Smoothed Stress = (0.6 * 1.0) + (0.4 * (2.9/3)) = 0.6 + 0.4 * 0.9666... = 0.6 + 0.3866... = 0.9866...
    # Multiplier = (1.12 + 0.98666...) / 2 = 2.10666... / 2 = 1.05333...
    assert result == pytest.approx(1.05333, rel=1e-3)