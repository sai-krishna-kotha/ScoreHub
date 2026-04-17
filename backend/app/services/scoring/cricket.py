from .base import BaseScoringEngine

class CricketEngine(BaseScoringEngine):

    def calculate_score(self, events):
        runs = 0
        wickets = 0
        balls = 0

        for e in events:
            if e.event_type == "BALL":
                runs += e.payload.get("runs", 0)
                balls += 1

            elif e.event_type == "WICKET":
                wickets += 1
                balls += 1

        overs = f"{balls//6}.{balls%6}"

        return {
            "runs": runs,
            "wickets": wickets,
            "overs": overs
        }