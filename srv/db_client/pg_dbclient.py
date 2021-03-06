import time

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

        # trying to establish the DB connection
        # if it doesn't succeed then we exit application with an error code
        # otherwise proceed with executing SQL procedure
        if not self.connect():
            with self._db_instance.cursor() as cursor:
                cursor.callproc(f"reclada_object.{function_name}", [body,])
                results = cursor.fetchall()
                self._db_instance.commit()
            self._db_instance.close()
        else:
            print(f"Connection to DB can't be established. Check DB's credentials and its availability.")
            exit(1)

        return results

    def connect(self):
        """
            This method connects to DB
        """
        # catch all kind of exceptions here and
        # try reconnecting to DB five times with 10 seconds delay.
        # If connection is established return 0
        # otherwise return -1
        try_number = 1
        while try_number < 5:
            try:
                self._db_instance = ps.connect(f'dbname={self._database}  user={self._user}\
                  password={self._password} host={self._host} connect_timeout=10')
                self._db_instance.autocommit=True
                break
            except Exception as ex:
                try_number += 1
                time.sleep(10)
                continue

        ret_code = -1 if try_number >= 5 else 0
        return ret_code


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

    results = p_dbclient.send_request("list",'{"class": "Job", "attributes": { "status" : "fail" }}')
    jobs_for_processing = results[0]
    for job in jobs_for_processing[0]:
        task_id = job["attributes"]["task"]
        task = p_dbclient.send_request("list",'{"class": "Task", "attributes": { "GUID":"' + job["attributes"]["task"] + '"}}')
        print(job)

