# app/core/tutor_engine/tutor_config.py

# --- Diagnoser Configuration ---
DECAY_RATE = 0.1
TARGET_QUESTIONS_FOR_CONFIDENCE = 200
MASTERY_TARGET = 0.90
CONQUER_THRESHOLD = 0.80
MIN_CYCLES_IN_STATE_FOR_REGRESSION = 3
MASTERY_DROP_THRESHOLD_FOR_REGRESSION = 0.20 # 20% drop

# Defines the progression of states for Hysteresis Gate logic.
STATE_PROGRESSION = ['DISCOVERY', 'DEEP_WORK', 'CONQUER', 'CEMENT', 'MAINTAIN']
