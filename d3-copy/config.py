""" 
CAR CONFIG 

This file is read by your car application's manage.py script to change the car
performance. 

EXMAPLE
-----------
import dk
cfg = dk.load_config(config_path='~/d2/config.py')
print(cfg.CAMERA_RESOLUTION)

"""


import os

#PATHS
CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')
MODELS_PATH = os.path.join(CAR_PATH, 'models')

#VEHICLE
DRIVE_LOOP_HZ = 20
MAX_LOOPS = 100000

#CAMERA
CAMERA_RESOLUTION = (120, 160) #(height, width)
CAMERA_FRAMERATE = DRIVE_LOOP_HZ

#STEERING
STEERING_CHANNEL = 1
STEERING_LEFT_PWM = 460
STEERING_RIGHT_PWM = 260

#THROTTLE
THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 500
THROTTLE_STOPPED_PWM = 370
THROTTLE_REVERSE_PWM = 220

# Setting options for autodrive in manage.py 
CONSTANT_THROTTLE = .20
MODE_CONFIG = 'local_angle'

# Setting options for 3-point turn
LEFT_ANGLE_X = 0.0
THROTTLE_TIME_X = 100
RIGHT_ANGLE_Y = 0.0
THROTTLE_TIME_Y = 100
LEFT_ANGLE_Z = 0.0
THROTTLE_TIME_Z = 100

#TRAINING
BATCH_SIZE = 128
TRAIN_TEST_SPLIT = 0.8

#JOYSTICK
USE_JOYSTICK_AS_DEFAULT = False
JOYSTICK_MAX_THROTTLE = 0.25
JOYSTICK_STEERING_SCALE = 1.0
AUTO_RECORD_ON_THROTTLE = True

# IoT
IOT_ENDPOINT = "ad16cm18p9apb.iot.us-east-1.amazonaws.com"
ROOT_CERT_PATH = "./iotCerts/rootCA.pem"
CERT_PATH = "./iotCerts/cert.pem"
PRIVATE_KEY_PATH = "./iotCerts/private.key"
CLIENT_NAME = "bot1"
THING_NAME = "waiterbot-bot1"
REQ_DELIVERY_TOPIC = "req/waiterbot/v1/deliver/" + CLIENT_NAME
RES_DELIVERY_TOPIC = "res/waiterbot/v1/deliver/" + CLIENT_NAME
SHUTDOWN_TOPIC = "req/waiterbot/v1/shutdown/" + CLIENT_NAME
MODEL_MAP = {
    1: "os.path.join(MODELS_PATH)/matt-desk-10-02-1430",
    2: "os.path.join(MODELS_PATH)/wangechi-desk-10-02",
    3: "os.path.join(MODELS_PATH)/peter_desk-10-05",
    4: "PATH_TO_TABLE_4_MODEL",
}
