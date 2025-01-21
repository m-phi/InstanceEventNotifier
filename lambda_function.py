import json
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SES configuration
SES_REGION = 'us-east-1'  # Change to your SES region
SENDER_EMAIL = 'aaggarwal@siterx.com'
RECIPIENT_EMAIL = 'aaggarwal@siterx.com'
SUBJECT = 'EC2 Instance State Change'

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    # Extract instance details from the event
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id', 'Unknown instance')
    state = detail.get('state', 'Unknown state')

    # Extract user identity ARN and email
    # user_principalId = event.get('userIdentity', {}).get('principalId', 'Unknown user')
    user_identity_arn = event.get('userIdentity', {}).get('arn', 'Unknown user')
    user_email = user_identity_arn.split('/')[-1] if user_identity_arn != 'Unknown user' else 'Unknown user'

    logger.info("Instance ID: %s, State: %s, User ARN: %s, User Email: %s", instance_id, state, user_identity_arn, user_email)

        
    if state in ['terminated', 'stopped']:
        # Send an email notification
        send_email(instance_id, state, user_email)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def send_email(instance_id, state, user_email):
    client = boto3.client('ses', region_name=SES_REGION)
    
    body_text = f"The EC2 instance with ID {instance_id} has been {state} by {user_email}."
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>EC2 Instance State Change</h1>
      <p>The EC2 instance with ID <b>{instance_id}</b> has been <b>{state}</b> by user <b>{user_email}</b>.</p>
    </body>
    </html>"""
    
    response = client.send_email(
        Source=SENDER_EMAIL,
        Destination={
            'ToAddresses': [
                RECIPIENT_EMAIL,
            ],
        },
        Message={
            'Subject': {
                'Data': SUBJECT,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Failed to send email: {response}")

# Ensure you have the necessary IAM roles and permissions for the Lambda function to access SES and CloudWatch.