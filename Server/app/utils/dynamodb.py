import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def get_dynamodb_resource():
    """
    Initializes and returns a DynamoDB resource.
    """
    return boto3.resource(
        'dynamodb',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

def get_table_name(base_name):
    """
    Returns the full table name with prefix.
    """
    prefix = os.getenv('DYNAMODB_TABLE_PREFIX', '')
    return f"{prefix}{base_name}"

# Shared resource instance
dynamodb = get_dynamodb_resource()
