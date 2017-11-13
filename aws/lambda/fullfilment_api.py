
import json
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
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }

def get_orders():
    return dynamo.scan(TableName=os.environ['Dynamo_Order_Table'])['Items']

def fullfil_order(order_id):
    logger.info("Order ID: %s", order_id)
    response = dynamo.delete_item(
        TableName=os.environ['Dynamo_Order_Table'],
        Key={'order_id':{'S':order_id}}
    )

    # TODO: Send table info to rover to fulfill order. Get table dest
    # from delete_item response

def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    logger.info("Using table: %s", os.environ['Dynamo_Order_Table'])

    operations = {
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x)
    }

    operation = event['httpMethod']
    if operation in operations:
        logger.info("Operation: %s", operation)
        if operation == 'GET':
            return respond(None, get_orders())
        elif operation == 'POST':
            fullfil_order(json.loads(event['body'])['order_id'])
            return respond(None, "Successfully fulfilled order")
    else:
        logger.error('Unsupported method "{}"'.format(operation))
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
