from app.utils.dynamodb import dynamodb, get_table_name
from app.schemas.models import UserSchema
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

class User:
    table = dynamodb.Table(get_table_name('users'))

    @classmethod
    def get_by_id(cls, user_id):
        """
        Retrieves a user by their user_id.
        """
        try:
            response = cls.table.get_item(Key={'user_id': user_id})
            if 'Item' in response:
                return UserSchema(**response['Item'])
            return None
        except ClientError as e:
            print(f"Error fetching user: {e.response['Error']['Message']}")
            return None

    @classmethod
    def create(cls, user_data: UserSchema):
        """
        Creates a new user in DynamoDB.
        """
        try:
            # Convert to JSON-compatible dict (converts datetime to ISO string)
            item_dict = user_data.model_dump(mode='json')
            cls.table.put_item(Item=item_dict)
            return True
        except ClientError as e:
            print(f"Error creating user: {e.response['Error']['Message']}")
            return False

    @classmethod
    def get_by_email(cls, email):
        """
        Retrieves a user by their email using a table scan.
        """
        try:
            response = cls.table.scan(
                FilterExpression=Attr('email').eq(email)
            )
            items = response.get('Items', [])
            if items:
                return UserSchema(**items[0])
            return None
        except ClientError as e:
            print(f"Error fetching user by email: {e.response['Error']['Message']}")
            return None

    @classmethod
    def get_by_tenant(cls, tenant_id):
        """
        Retrieves all users for a specific tenant using the GSI.
        """
        try:
            response = cls.table.query(
                IndexName='TenantIndex',
                KeyConditionExpression='tenant_id = :tid',
                ExpressionAttributeValues={':tid': tenant_id}
            )
            return [UserSchema(**item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error querying users by tenant: {e.response['Error']['Message']}")
            return []
