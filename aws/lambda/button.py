import json
import time
import os
import logging

import boto3

print('loading function')

iot = boto3.client('iot-data')
dynamo = boto3.client('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
The following JSON template shows what is sent as the payload:
{
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE" | "DOUBLE" | "LONG"
}
"""

def lambda_handler(event, context):
    logger.info("Sending waiterbot back to the kitchen.")

    # iot.publish(
    #     topic='req/waiterbot/v1/deliver/+',
    #     qos=1,
    #     payload=json.dumps({
    #         'current_order': "0"
    #     })
    # )
    try:
        payload = json.loads(iot.get_thing_shadow(thingName=os.environ['Thing_Name'])['payload'].read())
        logger.info("Current %s shadow: %s", os.environ['Thing_Name'], (str(payload)))
        order_id = payload['state']['reported']['current_order']
        delivery_time = str(time.time())
        if order_id is not 0:
            dynamo.update_item(
                TableName=os.environ['Dynamo_Fulfilled_Table'],
                Key={'order_id':{'S':order_id}},
                UpdateExpression="SET delivery_time = :t",
                ExpressionAttributeValues={":t":{"S": delivery_time}},
            )
    except KeyError as e:
        logger.error("Problem parsing thing shadow at key %s", e)

    iot.update_thing_shadow(
        thingName=os.environ['Thing_Name'],
        payload=json.dumps({
            'state':{
                'desired':{
                    'current_order': "0",
                    'destination': 0,
                }
            }
        })
    )
