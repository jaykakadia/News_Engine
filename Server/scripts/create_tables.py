import sys
import os
from app.utils.dynamodb import dynamodb, get_table_name

# Add Server directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_tables():
    tables = [
        {
            'TableName': get_table_name('tenants'),
            'KeySchema': [{'AttributeName': 'tenant_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'tenant_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': get_table_name('users'),
            'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'tenant_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'TenantIndex',
                    'KeySchema': [{'AttributeName': 'tenant_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': get_table_name('interests'),
            'KeySchema': [{'AttributeName': 'interest_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'interest_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'UserIndex',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': get_table_name('news_items'),
            'KeySchema': [{'AttributeName': 'news_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'news_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': get_table_name('triggers'),
            'KeySchema': [{'AttributeName': 'trigger_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'trigger_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'UserIndex',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': get_table_name('chat_history'),
            'KeySchema': [{'AttributeName': 'chat_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'chat_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'UserIndex',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
    ]

    for table_def in tables:
        try:
            print(f"Creating table {table_def['TableName']}...")
            dynamodb.create_table(**table_def)
            print(f"Table {table_def['TableName']} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_def['TableName']}: {e}")

if __name__ == "__main__":
    create_tables()
