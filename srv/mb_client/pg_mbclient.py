from postgresql.notifyman import NotificationManager
import postgresql
import signal
from multiprocessing import Process, Queue
from srv.mb_client.mbclient import MBClient
from srv.coordinator.resource import Resource

SIGNALS_TO_HANDLE = [signal.SIGINT, signal.SIGTERM]


class PgMBClient(MBClient, Process):

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

        # create the Notification Manager
        # to handle notifications from different channels
        # For now we have only one channel
        self._pgc.listen(self._channels)
        nm = NotificationManager(self._pgc)
        nm.settimeout(600)
        for message in nm:
            # if timeout happens then we don't need
            # to process the message
            if message is None:
                # check for bad connections
                if nm.garbage:
                    nm.garbage.clear()
                # handle the request
                self.handle_request(0)
                # open the new connection
                self._pgc.close()
                self.open_db_connection()
                nm.connections.update(self._pgc)
                self._pgc.listen(self._channels)
                continue
            # if a message arrived then
            # we need to check the name of
            # the channel and if it equals the name
            # of the channel specified in Resource then
            # we need to handle it properly
            db, notifies = message
            for channel, payload, pid in notifies:
                if channel == self._channels:
                    self.handle_request(payload)

    def open_db_connection(self):
        """
            This method creates a DB connection
        """
        # create connection to DB
        self._pgc = postgresql.open( user=self._user,
                                     password=self._password,
                                     host=self._host,
                                     port=5432,
                                     database=self._database )


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
