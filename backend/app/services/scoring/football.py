from .base import BaseScoringEngine

class FootballEngine(BaseScoringEngine):

    def calculate_score(self, events):
        phases = {}

        for e in events:
            # Prefer phase_number if available
            phase_key = getattr(e, "phase_number", None)
            if phase_key is None:
                phase_key = e.phase_id

            if phase_key not in phases:
                phases[phase_key] = {"goals": 0}

            if e.event_type == "GOAL":
                phases[phase_key]["goals"] += 1

        # Order phases + compute total
        ordered_phases = []
        total_goals = 0

        for key in sorted(phases.keys()):
            goals = phases[key]["goals"]

            ordered_phases.append({
                "phase": key,
                "goals": goals
            })

            total_goals += goals

        return {
            "phases": ordered_phases,
            "total": {
                "goals": total_goals
            }
        }