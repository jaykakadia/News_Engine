from app.utils.dynamodb import dynamodb, get_table_name
from app.schemas.models import ChatHistorySchema
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

class ChatHistory:
    table = dynamodb.Table(get_table_name('chat_history'))

    @classmethod
    def save(cls, chat_data: ChatHistorySchema):
        """
        Saves a chat Q&A pair to DynamoDB.
        """
        try:
            item_dict = chat_data.model_dump(mode='json')
            cls.table.put_item(Item=item_dict)
            return True
        except ClientError as e:
            print(f"Error saving chat history: {e.response['Error']['Message']}")
            return False

    @classmethod
    def get_by_user(cls, user_id, limit=50):
        """
        Retrieves chat history for a user, sorted by newest first.
        """
        try:
            response = cls.table.scan(
                FilterExpression=Attr('user_id').eq(user_id),
                Limit=limit
            )
            items = response.get('Items', [])
            chats = [ChatHistorySchema(**item) for item in items]
            chats.sort(key=lambda c: c.created_at)
            return chats
        except ClientError as e:
            print(f"Error fetching chat history: {e.response['Error']['Message']}")
            return []
