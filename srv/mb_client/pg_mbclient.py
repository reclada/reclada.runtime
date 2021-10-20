from postgresql.notifyman import NotificationManager
import postgresql
import socket
import signal
from multiprocessing import Process, Queue
from srv.mb_client.mbclient import MBClient
from srv.coordinator.resource import Resource


class TimeOutException(Exception):
   pass

class PgMBClient(MBClient, Process):

    def __init__(self):
        Process.__init__(self)
        self._queue = None
        self._host = None
        self._database = None
        self._user = None
        self._password = None
        self._channels = None
        self._timeout = 300
        self._retry_number = 5
        self._log = None

    def set_log(self,log):
        self._log = log

    def log(self,message):
        if self._log :
            self._log.debug(message)

    def handle_request(self, body, block):
        """
            This method is called when a new message arrives
        :param body: message body
        """
        self._queue.put(body,block=block)

    def _signal_handler_connection(self, signum, frame):
        """
            This method handles timeout of connection to DB
            If timeout expires then the application should be restarted
        """
        self.log('There was a delay in establishing connection to DB')
        raise TimeOutException()


    def _signal_handler_listen(self, signum, frame):
        """
            This method handles timeout of listening notifications from DB
            If timeout expires then the new connection to DB should be created
        """
        # open another DB connection
        self.log('There was a delay in processing idle events. ')
        self._open_db_connection()
        self.log('The new DB connection was opened.')
        raise TimeOutException()


    def run(self):
        """
            This method gets called to start the loop of message handling
        """

        # open a DB connection
        # if the connection can't be established then
        # a kill message is put to the queue
        if self._open_db_connection():
            self.log("Can't establish connection to DB.")
            self.handle_request(1, True)

        # send a listen command to PostgreSQL server
        self.log("Starts listening notifications.")
        self._pgc.listen(self._channels)

        # reading notification from the channel
        self._listen_to_channel()

    def _listen_to_channel(self):
        """
            This method listens to the channel to get notifications
        """

        retry_number = 1
        self.log("Setting an alarm handler for idle events processing.")
        signal.signal(signal.SIGALRM, self._signal_handler_listen)

        while retry_number < self._retry_number:
            self.log("Creating Notification Manager.")
            nm = NotificationManager(self._pgc)
            self.log("Notification Manager has been created.")
            nm.settimeout(self._timeout)
            self.log("Timeout for Notification Manager has been set.")
            try:
                # set on alarm for new notifications
                self.log(f"Setting alarm for {self._timeout*2} sec.")
                signal.alarm(self._timeout * 2)
                for message in nm:
                    # set off alarm for new notifications
                    signal.alarm(0)
                    self.log("Gets an idle event. Alarm off.")
                    # if timeout happens then we don't need
                    # to process the message
                    if message is None:
                        # check for bad connections
                        if nm.garbage:
                            self.log(f'Clearing bad DB connections.')
                            nm.garbage.clear()
                        # close the old connection
                        self.log("Closing the current DB connection.")
                        self._pgc.close()
                        # open another DB connection
                        self.log("Opening a new DB Connection.")
                        self._open_db_connection()
                        # here we need to set an alarm handler one more time
                        # since in open_db_connection() another alarm handler was used.
                        signal.signal(signal.SIGALRM, self._signal_handler_listen)
                        signal.alarm(self._timeout*2)
                        # update connections in Notification Manager with the new connection
                        self.log("Adding a new DB connection to Notification Manager.")
                        nm.connections.update([self._pgc, ])
                        # send request to listening the notification channel
                        self.log("Starts listening for notifications.")
                        self._pgc.listen(self._channels)
                        # handle the request
                        self.handle_request(0, False)
                        continue
                    # if a message arrived then
                    # we need to check the name of
                    # the channel and if it equals the name
                    # of the channel specified in Resource then
                    # we need to handle it properly
                    self.log(f'Processing a new event.')
                    db, notifies = message
                    for channel, payload, pid in notifies:
                        if channel == self._channels:
                            self.log("Putting a message to the queue.")
                            self.handle_request(payload, False)
                    signal.alarm(self._timeout)
            except TimeOutException:
                signal.alarm(0)
                self.log(f"Notification Manager hangs. Trying to restore it. Retry number {retry_number}")
                retry_number += 1
                continue
            except Exception as ex:
                signal.alarm(0)
                self.log(f'Exception happened in Notification Manager. {format(ex)}')
                retry_number += 1
                continue

            retry_number += 1
            # It looks like we lost connection to DB and
            # it needs to be recreated
            self.log(f"The DB connection gets recreated {retry_number} time. ")
            self._open_db_connection()

        # Message Broker needs to be recreated.
        self.log(f"The number of attempts have been exceed.")
        self.log(f"The Message Client needs to be recreated.")
        self.handle_request(2, True)


    def _open_db_connection(self):
        """
            This method creates a DB connection
        """

        retry_number = 1
        signal.signal(signal.SIGALRM, self._signal_handler_connection)

        # we have to make sure that connection to DB
        # can be established. There are some number of retries which
        # how many attempts would be done to establish the DB connection
        while retry_number < self._retry_number:
            try:
                # setting an alarm to notify if establishing connection to DB
                # takes too much time
                signal.alarm(self._timeout*10)
                # create connection to DB
                self.log("Connecting to Message Broker.")
                self._pgc = postgresql.open( user=self._user,
                                             password=self._password,
                                             host=self._host,
                                             port=5432,
                                             database=self._database )
                self.log("Connected to Message Broker.")

                s = socket.fromfd(self._pgc.fileno(), socket.AF_INET, socket.SOCK_STREAM)
                # enable sending of keep-alive messages
                s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # time the connection needs to remain idle before start sending keepalive probes
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 20)
                # time between individual keepalive probes
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                # the maximum number of keepalive probes should send before dropping the connection
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, 70000)
                self.log("Additional configuration parameters were set.")
                signal.alarm(0)
                break
            except TimeOutException:
                signal.alarm(0)
                self.log(f"Retrying to establish connection to MB. Retry Number {retry_number}")
                retry_number += 1
                continue
            except Exception:
                print(f"Can't establish connection to DB.")
                retry_number += 1
                signal.alarm(0)
                continue

        # if after some retries connection to DB can't
        # be established then exit the application and print an error message
        ret_code = -1 if retry_number >= self._retry_number else 0
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
