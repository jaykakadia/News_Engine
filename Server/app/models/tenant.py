from app.utils.dynamodb import dynamodb, get_table_name
from app.schemas.models import TenantSchema
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

class Tenant:
    table = dynamodb.Table(get_table_name('tenants'))

    @classmethod
    def get_by_id(cls, tenant_id):
        """
        Retrieves a tenant by their tenant_id.
        """
        try:
            response = cls.table.get_item(Key={'tenant_id': tenant_id})
            if 'Item' in response:
                return TenantSchema(**response['Item'])
            return None
        except ClientError as e:
            print(f"Error fetching tenant: {e.response['Error']['Message']}")
            return None

    @classmethod
    def get_by_email(cls, email):
        """
        Retrieves a tenant by their email using a table scan.
        """
        try:
            response = cls.table.scan(
                FilterExpression=Attr('email').eq(email)
            )
            items = response.get('Items', [])
            if items:
                return TenantSchema(**items[0])
            return None
        except ClientError as e:
            print(f"Error fetching tenant by email: {e.response['Error']['Message']}")
            return None

    @classmethod
    def create(cls, tenant_data: TenantSchema):
        """
        Creates a new tenant (agency) in DynamoDB.
        """
        try:
            item_dict = tenant_data.model_dump(mode='json')
            cls.table.put_item(
                Item=item_dict,
                ConditionExpression="attribute_not_exists(tenant_id)"
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print("Tenant already exists.")
                return False
            print(f"Error creating tenant: {e.response['Error']['Message']}")
            return False

    @classmethod
    def list_all(cls, limit=50):
        """
        Lists all tenants.
        """
        try:
            response = cls.table.scan(Limit=limit)
            return [TenantSchema(**item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error listing tenants: {e.response['Error']['Message']}")
            return []
