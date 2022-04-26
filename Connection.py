from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class Connection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver conn when you're done with it
        self.driver.close()

    def test_conn(self):
        with self.driver.session() as session:
            try:
                session.run("Match () Return 1 Limit 1")
                print('connection ok')
            except Exception:
                print('connection error')