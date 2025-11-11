# app/core/tutor_engine/reasoning_engine.py

import logging

log = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Generates a clear, actionable reasoning string for a subject based on
    a hierarchical set of rules. (v20 spec Batch 5)
    """

    @staticmethod
    def generate_reasoning(diagnostics: dict, flags: dict) -> str:
        """
        Takes diagnostics and flags and returns the first matching reason
        from the v20 hierarchy.
        """
        if flags.get('roi_warning'):
            return (
                "Strategic Warning: You have invested a significant amount of time into this "
                "low-value topic with limited progress. The tutor recommends de-prioritizing "
                "it to focus on subjects with greater impact."
            )

        if flags.get('urgency_shock'):
            return (
                "Urgent Priority: This subject's importance has recently increased. "
                "It is a top priority to address it this cycle."
            )

        if diagnostics.get('mastery_confidence_score', 1.0) < 0.4:
            return (
                "Based on limited data, our top priority is to complete a diagnostic problem "
                "set to get a more accurate picture of your mastery."
            )

        if diagnostics['strategic_mode'] == 'CONQUER' and diagnostics.get('learning_velocity', 1.0) < 0.01:
            return (
                "Your progress has stalled. The tutor recommends trying a new study method "
                "or focusing on targeted problem sets to break through the plateau."
            )

        if diagnostics['strategic_mode'] == 'CEMENT':
            topics = diagnostics.get('mastery_by_topic', {})
            if topics:
                weakest_topic = min(topics, key=topics.get)
                return (
                    f"Your overall mastery is good, but your performance on '{weakest_topic}' is lagging. "
                    "This cycle's goal is to cement this specific weak point."
                )

        mode = diagnostics.get('strategic_mode')
        if mode == 'DISCOVERY':
            if flags.get('discovery_boost_applied'):
                return "Top Priority: This is one of your newest subjects. This week's goal is to start it and build momentum."
            else:
                return (
                    "Low Priority: This is a new subject in your Discovery Queue. It will be "
                    "prioritized in an upcoming cycle after you've established your current focus subjects."
                )
        if mode == 'CONQUER':
            return "Final Push: You are close to mastering this subject. This cycle's focus is on reaching the finish line."
        if mode == 'DEEP_WORK':
            return "Consistent effort is key. The goal is to continue building your foundational knowledge in this subject."
        if mode == 'MAINTAIN':
            return "Maintenance: A short review session is scheduled to ensure you retain this knowledge long-term."

        log.warning(f"No specific reasoning rule matched for mode '{mode}'. Using fallback.")
        return "A standard study session has been scheduled for this subject based on its current priority."
