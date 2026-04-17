from .base import BaseScoringEngine

class FootballEngine(BaseScoringEngine):

    def calculate_score(self, events):
        goals = 0

        for e in events:
            if e.event_type == "GOAL":
                goals += 1

        return {"goals": goals}