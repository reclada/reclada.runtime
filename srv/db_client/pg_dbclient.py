from srv.db_client.dbclient import DBClient
import psycopg2 as ps
from srv.coordinator.resource import Resource

class PgDBClient(DBClient):

    def __init__(self):
        self._host = None
        self._database = None
        self._user = None
        self._password = None
        self._channels = None
        self._db_instance = None

    def send_request(self, function_name, body):
        """
            This method sends a request to call a store procedure in DB
        :param function_name: a name of a store procedure to be called in DB
        :param body: a json object with parameters of the request
        """
        # before sending a request to DB we need to check if
        # the connection is still open and if it is not then
        # connect to DB again
        try:
            # In order to make sure a connection is still valid, read the property connection.isolation_level.
            # This will raise an OperationalError in case the connection is dead.
            self._db_instance.isolation_level
        except ps.OperationalError as oe:
            self.connect()
            print(format(oe))

        cursor = self._db_instance.cursor()
        cursor.callproc(f"reclada_object.{function_name}", [body,])
        return cursor.fetchall()

    def connect(self):
        """
            This method connects to DB
        """
        self._db_instance = ps.connect(f'dbname={self._database}  user={self._user}\
          password={self._password} host={self._host} connect_timeout=0',
                                       keepalives=1,
                                       keepalives_idle=30,
                                       keepalives_interval=10,
                                       keepalives_count=5
                                       )
        self._db_instance.autocommit=True


    def set_credentials(self, type, json_file):
        """
              This method sets the credential to connect to PostgreSQL DB
        :param type: the type of DB connection
        :param json_file: json_file with credentials
        """
        res = Resource()
        res = res.get(type, json_file)

        self._host = res.host
        self._database = res.database
        self._user = res.user
        self._password = res.password


if __name__ == "__main__":
    p_dbclient = PgDBClient()
    p_dbclient.set_credentials("DB", "database.json")
    p_dbclient.connect()

    results = p_dbclient.send_request("list", '{"class":"jsonschema"}')

    results = p_dbclient.send_request("list",'{"class": "Job", "attrs": { "status" : "fail" }}')
    jobs_for_processing = results[0]
    for job in jobs_for_processing[0]:
        task_id = job["attrs"]["task"]
        task = p_dbclient.send_request("list",'{"class": "Task", "attrs": { "id":"' + job["attrs"]["task"] + '"}}')
        print(job)

