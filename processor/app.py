import swagger_ui_bundle
import connexion
import requests
import os
import datetime
import logging
import uuid
from logging import config
import requests
import yaml
import sqlite3
import json

from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
from base import Base
from stats import Stats
from flask_cors import CORS, cross_origin

def create_database():
    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()
    c.execute('''
            CREATE TABLE stats
            (id INTEGER PRIMARY KEY ASC,
            trace_id VARCHAR(200) NOT NULL,
            num_car_returns INTEGER NOT NULL,
            num_car_rentals INTEGER NOT NULL,
            max_gas_used INTEGER,
            max_passenger_limit INTEGER,
            last_updated VARCHAR(100) NOT NULL)
            ''')
    conn.commit()
    conn.close()

    logger.info("Database created.")

def get_health():
    return 200

def get_stats():
    """ Receives a stats req """
    
    logger.info(f"Start get_stats request for latest stats")

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()

    if not results:
        logger.error(f'Statistics do not exist')
        return 404
    
    data = results.to_dict()
    
    logger.debug(data.items)
    logger.info("request has been completed")
    session.close()
    
    return data, 200

def populate_stats():
    """ Periodically update stats   """
    
    trace_id = str(uuid.uuid4())
    logger.info(f"Start Periodic Processing with trace id of {trace_id}")
    now = datetime.datetime.now()

    session = DB_SESSION()

    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()

    #check if previous stats exists
    if not results:
        results = Stats(0,
                0,
                0,
                0,
                datetime.datetime.fromtimestamp(0),
                str(uuid.uuid4()))

    prev_stats = results.to_dict()
    prev_time = prev_stats["last_updated"]
    current_timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    
    get_car_rentals = requests.get(app_config["get_car_rentals"]["url"], params={"start_timestamp": prev_time, "end_timestamp": current_timestamp}, headers={'Content-Type': 'application/json'})
    get_car_returns = requests.get(app_config["get_car_returns"]["url"], params={"start_timestamp": prev_time, "end_timestamp": current_timestamp}, headers={'Content-Type': 'application/json'})
    
    
    if(get_car_returns.status_code == 200):
        logger.info(f"{len(get_car_returns.json())} events received from car returns")
    else:
        logger.error(f"get_car_returns returned status code {get_car_returns.status_code}")

    if(get_car_rentals.status_code == 200):
        logger.info(f"{len(get_car_rentals.json())} events received from car rentals")
    else:
        logger.error(f"get_car_rentals returned status code {get_car_rentals.status_code}")

    # Processing Events
    if len(get_car_returns.json()) != 0 :
        new_car_returns = int(len(get_car_returns.json()))
        new_gas_used = max(get_car_returns.json(), key=lambda x:x['gas_used'])['gas_used']
        for event in get_car_returns.json():
            logger.debug(f'Event trace ID: { event["trace_id"] }')
    else: 
        new_car_returns = 0
        new_gas_used = 0

    if len(get_car_rentals.json()) != 0 :
        new_car_rentals = int(len(get_car_rentals.json()))
        new_passenger_limit = max(get_car_rentals.json(), key=lambda x:x['passenger_limit'])['passenger_limit']
        for event in get_car_rentals.json():
            logger.debug(f'Event trace ID: { event["trace_id"] }')
    else: 
        new_car_rentals = 0
        new_passenger_limit = 0


    """ Comparing with old stats """
    num_car_returns = results.num_car_returns + new_car_returns
    num_car_rentals = results.num_car_rentals + new_car_rentals

    if new_gas_used > results.max_gas_used:
        max_gas_used = new_gas_used
    else:
        max_gas_used = results.max_gas_used

    if new_passenger_limit > results.max_passenger_limit:
        max_passenger_limit = new_passenger_limit
    else:
        max_passenger_limit = results.max_passenger_limit

    stats = Stats(num_car_returns,
                max_gas_used,
                num_car_rentals,
                max_passenger_limit,
                now,
                trace_id)

    session.add(stats)

    session.commit()

    msg = f"""  
    Updated stats: 
    Num car returns: {stats.num_car_returns}
    Max gas used rooms: {stats.max_gas_used}
    Num car rentals: {stats.num_car_rentals}
    Max passenger limit: {stats.max_passenger_limit}
    Last updated: {now}
    Trace ID: {trace_id}
    """

    session.close()

    logger.debug(msg)
    logger.info("Periodic Processing completed")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 
                    'interval', 
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()

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

    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

DATABASE = app_config['datastore']['filename']
DB_ENGINE = create_engine(f"sqlite:///{DATABASE}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger = logging.getLogger('basicLogger')

if not os.path.isfile(DATABASE):
    create_database()

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")


if __name__ == "__main__":
    #run our standable gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)
