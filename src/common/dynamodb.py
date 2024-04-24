import os
import boto3

if os.environ.get('AWS_SAM_LOCAL', False):
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://host.docker.internal:8000')
else:
    dynamodb = boto3.resource('dynamodb')

