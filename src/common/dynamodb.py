import os
from packages import boto3


"""Shared DynamoDB resource."""
if os.environ.get('AWS_SAM_LOCAL', False):
    resource = boto3.resource('dynamodb', endpoint_url='http://host.docker.internal:8000')
else:
    resource = boto3.resource('dynamodb')

