from common import dynamodb
from common.exceptions import QueryError, NoMoreQuestionsError, QuestionNotFoundError
from packages.botocore.exceptions import ClientError
from common.logger import getLogger
import os


class QuestionData:
    """Wrapper for DynamoDB question table queries."""
    def __init__(self, logger=getLogger("QuestionData")):
        self.logger = logger
        try:
            self.table = dynamodb.resource.Table(os.environ["QUESTION_TABLE"])
            self.table.load()
        except ClientError as e:
            self.logger.error(f"Error loading Questions table ({os.environ["QUESTION_TABLE"]}): {e}")
            raise QueryError()

    def get_next(self, team: str, after: str | int) -> dict:
        """Returns the first question available for a team with an index higher than after."""
        try:
            # TODO: make sure this never returns the metadata
            db_response = self.table.query(KeyConditionExpression="team = :team and sk > :after",
                                           Limit=1,
                                           ExpressionAttributeValues={':team': team, ':after': str(after)})
        except ClientError as e:
            self.logger.error(f"Error getting next question from db: {e}")
            raise QueryError()
        self.logger.info(f"DynamoDB response to next question query: {db_response}")
        if items := db_response.get("Items"):
            if len(items) > 0:
                self.logger.info(f"DynamoDB response to next question query: {db_response}")
                return items[0]
        self.logger.info(f"No more questions found in response, raising NoMoreQuestionsError")
        raise NoMoreQuestionsError()

    def add(self, team: str, qas: list):
        """Adds a list of q/a dicts to the database for ONE team."""
        try:
            cter = self.table.get_item(Key={"team": team, "sk": "meta"})
            count = cter.get('team_question_count', 0)
            next_index = cter.get('next_unused_sk', 0)
            self.logger.info(f"Adding new questions with indices {next_index} - {next_index + len(qas)} for team {team}")
            with self.table.batch_writer() as writer:
                for qa in qas:
                    writer.put_item(Item={
                        'team': team,
                        'sk': str(next_index),
                        'question': qa['question'],
                        'answer_options': qa['answer_options'],
                        'correct_indices': qa['correct_indices'],
                    })
                    next_index += 1
                writer.put_item(Item={
                    'team': team,
                    'sk': "meta",
                    'team_question_count': count + len(qas),
                    'next_unused_sk': next_index,
                })
        except ClientError as e:
            self.logger.error(f"Error saving questions to DB: {e}")
            raise QueryError()

    def list(self, team: str | None = None):
        try:
            if not team:
                db_response = self.table.scan()
                return db_response.get('Items', [])
            db_response = self.table.query(KeyConditionExpression="team = :team",
                                           ExpressionAttributeValues={':team': team,})
            return db_response.get('Items', [])
        except ClientError as e:
            self.logger.error(f"Error scanning question data: {e}")
            raise QueryError()

