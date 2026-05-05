from .base import BaseScoringEngine

class CricketEngine(BaseScoringEngine):

    def calculate_score(self, events):
        score = {}

        for e in events:
            # 🔥 Team + Phase keys
            team_id = e.team_id

            phase_key = getattr(e, "phase_number", None)
            if phase_key is None:
                phase_key = e.phase_id

            if team_id not in score:
                score[team_id] = {}

            if phase_key not in score[team_id]:
                score[team_id][phase_key] = {
                    "runs": 0,
                    "wickets": 0,
                    "balls": 0
                }

            if e.event_type == "BALL":
                score[team_id][phase_key]["runs"] += e.payload.get("runs", 0)
                score[team_id][phase_key]["balls"] += 1

            elif e.event_type == "WICKET":
                score[team_id][phase_key]["wickets"] += 1
                score[team_id][phase_key]["balls"] += 1

        # 🔥 Format output
        final_output = {}

        for team_id, phases in score.items():
            ordered_phases = []
            total_runs = 0
            total_wickets = 0

            for key in sorted(phases.keys()):
                p = phases[key]
                balls = p["balls"]
                overs = f"{balls // 6}.{balls % 6}"

                ordered_phases.append({
                    "phase": key,
                    "runs": p["runs"],
                    "wickets": p["wickets"],
                    "overs": overs
                })

                total_runs += p["runs"]
                total_wickets += p["wickets"]

            final_output[team_id] = {
                "phases": ordered_phases,
                "total": {
                    "runs": total_runs,
                    "wickets": total_wickets
                }
            }

        return final_output