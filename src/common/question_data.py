from common import dynamodb
from common.exceptions import QueryError, NoMoreQuestionsError, QuestionNotFoundError
from packages.botocore.exceptions import ClientError
import os


class QuestionData:
    """Wrapper for DynamoDB question table queries."""
    def __init__(self):
        try:
            self.table = dynamodb.resource.Table(os.environ["QUESTION_TABLE"])
            self.table.load()
        except ClientError as e:
            print(e)
            raise QueryError()

    def get_next(self, team: str, after: str | int) -> dict:
        """Returns the first question available for a team with an index higher than after."""
        try:
            # TODO: make sure this never returns the counters
            db_response = self.table.query(KeyConditionExpression="team = :team and sk > :after",
                                           Limit=1,
                                           ExpressionAttributeValues={':team': team, ':after': str(after)})
        except ClientError as e:
            raise QueryError()
        print(db_response)
        if items := db_response.get("Items"):
            if len(items) > 0:
                return items[0]
        raise NoMoreQuestionsError()

    def add(self, team: str, qas: list):
        """Adds a list of q/a dicts to the database for ONE team."""
        try:
            cter = self.table.get_item(Key={"team": team, "sk": "counters"})
            count = cter.get('team_question_count', 0)
            next_index = cter.get('next_unused_sk', 0)
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
                    'sk': "counters",
                    'team_question_count': count + len(qas),
                    'next_unused_sk': next_index,
                })
        except ClientError as e:
            print(f"Error saving questions to DB: {e}")
            raise QueryError()

