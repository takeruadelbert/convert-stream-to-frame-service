import os

import pymysql.cursors

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
