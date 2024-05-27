from datetime import datetime

from common import dynamodb
from common.exceptions import QueryError
from packages.botocore.exceptions import ClientError
from common.logger import getLogger
import os


class GameData:
    """Wrapper for game-related DynamoDB queries"""
    def __init__(self, logger=getLogger("GameData")):
        self.logger = logger
        try:
            self.table = dynamodb.resource.Table(os.environ["GAME_TABLE"])
            self.table.load()
        except ClientError as e:
            self.logger.error(f"Error loading games table ({os.environ["GAME_TABLE"]}): {e}")
            raise QueryError()

    def now_playing(self, venue_id: str):
        try:
            db_response = self.table.query(KeyConditionExpression="venue_id = :venue_id and #end > :now",
                                           FilterExpression="#start < :now",
                                           ExpressionAttributeNames={'#end': 'end', '#start': 'start',},
                                           Limit=1,
                                           ExpressionAttributeValues={':venue_id': venue_id, ':now': datetime.utcnow().isoformat()})
        except ClientError as e:
            self.logger.error(f"Error searching for current game: {e}")
            raise QueryError()
        if len(db_response.get('Items', [])) == 1:
            self.logger.info(f"Found current game at venue #{venue_id}: {db_response['Items'][0]}")
            return db_response['Items'][0]
        else:
            self.logger.info(f"No current game found at venue #{venue_id}")

    def add(self, venue_id: str, games: list[dict(start="", end="", teams=[], max_session=-1, questions_per_session=10)]):
        try:
            with self.table.batch_writer() as writer:
                for game in games:
                    game['venue_id'] = venue_id
                    writer.put_item(Item=game)
        except ClientError as e:
            self.logger.error(f"Error saving game data to DB: {e}")
            raise QueryError()
        self.logger.info(f"Saved {len(games)} new games to db.")

    def list(self, venue_id: str | None = None):
        try:
            if not venue_id:
                db_response = self.table.scan()
                self.logger.info(f"DB response to scan: {db_response}")
                return db_response.get('Items', [])
            db_response = self.table.query(KeyConditionExpression="venue_id = :venue_id",
                                           ExpressionAttributeValues={':venue_id': venue_id,})
            return db_response.get('Items', [])
        except ClientError as e:
            self.logger.error(f"Error scanning game data: {e}")
            raise QueryError()