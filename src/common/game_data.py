from common import dynamodb
from common.exceptions import QueryError
from packages.botocore.exceptions import ClientError
import os


class GameData:
    """Wrapper for game-related DynamoDB queries"""
    def __init__(self):
        return # bypass table load for now
        try:
            self.table = dynamodb.resource.Table(os.environ["GAME_TABLE"])
            self.table.load()
        except ClientError as e:
            print(e)
            raise QueryError()

    def now_playing(self, venue_id: int):
        # TODO: get the data from db
        return {
                "id": 0,
                "teams": ("Anteaters", "Bruins"),
                "start": "2024-04-01T00:00:00",
                "end": "2024-06-01T00:00:00",
                "max_sessions": 100,
                "questions_per_session": 10,
        }

    def add(self, venue_id, teams, start_time, end_time):
        raise NotImplementedError() # TODO: implement
