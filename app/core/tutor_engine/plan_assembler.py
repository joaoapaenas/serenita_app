# app/core/tutor_engine/plan_assembler.py

import logging
from typing import List, Dict, Any

log = logging.getLogger(__name__)


def _create_plan_from_allocation(allocation_map: Dict[str, float], focus_mode: str,
                                  processed_subjects: List[Dict[str, Any]],
                                  maintain_subjects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper to build a single plan structure from a time allocation map."""
    print(f"  _create_plan_from_allocation received allocation_map: {allocation_map}")
    sessions = []
    # Create a map for quick lookup of subject data by subject_id
    subject_data_map = {s['subject_id']: s for s in processed_subjects + maintain_subjects}

    for subject_id, allocated_minutes_float in allocation_map.items():
        allocated_minutes = round(allocated_minutes_float)
        if allocated_minutes > 0:
            subject_data = subject_data_map.get(subject_id)
            if subject_data:
                sessions.append({
                    'subject_name': subject_data['subject_name'],
                    'subject_id': subject_id,
                    'allocated_minutes': allocated_minutes,
                    'reasoning': subject_data['reasoning'],
                    'strategic_mode': subject_data['diagnostics']['strategic_mode']
                })

    # Add maintain subjects with a fixed small time block if not already in allocation_map
    for subject_data in maintain_subjects:
        if subject_data['subject_id'] not in allocation_map:
            sessions.append({
                'subject_name': subject_data['subject_name'],
                'subject_id': subject_data['subject_id'],
                'allocated_minutes': 30,  # Fixed maintenance time
                'reasoning': subject_data['reasoning'],
                'strategic_mode': 'MAINTAIN'
            })

    return {
        'focus_mode': focus_mode,
        'description': f"A {focus_mode.lower()}-focus plan for this cycle.",
        'sessions': sorted(sessions, key=lambda x: x['allocated_minutes'], reverse=True)
    }


class PlanAssembler:
    """
    Generates the dual Tactical and Strategic plan views based on the
    processed subject data. (v20 spec Batch 6)
    """

    def __init__(self, processed_subjects: List[Dict[str, Any]], cycle_config: Dict[str, Any]):
        self.processed_subjects = [s for s in processed_subjects if s['diagnostics']['strategic_mode'] != 'MAINTAIN']
        self.maintain_subjects = [s for s in processed_subjects if s['diagnostics']['strategic_mode'] == 'MAINTAIN']
        self.cycle_config = cycle_config

    def _dispatch_time_allocation(self) -> Dict[str, float]:
        """Selects the time allocation strategy based on the cycle configuration."""
        strategy = self.cycle_config.get('timing_strategy', 'Adaptive')
        log.info(f"Using '{strategy}' timing strategy for plan generation.")

        if strategy == 'Fixed':
            return self._allocate_time_fixed()
        elif strategy == 'Basic':
            return self._allocate_time_basic()
        else:  # Default to Adaptive
            return self._allocate_time_adaptive()

    def _allocate_time_fixed(self) -> Dict[str, float]:
        """Gives every subject the same fixed block duration."""
        fixed_time = self.cycle_config.get('block_duration_min', 60)
        return {s['subject_id']: float(fixed_time) for s in self.processed_subjects}

    def _allocate_time_basic(self) -> Dict[str, float]:
        """Groups subjects into three time tiers: 45, 60, 90 min."""
        time_map = {}
        if not self.processed_subjects:
            return time_map

        priorities = [s['final_priority'] for s in self.processed_subjects]
        min_p, max_p = min(priorities), max(priorities)

        # If all priorities are the same, give everyone medium time
        if min_p == max_p:
            return {s['subject_id']: 60.0 for s in self.processed_subjects}

        range_p = max_p - min_p
        # Avoid division by zero if there's only one subject or all have same priority
        if range_p == 0:
            return {s['subject_id']: 60.0 for s in self.processed_subjects}

        tier_1_threshold = min_p + range_p * 0.33
        tier_2_threshold = min_p + range_p * 0.66

        for s in self.processed_subjects:
            priority = s['final_priority']
            if priority <= tier_1_threshold:
                time_map[s['subject_id']] = 45.0  # Low priority
            elif priority <= tier_2_threshold:
                time_map[s['subject_id']] = 60.0  # Medium priority
            else:
                time_map[s['subject_id']] = 90.0  # High priority
        return time_map

    def _allocate_time_adaptive(self) -> Dict[str, float]:
        """Calculates time proportionally, then rounds and clamps it."""
        total_priority = sum(s['final_priority'] for s in self.processed_subjects)
        available_time = self.cycle_config.get('available_time_minutes', 0)

        if total_priority == 0:
            return {s['subject_id']: 40.0 for s in self.processed_subjects}  # Give minimum if no priority

        time_map = {}
        for s in self.processed_subjects:
            proportional_time = (s['final_priority'] / total_priority) * available_time
            # Round to nearest 10, then clamp between 40 and 110
            rounded_time = round(proportional_time / 10.0) * 10
            clamped_time = max(40.0, min(110.0, float(rounded_time)))
            time_map[s['subject_id']] = clamped_time
        log.debug(f"Adaptive time allocation: {time_map}")
        return time_map

    def generate_strategic_view(self) -> (Dict[str, Any], Dict[str, float]):
        """
        Generates the high-level plan_scaffold with a recommended plan and
        1-2 alternatives. (v20 spec 6.2)
        """
        allocated_time_map = self._dispatch_time_allocation()
        recommended_plan = _create_plan_from_allocation(allocated_time_map, "Balanced",
                                                        self.processed_subjects, self.maintain_subjects)

        alternative_plans = []
        deep_work_plan = self._generate_deep_work_plan(allocated_time_map)
        if deep_work_plan:
            alternative_plans.append(deep_work_plan)

        review_plan = self._generate_review_reinforce_plan(allocated_time_map)
        if review_plan:
            alternative_plans.append(review_plan)

        plan_scaffold = {
            'recommended_plan': recommended_plan,
            'alternative_plans': alternative_plans
        }
        return plan_scaffold, allocated_time_map

    def _generate_deep_work_plan(self, base_allocated_time_map: Dict[str, float]) -> Dict[str, Any] | None:
        """Focuses heavily on the top 1-2 priority subjects."""
        candidates = [s for s in self.processed_subjects if
                      s['diagnostics']['strategic_mode'] in ['DEEP_WORK', 'CONQUER']]

        if not candidates:
            return None

        focus_subjects = sorted(candidates, key=lambda x: x['final_priority'], reverse=True)[:2]
        focus_subject_ids = {s['subject_id'] for s in focus_subjects}
        other_subjects = [s for s in self.processed_subjects if s['subject_id'] not in focus_subject_ids]
        print(f"  _generate_deep_work_plan: candidates={candidates}")
        print(f"  _generate_deep_work_plan: focus_subjects={focus_subjects}")
        print(f"  _generate_deep_work_plan: other_subjects={other_subjects}")

        available_time = self.cycle_config.get('available_time_minutes', 0)

        deep_work_allocation = {}

        # Allocate 70% of available_time to focus subjects, 30% to others
        time_for_focus_group = available_time * 0.70
        time_for_others_group = available_time * 0.30

        focus_priority_total = sum(s['final_priority'] for s in focus_subjects)
        print(f"  _generate_deep_work_plan: focus_priority_total={focus_priority_total}")
        if focus_priority_total > 0:
            for s in focus_subjects:
                deep_work_allocation[s['subject_id']] = (s['final_priority'] / focus_priority_total) * time_for_focus_group

        others_priority_total = sum(s['final_priority'] for s in other_subjects)
        print(f"  _generate_deep_work_plan: others_priority_total={others_priority_total}")
        if others_priority_total > 0:
            for s in other_subjects:
                deep_work_allocation[s['subject_id']] = (s['final_priority'] / others_priority_total) * time_for_others_group
        log.debug(f"Deep work allocation: {deep_work_allocation}")
        return _create_plan_from_allocation(deep_work_allocation.copy(), "Deep Work",
                                            self.processed_subjects, self.maintain_subjects)

    def _generate_review_reinforce_plan(self, base_allocated_time_map: Dict[str, float]) -> Dict[str, Any] | None:
        """Prioritizes subjects in CEMENT or those with low durability."""
        candidates = [s for s in self.processed_subjects if
                      s['diagnostics']['strategic_mode'] == 'CEMENT' or s['diagnostics']['durability_factor'] < 0.6]
        if not candidates:
            return None

        review_allocation = base_allocated_time_map.copy() # Use the passed base map
        candidate_ids = {c['subject_id'] for c in candidates}
        for subject_id in review_allocation:
            if subject_id not in candidate_ids:
                review_allocation[subject_id] /= 2

        log.debug(f"Review & Reinforce allocation: {review_allocation}")
        return _create_plan_from_allocation(review_allocation.copy(), "Review & Reinforce",
                                            self.processed_subjects, self.maintain_subjects)

    def generate_tactical_view(self, allocated_time_map: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generates the detailed, day-by-day sequenced_plan of WorkUnits.
        (v20 spec 6.1)

        NOTE: This is a simplified implementation. A full implementation would
        require more complex logic for interleaving and daily distribution.
        """
        sequenced_plan = []
        all_subjects_map = {s.id: s for s in self.cycle_config['subjects']}

        # 1. Task Packing
        scheduled_tasks = []
        for subject_data in self.processed_subjects:
            subject_id = subject_data['subject_id']
            time_for_subject = allocated_time_map.get(subject_id, 0)

            original_subject = all_subjects_map.get(subject_id)
            if not original_subject or not original_subject.work_units:
                continue

            time_used = 0
            # --- Schedule all tasks within budget, passing completion status ---
            for work_unit in original_subject.work_units:
                if (time_used + work_unit.estimated_time_minutes) <= time_for_subject:
                    scheduled_tasks.append({
                        'subject_name': subject_data['subject_name'],
                        'subject_id': subject_id,
                        'work_unit_id': work_unit.unit_id,
                        'work_unit_title': work_unit.title,
                        'allocated_minutes': work_unit.estimated_time_minutes,
                        'reasoning': subject_data['reasoning'],
                        'is_completed': work_unit.is_completed  # Pass completion status
                    })
                    if not work_unit.is_completed:
                        time_used += work_unit.estimated_time_minutes

        # 2. Daily Sequencing (Simplified)
        cycle_days = self.cycle_config.get('cycle_duration_days', 7)
        if cycle_days == 0: cycle_days = 1

        for i, task in enumerate(scheduled_tasks):
            day_index = i % cycle_days
            task['day_index'] = day_index
            sequenced_plan.append(task)

        return sequenced_plan