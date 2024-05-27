import random

from common import dynamodb
from common.exceptions import QueryError, NoMoreQuestionsError, QuestionNotFoundError, IntegrityError
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

    def get_random_set(self, teams: [dict(name=None, exclude_sks=None, meta=None)], n: int):
        """Returns a total of n random questions across teams."""
        self.logger.info("Starting random question set selection")
        questions = []
        for i in range(n):
            team = None
            while teams and not team:
                tmp = random.sample(teams, 1)[0] if len(teams) > 1 else teams[0]
                if int(tmp['meta'].get('team_question_count', 0)) > len(tmp['exclude_sks']):
                    team = tmp
                else:
                    teams.remove(tmp)
            if not team:
                raise NoMoreQuestionsError(f"Requested number of questions ({n}) is greater than available.")
            self.logger.info(f"Selected team {team} for question index {i}")
            try:
                random_max = int(team['meta'].get('next_unused_sk', 0)) - 1
                question = None
                while (not question) and len(team['exclude_sks']) <= random_max:
                    rnd = random.randint(0, random_max)
                    self.logger.info(f"Trying index {rnd}")
                    if rnd in team['exclude_sks']:
                        self.logger.info(f"Excluded, retrying")
                        continue
                    elif (len(q := (self.table.query(KeyConditionExpression="team = :team and sk = :qsk",
                                               Limit=1,
                                               ExpressionAttributeValues={':team': team['name'],
                                                                          ':qsk': str(rnd)}).get('Items', []))) > 0):
                        self.logger.info(f"Question found: {q}")
                        question = q[0]
                    else:
                        self.logger.info(f"Not found")
                    team['exclude_sks'].add(rnd)
                if question:
                    questions.append(question)
                else:
                    self.logger.error(f"Could not find question for {team}")
                    raise IntegrityError("Could not find a question, likely incorrect team metadata")
            except ClientError as e:
                raise QueryError("Failed to retrieve a question")
        return questions

    def get_team_meta(self, team: str) -> dict:
        """Returns the metadata for the team (# of questions, logo, etc.)"""
        try:
            if meta := self.table.get_item(Key={"team": team, "sk": "meta"}).get('Item', {}):
                self.logger.info(f"Metadata found for {team}: {meta}")
                return meta
            raise IntegrityError(f"Could not find metadata for team {team}")
        except ClientError as e:
            self.logger.error(f"Error getting team metadata from db: {e}")
            raise QueryError()

    def update_logo(self, team: str, logo_url: str) -> dict:
        """Updates the logo for a team (team must already exist)."""
        try:
            old = self.table.update_item(
                Key={"team": team, "sk": "meta"},
                UpdateExpression="set #logo=:logo",
                ExpressionAttributeNames={
                    '#logo': 'logo',
                },
                ExpressionAttributeValues={
                    ':logo': logo_url,
                },
                ReturnValues="UPDATED_OLD"
            )
            self.logger.info(f"Updated logo for {team} from {old.get('Attributes', {}).get('logo', None)} to {logo_url}")
        except ClientError as e:
            self.logger.error(f"Error updating team logo: {e}")
            raise QueryError("Failed to update logo")

    def add(self, team: str, qas: list):
        """Adds a list of q/a dicts to the database for ONE team."""
        try:
            meta = self.table.get_item(Key={"team": team, "sk": "meta"}).get('Item', {})
            count = meta.get('team_question_count', 0)
            next_index = meta.get('next_unused_sk', 0)
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

