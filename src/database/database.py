import os

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.misc.constant.value import STATUS_RUNNING, STATUS_PROCESSING
from src.misc.helper.helper import get_current_datetime

db_host = os.getenv("DB_HOST")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_username, db_password, db_host, db_name))
Base = declarative_base()


class InputImage(Base):
    __tablename__ = "input_image"
    id = Column(Integer, primary_key=True)
    status = Column(String)
    token = Column(String)
    ticket_number = Column(String)
    created_date = Column(DateTime)


class DataState(Base):
    __tablename__ = "data_state"
    id = Column(Integer, primary_key=True)
    id_gate = Column(String)
    last_state = Column(String)
    status = Column(String)
    url = Column(String)
    created_date = Column(DateTime)


class Database:
    def __init__(self, logger):
        self.logger = logger
        session = sessionmaker(bind=engine)
        self.session = session()

    def fetch_data_stream(self):
        data_states = self.session.query(DataState).filter(DataState.status == STATUS_RUNNING).all()
        self.session.commit()
        return data_states

    def add_default_image_result_data(self, ticket, token):
        try:
            input_image = InputImage(ticket_number=ticket, token=token, status=STATUS_PROCESSING,
                                     created_date=get_current_datetime())
            self.session.add(input_image)
            self.session.commit()
            return True
        except Exception as error:
            self.logger.error("Error has occurred when adding default data image result : {}".format(error))
            return False
