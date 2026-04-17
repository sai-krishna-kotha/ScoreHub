from app.services.scoring.cricket import CricketEngine
from app.services.scoring.football import FootballEngine

def get_engine(sport_name: str):
    if sport_name.lower() == "cricket":
        print("\nCricket Engine is running!!\n")
        return CricketEngine()
    elif sport_name.lower() == "football":
        print("\nFootball Engine is running!!\n")
        return FootballEngine()
    else:
        raise Exception("Unsupported sport")