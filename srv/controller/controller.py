#!/usr/bin/python3
# from multiprocessing import Queue
from asyncio.queues import Queue
from collections import namedtuple, Counter
from enum import Enum
import json
import asyncclick as click
import time
import logging
import asyncio

from srv.controller._version import __version__
from srv.coordinator.stage.stage_factory import stage
from srv.mb_client.mbclient_factory import mbclient
from srv.db_client.dbclient_factory import dbclient
import srv.logger.logger as log

class Controller():

    def __init__(self, platform, message_client, database_client, lg):
        self._log = lg
        self._stage = stage.get_stage(platform)
        self._message_client = mbclient.get_client(message_client)
        self._db_client = dbclient.get_client(database_client)
        self._queue = Queue()
        self._stages = {}
        self._database_type = database_client
        self._block_awaiting = False

    async def start(self):
        """
            This method starts processing messages from a message broker
        """
        # sets credentials to connect to MB
        if self._message_client.set_credentials("MB", None):
            self._log.error("Not enough information for Message Broker Client.")
            return

        # sets the queue to exchange messages between
        # broker and coordinator
        self._message_client.set_queue(self._queue)
        # sets credentials to DB's connection
        self._db_client.set_credentials("DB", None)

        # start the client to receive messages in a separate process
        try:
            self._message_client.start()
        except Exception as ex:
            self._log.error(format(ex))
            raise ex

        while True:

            await self.read_message()
            p=2.3

        self._message_client.join()


    async def read_message(self):
        message = await self._queue.get()
        if type(message) is int and int(message) == 0:
            # we need to log this message only once
            # so if the flag block_awaiting is not set to False
            # then we log this message otherwise just skip it
            if not self._block_awaiting:
                self._log.info("Awaiting for notifications...")
                self._block_awaiting = True
        else:
            self._log.info(f"A new notification was received.")
            # return the flag block_awaiting to the initial state
            self._block_awaiting = False




@click.command()
@click.option('-version', count=True)
@click.option('-platform', default='K8S', type=str)
@click.option('-database', default='POSTGRESQL', type=str)
@click.option('-messenger', default='POSTGRESQL', type=str)
@click.option('-verbose', count=True)
async def run(platform, database, messenger, verbose, version):

    # if version option is specified then
    # print version number and quit the app
    if version:
        print(f"Controller version {__version__}")
        return

    # checking if verbose option was specified and
    # if it was then create the logger for debugging otherwise
    # the logger would save only INFO messages
    if verbose:
        lg = log.get_logger("controller", logging.DEBUG, "contoller.log")
    else:
        lg = log.get_logger('controller', logging.INFO, "controller.log")

    lg.info(f"Controller v{__version__} started")
    # starting coordinator
    controller = Controller(platform, database, messenger, lg)
    await controller.start()


if __name__ == "__main__":
    asyncio.run(run())