import os
from dotenv import load_dotenv

load_dotenv()
userId = os.environ.get('USER_ID')
userPassowrd = os.environ.get('USER_PASSWORD')
redisHost = os.environ.get('REDIS_HOST')
redisPort = os.environ.get('REDIS_PORT')
redisDb = os.environ.get('REDIS_DB')
websocketsPort = os.environ.get('WEBSOCKETS_PORT')
mqttUser = os.environ.get('MQTT_USER')
mqttPassword = os.environ.get('MQTT_PASSWORD')
mqttHost = os.environ.get('MQTT_HOST')