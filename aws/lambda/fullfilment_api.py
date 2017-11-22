import json
import time
import logging
import os

import boto3

print('Loading function')

dynamo = boto3.client('dynamodb')
iot_data = boto3.client('iot-data')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    }

def get_orders():
    return dynamo.scan(TableName=os.environ['Dynamo_Order_Table'])['Items']

def fulfill_order(order_id):
    # Delete order from in_flight table and add it to fulfilled table
    logger.info("Order ID to fulfill: %s", order_id)
    response = dynamo.delete_item(
        TableName=os.environ['Dynamo_Order_Table'],
        Key={'order_id':{'S':order_id}},
        ReturnValues='ALL_OLD',
    )

    try:
        order = response['Attributes']
        order_id = order['order_id']['S']
        table = order['table']['N']
    except KeyError as e:
        logger.error("No %s in delete_item response. Order ID probs didn't exist", e)
        raise

    fulfilled_time = str(time.time())
    order.update({"fulfilled_time":{'S': fulfilled_time}})

    dynamo.put_item(
        TableName=os.environ['Dynamo_Fulfilled_Table'],
        Item=order,
    )

    # Send a message to IoT to tell Waiterbot to deliver order
    logger.info("Sending Waiterbot to table %s", table)
    # payload = json.dumps({
    #     'destination': table,
    #     'current_order': order_id,
    # })
    # iot_data.publish(
    #     topic='req/waiterbot/v1/deliver/+',
    #     qos=1,
    #     payload=payload
    # )
    iot_data.update_thing_shadow(
        thingName=os.environ['Thing_Name'],
        payload=json.dumps({
            'state':{
                'desired':{
                    'current_order': order_id,
                    'destination': int(table),
                }
            }
        })
    )

def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    logger.info("Using table: %s", os.environ['Dynamo_Order_Table'])

    operation = event['httpMethod']
    logger.info("Operation: %s", operation)
    if operation == 'GET':
        return respond(None, get_orders())
    elif operation == 'POST':
        try:
            fulfill_order(json.loads(event['body'])['order_id'])
            return respond(None, "Successfully fulfilled order")
        except KeyError as e:
            logger.error("Missing Key: %s", e)
            return respond("Problem fulfilling order")
    else:
        logger.error("Unsupported method %s", operation)
        return respond("Unsupported method '{}'".format(operation))
