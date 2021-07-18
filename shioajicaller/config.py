import os
from dotenv import load_dotenv

load_dotenv()
userId = os.environ.get('USER_ID')
userPassowrd = os.environ.get('USER_PASSWORD')
mqttHost = os.environ.get('MQTT_HOST')
mqttUser = os.environ.get('MQTT_USER')
mqttPassowrd = os.environ.get('MQTT_PASSWORD')