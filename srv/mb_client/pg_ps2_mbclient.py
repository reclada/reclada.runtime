import psycopg2
import psycopg2.extensions
import time
import select
from multiprocessing import Process, Queue
from srv.mb_client.mbclient import MBClient
from srv.coordinator.resource import Resource

class PgPs2MBClient(MBClient, Process):

    def __init__(self):
        Process.__init__(self)
        self._queue = None
        self._host = None
        self._database = None
        self._user = None
        self._password = None
        self._channels = None

    def handle_request(self, body):
        """
            This method is called when a new message arrives
        :param body: message body
        """
        self._queue.put(body)

    def run(self):
        """
            This method gets called to start the loop of message handling
        """

        # open a DB connection
        self.open_db_connection()
        try_number = 1

        while try_number < 5:
            try:
                if select.select([self._pgc], [], [], 600) == ([],[],[]):
                    self.handle_request(0)
                    continue
                else:
                    self._pgc.poll()
                    while self._pgc.notifies:
                        message = self._pgc.notifies.pop(0)
                        if message.channel == self._channels:
                            self.handle_request(message.payload)
            except Exception as ex:
                print(f'DB connection error.')
                self.open_db_connection()
                try_number += 1

        print(f"Can't establish connection to DB.")
        exit(1)


    def open_db_connection(self):
        """
            This method creates a DB connection
        """
        # create connection to DB
        try_number = 1
        while try_number < 5:
            try:
                self._pgc = psycopg2.connect( user=self._user,
                                              password=self._password,
                                              host=self._host,
                                              port=5432,
                                              database=self._database )
                self._pgc.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                self._cursor = self._pgc.cursor()
                self._cursor.execute(f'LISTEN {self._channels};')
                break
            except Exception as ex:
                try_number += 1
                time.sleep(10)
                continue

        ret_code = -1 if try_number >= 5 else 0
        return ret_code


    def set_credentials(self, type, json_file):
        """
              This method sets the credential to connect to PostgreSQL notify channel
              :param type: type of connection to message broker
              :param json_file: json file with credentials
        """
        res = Resource()
        res = res.get(type, json_file)
        self._host = res.host
        if self._host is None:
            return 1
        self._database = res.database
        if self._database is None:
            return 1
        self._user = res.user
        if self._user is None:
            return 1
        self._password = res.password
        if self._password is None:
            return 1
        self._channels = res.channel
        if self._channels is None:
            return 1


    def set_queue(self, queue):
        """
            This method saves the queue for message's exchange
        :param queue: message queue
        """
        self._queue = queue


if __name__ == "__main__":
    q_mbclient = Queue()
    p_mbclient = PgMBClient()
    p_mbclient.set_credentials("MB", "messaging.json")
    p_mbclient.set_queue(q_mbclient)
    print(" [x] Awaiting requests")

    p_mbclient.start()

    # Wait for a message in the queue
    while True:
        message = q_mbclient.get(block=True)
        print(f"From the Queue: {message}")
