from app.utils.dynamodb import dynamodb, get_table_name
from app.schemas.models import NewsItemSchema
from botocore.exceptions import ClientError

class NewsItem:
    table = dynamodb.Table(get_table_name('news_items'))

    @classmethod
    def get_by_id(cls, news_id):
        """
        Retrieves a news item by its news_id.
        """
        try:
            response = cls.table.get_item(Key={'news_id': news_id})
            if 'Item' in response:
                return NewsItemSchema(**response['Item'])
            return None
        except ClientError as e:
            print(f"Error fetching news item: {e.response['Error']['Message']}")
            return None

    @classmethod
    def create(cls, news_data: NewsItemSchema):
        """
        Creates a new news item in DynamoDB.
        Uses a conditional write to avoid duplicates during concurrent ingestion.
        """
        try:
            # Convert to JSON-compatible dict (converts datetime to ISO string)
            item_dict = news_data.model_dump(mode='json')
            cls.table.put_item(
                Item=item_dict,
                ConditionExpression="attribute_not_exists(news_id)"
            )
            return True
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == "ConditionalCheckFailedException":
                # Item already exists, safe to ignore
                return False
            print(f"Error creating news item: {e.response['Error']['Message']}")
            return False

    @classmethod
    def list_all(cls, limit=20):
        """
        Lists news items (scan operation, use with caution on large tables).
        """
        try:
            response = cls.table.scan(Limit=limit)
            return [NewsItemSchema(**item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error scanning news items: {e.response['Error']['Message']}")
            return []
