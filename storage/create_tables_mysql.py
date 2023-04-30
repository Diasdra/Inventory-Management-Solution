import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(host=app_config["datastore"]["host"],
                                  user=app_config["datastore"]["user"],
                                  password=app_config["datastore"]["hostname"],
                                  database=app_config["datastore"]["db"])

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE rented_car
          (id INT NOT NULL AUTO_INCREMENT, 
           trace_id VARCHAR(200) NOT NULL,
           car_id INTEGER(250) NOT NULL, 
           car_type VARCHAR(250) NOT NULL, 
           location VARCHAR(250) NOT NULL,
           mileage Integer(200) NOT NULL,
           passenger_limit Integer(200) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT rent_car_pk PRIMARY KEY(id))
          ''')


db_cursor.execute('''
          CREATE TABLE returned_car
          (id INT NOT NULL AUTO_INCREMENT,
           trace_id VARCHAR(200) NOT NULL, 
           car_id INTEGER(250) NOT NULL, 
           kilometers Integer(200) NOT NULL,
           gas_used Integer(200) NOT NULL,
           cost Integer(200) NOT NULL,
           rent_duration Integer(200) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT return_car_pk PRIMARY KEY(id))
          ''')

db_conn.commit()
db_conn.close()
