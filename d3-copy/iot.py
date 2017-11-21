'''
Class used to connect Waiterbot to AWS IoT.
'''

import json
import time
from AWSIoTPythonSDK import MQTTLib
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class IotClient:

    def __init__(self, cfg, vehicle):
        self.vehicle = vehicle
        self._shadow_client = AWSIoTMQTTShadowClient(cfg.CLIENT_NAME)
        self._shadow_client.configureEndpoint(cfg.IOT_ENDPOINT, 8883)
        self._shadow_client.configureCredentials(cfg.ROOT_CERT, cfg.PRIVATE_KEY, cfg.CERT_PATH)
        self._shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
        self._shadow_client.configureMQTTOperationTimeout(5)  # 5 sec

        if not self._shadow_client.connect():
            print("Cannot connect to IoT. This is bad.")
        self.shadow_handler = self._shadow_client.createShadowHandlerWithName(cfg.THING_NAME, True)
        #self._mqtt_client = self._shadow_client.getMQTTConnection()

        # Delete any existing shadow and create a fresh one
        self.shadow_handler.shadowDelete(self._delete_callback, 5)
        self.shadow = {
            "state": {
                "reported": {
                    "location": 0,
                    "destination": 0,
                    "current_order": "0",
                }
            }
        }
        self.shadow_handler.shadowUpdate(json.dumps(self.shadow), self._update_callback, 5)
        # Create subscription to shadow delta topic to receive delivery requests
        self.shadow_handler.shadowRegisterDeltaCallback(self._delta_callback)

    def _update_callback(self, payload, response_status, token):
        '''
        Callback function invoked when the shadow handler updates the thing shadow.
        '''
        if response_status == "timeout":
            print("Update request " + token + " time out!")
        if response_status == "accepted":
            payload_dict = json.loads(payload)
            print("~~~~~~~~~~~~~~~~~~~~~~~")
            print("Update request with token: " + token + " accepted!")
            print("Current location: " + str(payload_dict["state"]["reported"]["location"]))
            print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        if response_status == "rejected":
            print("Update request " + token + " rejected!")

    def _delete_callback(self, payload, response_status, token):
        '''
        Callback function invoked when the shadow handler deletes the thing shadow.
        '''
        if response_status == "timeout":
            print("Delete request " + token + " time out!")
        if response_status == "accepted":
            print("~~~~~~~~~~~~~~~~~~~~~~~")
            print("Delete request with token: " + token + " accepted!")
            print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        if response_status == "rejected":
            print("Delete request " + token + " rejected!")

    def _delta_callback(self, payload, response_status, token):
        '''
        Callback function invoked when the shadow handler receives a new, desired state.
        '''
        print("++++++++DELTA++++++++++")
        print("Response status: " + response_status)
        print("Payload: " +payload)
        payload_dict = json.loads(payload)
        
        # Based on current and desired states, make appropriate action
        current_state = self.shadow['state']['reported']
        # The contents of the delta payload will tell us what action to take
        desired_state = payload_dict['state']
        if 'destination' in desired_state and 'current_order' in desired_state: 
            if desired_state['destination'] is not 0: # moving to a table
                # Get the model to get to the table
                model = desired_state['destination']
                # Update shadow with new values
                self.shadow['state']['reported']['location'] = -1 # -1 for moving
                self.shadow['state']['reported']['destination'] = desired_state['destination']
                self.shadow['state']['reported']['current_order'] = desired_state['current_order']
                print("Model # to use: " + model)
                print("Current shadow: " + str(self.shadow))
            elif desired_state['destination'] is 0: # going back to kitchen
                # The same model we used to get to the table we use to get back to the kitchen
                model = self.shadow['state']['reported']['destination']
                # Update shadow with new values
                self.shadow['state']['reported']['location'] = -1 # -1 for moving
                self.shadow['state']['reported']['destination'] = desired_state['destination']
                self.shadow['state']['reported']['current_order'] = desired_state['current_order']
                print("Model # to use: " + model)
                print("Current shadow: " + str(self.shadow))
        
        print("+++++++++++++++++++++++\n\n")
        self.shadow_handler.shadowUpdate(json.dumps(self.shadow), self._update_callback, 5)

    def update_shadow(self):
        '''
        Call when the rover stops moving. Update the shadow to reflect that the rover has reached
        it's destination.
        '''
        print("Rover stopped. Updating shadow...")
        self.shadow['state']['reported']['location'] = self.shadow['state']['reported']['destination']
        self.shadow_handler.shadowUpdate(json.dumps(self.shadow), self._update_callback, 5)
