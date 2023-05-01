import swagger_ui_bundle
import connexion
import requests
import time
import os
import datetime
import logging
from logging import config
import requests
import yaml
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

def health():
    """ Periodically update Health   """
    curr_time = datetime.datetime.now()
    curr_time_str = curr_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    health = {}

    receiver_health = app_config["receiver_health"]
    storage_health = app_config["storage_health"]
    processor_health = app_config["processor_health"]
    audit_health = app_config["audit_health"]
    timeout = app_config["timeout"]
    
    service_health_list = [receiver_health, storage_health, processor_health, audit_health]

    for health_check in service_health_list:
        try:
            requests.get(health_check["url"], timeout=timeout)
            health[health_check["service"]] = "Running"
        except Exception as e:
            health[health_check["service"]] = "Down"

    health["last_updated"] = curr_time_str

    logger.info(f"Health Check: {health}")

    with open("health_check.json", "w+") as f:
        json.dump(health, f, indent=4)

    return health, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(health, 
                    'interval', 
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()
    
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

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)