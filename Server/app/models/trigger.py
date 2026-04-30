from app.utils.dynamodb import dynamodb, get_table_name
from app.schemas.models import TriggerSchema
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

class Trigger:
    table = dynamodb.Table(get_table_name('triggers'))

    @classmethod
    def get_by_user(cls, user_id, limit=50):
        """
        Retrieves all triggers for a specific user, sorted by newest first.
        """
        try:
            response = cls.table.scan(
                FilterExpression=Attr('user_id').eq(user_id),
                Limit=limit
            )
            items = response.get('Items', [])
            triggers = [TriggerSchema(**item) for item in items]
            triggers.sort(key=lambda t: t.created_at, reverse=True)
            return triggers
        except ClientError as e:
            print(f"Error fetching triggers: {e.response['Error']['Message']}")
            return []

    @classmethod
    def get_unread_count(cls, user_id):
        """
        Returns the count of unread triggers for a user.
        """
        try:
            response = cls.table.scan(
                FilterExpression=Attr('user_id').eq(user_id) & Attr('sent').eq(False),
                Select='COUNT'
            )
            return response.get('Count', 0)
        except ClientError as e:
            print(f"Error counting triggers: {e.response['Error']['Message']}")
            return 0

    @classmethod
    def create(cls, trigger_data: TriggerSchema):
        """
        Creates a new trigger record in DynamoDB.
        """
        try:
            item_dict = trigger_data.model_dump(mode='json')
            cls.table.put_item(Item=item_dict)
            return True
        except ClientError as e:
            print(f"Error creating trigger: {e.response['Error']['Message']}")
            return False

    @classmethod
    def mark_as_read(cls, trigger_id):
        """
        Marks a trigger as read/sent.
        """
        try:
            cls.table.update_item(
                Key={'trigger_id': trigger_id},
                UpdateExpression='SET sent = :s',
                ExpressionAttributeValues={':s': True}
            )
            return True
        except ClientError as e:
            print(f"Error marking trigger as read: {e.response['Error']['Message']}")
            return False

    @classmethod
    def get_all(cls, limit=200):
        """
        Lists all triggers (used by analytics engine).
        """
        try:
            response = cls.table.scan(Limit=limit)
            return [TriggerSchema(**item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error listing triggers: {e.response['Error']['Message']}")
            return []

    @classmethod
    def count_recent(cls, hours=24):
        """
        Returns the count of triggers created in the last N hours (for analytics).
        Falls back to scan since we don't have a time-based GSI.
        """
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        try:
            response = cls.table.scan(
                FilterExpression=Attr('created_at').gte(cutoff),
                Select='COUNT'
            )
            return response.get('Count', 0)
        except ClientError as e:
            print(f"Error counting recent triggers: {e.response['Error']['Message']}")
            return 0

