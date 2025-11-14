# app/core/tutor_engine/priority_strategies.py
from typing import Protocol

class IPriorityStrategy(Protocol):
    def calculate(self, points: int, mastery: float, confidence: float, durability: float) -> float: ...

class DiscoveryPriorityStrategy:
    def calculate(self, points, **kwargs):
        return 50 + (points * 10)

class DeepWorkPriorityStrategy:
    def calculate(self, points, mastery, confidence, **kwargs):
        confidence_modulator = 0.4 + (0.6 * confidence)
        return (50 + (points * 5) + (1.0 - mastery) * 50) * confidence_modulator

class ConquerPriorityStrategy:
    def calculate(self, points, mastery, confidence, **kwargs):
        confidence_modulator = 0.4 + (0.6 * confidence)
        return (90 + mastery * 20 + points * 2) * confidence_modulator

class CementPriorityStrategy:
    def calculate(self, points, durability, confidence, **kwargs):
        confidence_modulator = 0.4 + (0.6 * confidence)
        return (40 + (1.0 - durability) * 40 + points * 3) * confidence_modulator

class MaintainPriorityStrategy:
    def calculate(self, points, confidence, **kwargs):
        confidence_modulator = 0.4 + (0.6 * confidence)
        return (10 + points * 2) * confidence_modulator
