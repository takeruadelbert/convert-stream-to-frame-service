import os

import pymysql.cursors

from misc.constant.value import STATUS_PROCESSING

db_host = os.getenv("DB_HOST")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


class Database:
    def __init__(self, logger):
        self.logger = logger
        self.db_connection = pymysql.connect(host=db_host, user=db_username, password=db_password, db=db_name,
                                             autocommit=True)
        self.db_cursor = self.db_connection.cursor()

    def fetch_data_stream(self):
        self.db_cursor.execute("SELECT url, gate_id FROM state")
        return self.db_cursor.fetchall()

    def check_if_gate_id_exists(self, gate_id):
        self.db_cursor.execute("SELECT gate_id FROM state WHERE gate_id = %s", (gate_id,))
        return self.db_cursor.fetchone()

    def add_default_image_result_data(self, ticket):
        try:
            self.db_cursor.execute("INSERT INTO image_result (ticket_number, status) VALUES (%s, %s)",
                                   (ticket, STATUS_PROCESSING))
            self.db_connection.commit()
            self.logger.info("Success added default data image result with ticket number : {}".format(ticket))
            return True
        except Exception as error:
            self.logger.error("Error has occurred when adding default data image result : {}".format(error))
            return False
