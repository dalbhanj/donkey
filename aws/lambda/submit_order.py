import json
import time
import logging
import os

import boto3

print('Loading function')

dynamo = boto3.client('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else res,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def lambda_handler(event, context):
    '''
    Sends customer order to dynamo table for tracking and fulfillment.

    Event contains the following keys:

      - table: the table making the order
      - menu_item: the ordered item
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    logger.info("Using table: %s", os.environ['Dynamo_Order_Table'])
    logger.info("Menu items: %s", os.environ['Menu_Items'])

    try:
        valid_items = os.environ['Menu_Items']
        body = json.loads(event['body'])
        order_time = str(time.time())
        table = body['table']
        menu_item = body['menu_item']

        if int(table) < 1 or int(table) > 4 or menu_item not in valid_items:
            logger.error("Invalid order %s", json.dumps(event, indent=2))
            return respond("Invalid order.")

        payload = {
            'order_id': {'S':order_time},
            'table': {'N':table},
            'menu_item': {'S':menu_item}
        }
        logger.info("Order info: %s", json.dumps(payload, indent=2))
        dynamo.put_item(
            TableName=os.environ['Dynamo_Order_Table'],
            Item=payload
        )
        return respond(None, "Order successfully submitted")
    except KeyError as exc:
        logger.error(exc)
        return respond("Missing key " + str(exc))
    except TypeError as exc:
        logger.error(exc)
        return respond("Type error " + str(exc))
    except Exception as exc:
        logger.error(exc)
        return respond("Unknown error " + str(exc))
