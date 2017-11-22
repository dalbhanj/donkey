'''
Class used to connect Waiterbot to AWS IoT.
'''

import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class IotClient:

    def __init__(self, cfg, vehicle, delta_callback=None):
        self.vehicle = vehicle
        self.cfg = cfg
        self._shadow_client = AWSIoTMQTTShadowClient(cfg.CLIENT_NAME)
        self._shadow_client.configureEndpoint(cfg.IOT_ENDPOINT, 8883)
        self._shadow_client.configureCredentials(cfg.ROOT_CERT, cfg.PRIVATE_KEY, cfg.CERT_PATH)
        self._shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
        self._shadow_client.configureMQTTOperationTimeout(5)  # 5 sec

        if not self._shadow_client.connect():
            print("Cannot connect to IoT. This is bad.")
        self.shadow_handler = self._shadow_client.createShadowHandlerWithName(cfg.THING_NAME, True)

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
        if delta_callback:
            self.shadow_handler.shadowRegisterDeltaCallback(delta_callback)
        else:
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
        model_num = self.get_model_num(payload_dict)
        print("+++++++++++++++++++++++\n\n")
        self.move_vehicle(model_num)
        self.shadow_handler.shadowUpdate(json.dumps(self.shadow), self._update_callback, 5)

    def get_model_num(self, payload_dict):
        '''
        **Description**
        Get the model number for the delivery (or for return to kitchen)

        This function also updates reported local shadow to match desired
        location and current_order.
        '''
        # The contents of the delta payload will tell us what action to take
        desired_state = payload_dict['state']
        model_num = 0
        if 'destination' in desired_state and 'current_order' in desired_state:
            if desired_state['destination'] is not 0: # moving to a table
                # Get the model to get to the table
                model_num = desired_state['destination']
                # Update shadow with new values
                self.shadow['state']['reported']['location'] = -1 # -1 for moving
                self.shadow['state']['reported']['destination'] = desired_state['destination']
                self.shadow['state']['reported']['current_order'] = desired_state['current_order']
                print("Model # to use: " + str(model_num))
                print("Current shadow: " + str(self.shadow))
            elif desired_state['destination'] is 0: # going back to kitchen
                # The same model we used to get to the table we use to get back to the kitchen
                model_num = self.shadow['state']['reported']['destination']
                # Update shadow with new values
                self.shadow['state']['reported']['location'] = -1 # -1 for moving
                self.shadow['state']['reported']['destination'] = desired_state['destination']
                self.shadow['state']['reported']['current_order'] = desired_state['current_order']
                print("Model # to use: " + str(model_num))
                print("Current shadow: " + str(self.shadow))
        return model_num

    def move_vehicle(self, model_num):
        '''
        **Description**
        Uses the specified model number to create a new Keras part for vehicle
        then calls vehicle.run to move the rover to the desired destination.
        '''
        # Get the current Keras part from vehicle to load new model
        # THIS ASSUMES THE PART IS ALWAYS NAMED kl
        print("Using model at " + self.cfg.MODEL_MAP[model_num])
        self.vehicle.get("kl").load(self.cfg.MODEL_MAP[model_num])

        try:
            self.vehicle.run(rate_hz=self.cfg.DRIVE_LOOP_HZ,
                             max_loop_count=self.cfg.MAX_LOOPS)
        except KeyboardInterrupt:
            print('pausing')
            self.vehicle.pause()
            self.update_shadow_after_stop()

    def update_shadow_after_stop(self):
        '''
        Call when the rover stops moving. Update the shadow to reflect that the rover has reached
        it's destination.
        '''
        print("Rover (should be) stopped. Updating shadow...")
        self.shadow['state']['reported']['location'] = self.shadow['state']['reported']['destination']
        self.shadow_handler.shadowUpdate(json.dumps(self.shadow), self._update_callback, 5)
