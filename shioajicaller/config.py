import os
from dotenv import load_dotenv, find_dotenv

try:
    load_dotenv(find_dotenv( raise_error_if_not_found = True))
except Exception:
    try:
        load_dotenv(find_dotenv( usecwd= True,raise_error_if_not_found = True))
    except Exception:
        pass

apiKey = os.environ.get('API_KEY')
secretKey = os.environ.get('SECRET_KEY')
redisHost = os.environ.get('REDIS_HOST')
redisPort = os.environ.get('REDIS_PORT')
redisDb = os.environ.get('REDIS_DB')
websocketsPort = os.environ.get('WEBSOCKETS_PORT')
mqttUser = os.environ.get('MQTT_USER')
mqttPassword = os.environ.get('MQTT_PASSWORD')
mqttHost = os.environ.get('MQTT_HOST')