import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SES_REGION = 'us-east-1'
SENDER_EMAIL = 'aaggarwal@siterx.com'

def lambda_handler(event, context):
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id')
    state = detail.get('state')
    user_identity_arn = detail.get('userIdentity', {}).get('arn')
    user_email = detail.get('userIdentity', {}).get('userName') + '@siterx.com'  # Adjust as needed
    account_id = event.get('account')
    environment = 'ITOPS Sandbox'  # Adjust as needed
    event_name = detail.get('eventName')

    logger.info("Instance ID: %s, State: %s, User ARN: %s, User Email: %s, Account ID: %s, Environment: %s, Event Name: %s",
            instance_id, state, user_identity_arn, user_email, account_id, environment, event_name)

    if state in ["stopped", "terminated", "running", "rebooting"] or event_name == "RebootInstances":
        # Send an email notification
        send_email(instance_id, state, user_email, environment)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def send_email(instance_id, state, user_email, environment):
    client = boto3.client('ses', region_name=SES_REGION)
    
    body_text = f"The EC2 instance with ID {instance_id} has been {state} by {user_email}."
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>EC2 Instance State Change for {environment} account</h1>
      <p>The EC2 instance with ID <b>{instance_id}</b> has been <b>{state}</b> by user <b>{user_email}</b>.</p>
    </body>
    </html>"""
    
    response = client.send_email(
        Source=SENDER_EMAIL,
        Destination={
            'ToAddresses': [
                user_email,
            ]
        },
        Message={
            'Subject': {
                'Data': f"EC2 Instance State Change Notification for {environment}",
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
    return response