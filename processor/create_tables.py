import sqlite3

conn = sqlite3.connect('stats.sqlite')

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