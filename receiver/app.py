import connexion
import swagger_ui_bundle
import os
import yaml
import logging
from logging import config
import uuid
import datetime
import time
import json

from connexion import NoContent
from pykafka import KafkaClient
        
def return_car(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace

    logger.info('Received return car event with trace id' + trace)

    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "return_car", 
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 
            "payload": body }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
            
    logger.info('Returned return car event response(Id: ' + trace )

    return body, 201

def rent_car(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace

    logger.info('Received rentcar even with trace id' + trace)

    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "rent_car", 
            "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 
            "payload": body }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Returned rent car event response(Id: ' + trace )

    return body, 201


def get_health():

    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")

# connect at start instead of each function
max_retry = app_config["kafka"]["max_retries"]
kafka_sleep_time = app_config["kafka"]["sleep_time"]
hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
retry = 0
while retry < max_retry:
    retry += 1
    logger.info(f'Attempting to connect to kafak - Attempt #{retry}')
    try:
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config['events']['topic'])]
        logger.info(f'Connection Attempt #{retry} successful')
        break
    except Exception as e:
        logger.error(f'Kafka connection failed. Attempt #{retry}')
        time.sleep(kafka_sleep_time)


if __name__ == "__main__":
    app.run(port=8080, use_reloader=False)
