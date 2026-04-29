from app.utils.dynamodb import dynamodb, get_table_name
from app.schemas.models import InterestSchema
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

class Interest:
    table = dynamodb.Table(get_table_name('interests'))

    @classmethod
    def get_by_user(cls, user_id):
        """
        Retrieves interests for a specific user.
        Returns a single InterestSchema or None.
        """
        try:
            response = cls.table.scan(
                FilterExpression=Attr('user_id').eq(user_id)
            )
            items = response.get('Items', [])
            if items:
                return InterestSchema(**items[0])
            return None
        except ClientError as e:
            print(f"Error fetching interests: {e.response['Error']['Message']}")
            return None

    @classmethod
    def create(cls, interest_data: InterestSchema):
        """
        Creates a new interest record in DynamoDB.
        """
        try:
            item_dict = interest_data.model_dump(mode='json')
            cls.table.put_item(Item=item_dict)
            return True
        except ClientError as e:
            print(f"Error creating interest: {e.response['Error']['Message']}")
            return False

    @classmethod
    def update(cls, interest_id, keywords, categories):
        """
        Updates an existing interest record.
        """
        try:
            cls.table.update_item(
                Key={'interest_id': interest_id},
                UpdateExpression='SET keywords = :k, categories = :c',
                ExpressionAttributeValues={
                    ':k': keywords,
                    ':c': categories
                }
            )
            return True
        except ClientError as e:
            print(f"Error updating interest: {e.response['Error']['Message']}")
            return False

    @classmethod
    def list_all(cls, limit=100):
        """
        Lists all interests (used by trigger engine to match against all users).
        """
        try:
            response = cls.table.scan(Limit=limit)
            return [InterestSchema(**item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error listing interests: {e.response['Error']['Message']}")
            return []
