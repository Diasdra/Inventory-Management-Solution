
import json
import swagger_ui_bundle
import connexion
import os
import yaml
import logging
from logging import config

from pykafka import KafkaClient
from flask_cors import CORS, cross_origin


def get_health():
    return 200

def get_return_car_application(index):
    """ Get return car app in History """
    
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info(f"Retriving expense at index {index}")
    try:
        pos = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if  msg["type"] == "return_car":
                if index == pos:
                    logger.info(f'found return_car application at index {index}: {msg}')
                    return msg, 200
                else:
                    pos+=1
    except:
        logger.error("No more messages found")
        
    logger.error(f"could not find expense at index {index}")
    return { "message": "Not Found"}, 404

def get_rent_car_application(index):
    """ Get rent car app in History """
    
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info("Retrieving rent car at index %d" % index)
    try:
        pos = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if  msg["type"] == "rent_car":
                if index == pos:
                    logger.info(f'found rent_car application at index {index}: {msg}')
                    return msg, 200
                else:
                    pos+=1
    except:
        logger.error("No more messages found")
        return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")


if __name__ == "__main__":
    app.run(port=8110)
