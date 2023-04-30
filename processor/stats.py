from sqlalchemy import Column, Integer, String, DateTime
from base import Base

class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    num_car_returns = Column(Integer, nullable=False)
    max_gas_used = Column(Integer, nullable=False)
    num_car_rentals = Column(Integer, nullable=True)
    max_passenger_limit = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_car_returns, max_gas_used, num_car_rentals, max_passenger_limit,
        last_updated,trace_id):

        """ Initializes a processing statistics object """
        self.trace_id = trace_id
        self.num_car_returns = num_car_returns
        self.max_gas_used = max_gas_used
        self.num_car_rentals = num_car_rentals
        self.max_passenger_limit = max_passenger_limit
        self.last_updated = last_updated

    def to_dict(self):

        """ Dictionary Representation of a statistics """

        dict = {}
        dict['trace_id'] = self.trace_id
        dict['num_car_returns'] = self.num_car_returns
        dict['max_gas_used'] = self.max_gas_used
        dict['num_car_rentals'] = self.num_car_rentals
        dict['max_passenger_limit'] = self.max_passenger_limit
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
        return dict