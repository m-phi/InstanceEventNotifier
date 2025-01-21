import json
import boto3

# SES configuration
SES_REGION = 'us-east-1'  # Change to your SES region
SENDER_EMAIL = 'aaggarwal@siterx.com'
RECIPIENT_EMAIL = 'aaggarwal@siterx.com'
SUBJECT = 'EC2 Instance Stopped'

def lambda_handler(event, context):
    # Extract instance details from the event
    detail = event['detail']
    instance_id = detail['instance-id']
    state = detail['state']

    # Extract user identity ARN and email
    user_principalId = event.get('userIdentity', {}).get('principalId', 'Unknown user')
    # user_identity_arn = event.get('userIdentity', {}).get('arn', 'Unknown user')
    user_email = user_principalId.split(':')[1] if user_principalId != 'Unknown user' else 'Unknown user'
        
    if state == 'stopped':
        # Send an email notification
        send_email(instance_id, user_email)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def send_email(instance_id, user_email):
    client = boto3.client('ses', region_name=SES_REGION)
    
    body_text = f"The EC2 instance with ID {instance_id} has been stopped by {user_email}."
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>EC2 Instance Stopped</h1>
      <p>The EC2 instance with ID <b>{instance_id}</b> has been stopped by {user_email}.</p>
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