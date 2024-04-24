from .dynamodb import dynamodb
from .exceptions import QueryError, AuthError
from botocore.exceptions import ClientError
import sys
import os
from hashlib import sha256


class Users:
    def __init__(self):
        try:
            self.table = dynamodb.Table(os.environ["USER_TABLE"])
            self.table.load()
        except ClientError as e:
            print(e)
            raise QueryError()

    def get_user(self, token):
        try:
            if sys.getsizeof(token) != 128:
                print("Invalid user token size")
                raise AuthError()
            hashed = sha256(token)
        except Exception as e:
            print(f"Failed to hash user token")
            raise AuthError()
        try:
            dbresponse = self.table.get_item(Key={"pk": hashed.digest()})
        except ClientError as e:
            raise QueryError()
        if dbresponse:
            return dbresponse
        raise AuthError()

    def add_user(self, token, ip="", username="Anonymous"):
        hashed = sha256(token.bytes)
        try: 
            self.table.put_item(
                Item={
                    'pk': hashed.digest(),
                    'score': 0,
                    'username': username,
                    'lastIP': ip,
                    'questionsSeen': []
                }
            )
        except ClientError as e:
            print(f"Error saving user to DB: {e}")
            raise QueryError()

