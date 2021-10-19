import datetime
import json

import aiopg
import asyncio
from asyncio.queues import Queue

from srv.controller.async_mb_client.mbclient import MBClient
from srv.controller.resource import Resource


class AsyncPgMBClient(MBClient):

    def __init__(self, loop):
        self._queue_received = Queue(loop=loop, maxsize=1000)
        self._queue_to_send = Queue(loop=loop, maxsize=1000)
        self._host = None
        self._database = None
        self._user = None
        self._password = None
        self._channels = None
        self._loop = loop

    async def handle_request(self, body):
        """
            This method is called when a new message needs to be sent
        :param body: message body
        """
        await self._queue_to_send.put(body)

    async def run(self):
        """
            This method prepares tasks for running inside the asyncio loop
        """
        # create connection to DB
        dsn = f"user={self._user} password={self._password} host={self._host} dbname={self._database}"

        # create a pool of DB connections
        async with aiopg.create_pool(dsn) as pool:
            # create a connection for listening notification
            async with pool.acquire() as listen_connection:
                # create async object for listener
                listener = self.listen_from(listen_connection)
                # create a connection for sending notifications
                async with pool.acquire() as send_connection:
                    # create async object for sending notifications
                    notifier = self.send_to(send_connection)
                    # create a connection for keep_alive event
                    async with pool.acquire() as keep_alive_connection:
                        # create async object for keep_alive event
                        keep_alive = self.keep_alive(keep_alive_connection)
                    # start an async loop
                    await asyncio.gather(listener, notifier, keep_alive)

    async def listen_from(self, connection):
        """
            This method waits for arriving new messages
        """
        # creates a cursor from connection supplied as an input parameter
        async with connection.cursor() as cur:
            # send a request to DB to listen messages on the specified channel
            await cur.execute(f"LISTEN {self._channels}")
            # creates the infinite loop to listen for messages
            while True:
                # waits for messages and handles them
                msg = await connection.notifies.get()
                js_message = json.loads(msg.payload)
                js_message_type = js_message.get('MsgType')
                if js_message_type is not None:
                    # if message is a keep_alive message then do nothing and
                    # continue looping
                    if js_message_type == 0:
                        print(f'Keep alive -> {datetime.datetime.now()}')
                        continue
                    else:
                        # other messages need to put in out queue
                        await self._queue_received.put(msg.payload)
                else:
                    # if the message doesn't have a right format
                    # just print a message and continue looping
                    print(f'Message is not supported {js_message}')

    async def send_to(self, connection):
        """
            This method sends a message to the specified channel
        """
        # create a cursor on the specified channel
        async with connection.cursor() as cur:
            # create an infinite loop
            while True:
                # waiting for a message which is supposed to be sent
                msg = await self._queue_to_send.get()
                # sending the message by execution a DB query
                await cur.execute(f"NOTIFY {self._channels}, %s", (json.dumps(msg),))

    async def keep_alive(self, connection):
        # create an infinite loop for keep_alive messages
        while True:
            # sleep for 10 seconds
            await asyncio.sleep(10)
            # creates a keep_alive message
            msg = {
                'MsgType': 0
            }
            # put the message to the out queue
            await self.handle_request(msg)

    async def get_message(self):
        """
            This method gets a first message from the queue
        """
        return await self._queue_received.get()

    async def send_message(self, msg):
        """
            This method puts a message to the output queue
        """
        return await self._queue_to_send.put(msg)

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


if __name__ == "__main__":
    q_mbclient_in = Queue()
    q_mbclient_out = Queue()
    loop=asyncio.get_event_loop()
    p_mbclient = AsyncPgMBClient(loop)
    p_mbclient.set_credentials("MB", None)
    print(" [x] Awaiting requests")

    asyncio.ensure_future(p_mbclient.run())
    loop.run_forever()

