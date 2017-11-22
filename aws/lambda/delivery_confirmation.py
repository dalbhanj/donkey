import json
import os
import logging

import boto3

print('Loading function')

dynamo = boto3.client('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    '''Event contains the following keys:

      - table: the table the rover made a delivery to
      - order_id: the order id for the delivery
      - delivery_time: the time the customer acknowledged delivery of the item
    '''
    print("Received event: " + json.dumps(event, indent=2))

    if 'table' in event and 'order_id' in event and 'delivery_time' in event:
        dynamo.update_item(
            TableName=os.environ['Dynamo_Fulfilled_Table'],
            Key={'order_id':{'S':event['order_id']}},
            UpdateExpression="SET delivery_time = :t",
            ExpressionAttributeValues={":t":{"S": event['delivery_time']}},
        )
    else:
        logger.error("Something went wrong. Received event: %s", json.dumps(event, indent=2))
