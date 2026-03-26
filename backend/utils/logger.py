import os
import boto3
import json
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

LOG_TABLE = os.getenv('DYNAMODB_LOG_TABLE')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

def log_event(event_type, status, user_id, details):
    try:
        table = dynamodb.Table(LOG_TABLE)
        log_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'log_id': log_id,
            'timestamp': timestamp,
            'event_type': event_type,
            'status': status,
            'user_id': user_id,
            'details': json.dumps(details)
        }
        
        table.put_item(Item=item)
        
        if status == 'error':
            notify_error(event_type, details)
            
        return log_id
    except Exception as e:
        print(f"Logging failed: {str(e)}")
        return None

def notify_error(event_type, details):
    try:
        message = f"Error in Lakehouse Analytics:\nType: {event_type}\nDetails: {json.dumps(details, indent=2)}"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"Lakehouse Alert: {event_type}"
        )
    except Exception as e:
        print(f"SNS notification failed: {str(e)}")
