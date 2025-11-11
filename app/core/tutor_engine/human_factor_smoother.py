# app/core/tutor_engine/human_factor_smoother.py

import logging
from typing import Dict, Any

log = logging.getLogger(__name__)


class HumanFactorSmoother:
    """Calculates the CognitiveCapacityMultiplier for the cycle, as per v20 spec 4.1.1."""

    ENERGY_MAP = {'High': 1.2, 'Normal': 1.0, 'Low': 0.8}
    STRESS_MAP = {'High': 0.8, 'Normal': 1.0, 'Low': 1.1}

    def run(self, current_human_factor: Dict[str, Any], history: list) -> float:
        """Calculates and returns the CognitiveCapacityMultiplier."""
        current_energy = self.ENERGY_MAP.get(current_human_factor.get('energy_level'), 1.0)
        current_stress = self.STRESS_MAP.get(current_human_factor.get('stress_level'), 1.0)

        if not history:
            hist_avg_energy = 1.0
            hist_avg_stress = 1.0
        else:
            hist_avg_energy = sum(self.ENERGY_MAP.get(h.energy_level, 1.0) for h in history) / len(history)
            hist_avg_stress = sum(self.STRESS_MAP.get(h.stress_level, 1.0) for h in history) / len(history)

        smoothed_energy = (0.6 * current_energy) + (0.4 * hist_avg_energy)
        smoothed_stress = (0.6 * current_stress) + (0.4 * hist_avg_stress)

        cognitive_capacity_multiplier = (smoothed_energy + smoothed_stress) / 2.0
        log.debug(f"Calculated CognitiveCapacityMultiplier: {cognitive_capacity_multiplier:.3f}")
        return cognitive_capacity_multiplier
