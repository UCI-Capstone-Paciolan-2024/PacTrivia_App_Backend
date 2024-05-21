from common import dynamodb
from common.exceptions import QueryError
from packages.botocore.exceptions import ClientError
from common.logger import getLogger
import os


class VenueData:
    """Wrapper for venue DynamoDB table queries."""
    def __init__(self, logger=getLogger("VenueData")):
        self.logger = logger
        return  # bypass table load for now (TODO)
        try:
            self.table = dynamodb.resource.Table(os.environ["VENUE_TABLE"])
            self.table.load()
        except ClientError as e:
            self.logger.error(f"Error loading venue table ({os.environ["VENUE_TABLE"]}): {e}")
            raise QueryError()

    def find_nearby(self, coords=None, radius_m=500):
        """Return a list of venues near the given coordinates."""
        # TODO: get the data from db by coordinate
        return [
            {"id": 0,
             "name": "UCI Bren Events Center",
             "distance": 0,
             },
        ]

    def add(self, name, coords):
        """Add a new venue to the database."""
        raise NotImplementedError() # TODO: implement

    def list(self, name, coords):
        """List all venues in database."""
        raise NotImplementedError() # TODO: implement
