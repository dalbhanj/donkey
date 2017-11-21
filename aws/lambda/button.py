import json
import logging

import boto3

print('loading function')

iot = boto3.client('iot-data')
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

    iot.publish(
        topic='req/waiterbot/v1/deliver/bot1',
        qos=1,
        payload=json.dumps({
            'destination': 0,
            'current_order': "0"
        })
    )
