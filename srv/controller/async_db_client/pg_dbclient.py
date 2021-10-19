import asyncio

from srv.controller.async_db_client.dbclient import DBClient
import aiopg as ps
from srv.controller.resource import Resource

class AsyncPgDBClient(DBClient):

    def __init__(self):
        self._host = None
        self._database = None
        self._user = None
        self._password = None
        self._channels = None
        self._loop = asyncio.new_event_loop()
        self._results = None

    async def process_request(self, function_name, payload):
        """
            This method sends a request to call a store procedure in DB
            The name of the store procedure and the payload comes from
            the queue
        """
        # create connection to DB
        dsn = f"user={self._user} password={self._password} host={self._host} dbname={self._database}"

        # create a pool of DB connections
        async with ps.create_pool(dsn) as pool:
            # create a connection for listening notification
            async with pool.acquire() as db_connection:
                cursor = db_connection.cursor()
                await cursor.send("")

        await self.connect()
        with await self._db_instance.cursor() as cursor:
            await cursor.callproc(f"reclada_object.{function_name}", [payload,])
            self._results = await cursor.fetchall()
            await self._db_instance.commit()
        await self._db_instance.close()

        return self._results

    async def connect(self):
        """
            This method connects to DB
        """
        self._db_instance = await ps.connect(f'dbname={self._database}  user={self._user}\
          password={self._password} host={self._host}')
        self._db_instance.autocommit=True


    async def send_request(self, function_name, payload):

        send_task = self._loop.create_task(self.process_request(function_name, payload))
        await send_task

        return self._results


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
    p_dbclient = AsyncPgDBClient()
    p_dbclient.set_credentials("DB", "database.json")
    p_dbclient._loop.run_until_complete(p_dbclient.connect())

    p_dbclient._loop.run_until_complete(p_dbclient.send_request("list", '{"class":"Runner"}'))

    print(f"{p_dbclient._results}")

    results = p_dbclient.send_request("list",'{"class": "Job", "attributes": { "status" : "fail" }}')
    jobs_for_processing = results[0]
    for job in jobs_for_processing[0]:
        task_id = job["attributes"]["task"]
        task = p_dbclient.send_request("list",'{"class": "Task", "attributes": { "GUID":"' + job["attributes"]["task"] + '"}}')
        print(job)

