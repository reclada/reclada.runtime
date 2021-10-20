#!/usr/bin/python3
from multiprocessing import Queue
from collections import namedtuple, Counter
from enum import Enum
import json
import click
import time
import logging
import subprocess
import os
import sys

from srv.coordinator._version import __version__
from srv.coordinator.stage.stage_factory import stage
from srv.mb_client.mbclient_factory import mbclient
from srv.db_client.dbclient_factory import dbclient
import srv.logger.logger as log

Stage = namedtuple("Stage", "type reference runners")
Runner = namedtuple("Runner", "id number_of_jobs state")

class RunnerState(Enum):
    BUSY = "up"
    DOWN = "down"
    IDLE = "idle"

class Coordinator():

    def __init__(self, platform, message_client, database_client, lg):
        self._log = lg
        self._stage = stage.get_stage(platform)
        self._message_client = mbclient.get_client(message_client)
        self._message_client_name = message_client
        self._message_client.set_log(self._log)
        self._db_client = dbclient.get_client(database_client)
        self._queue = Queue()
        self._stages = {}
        self._database_type = database_client

    def start(self):
        """
            This method starts processing messages from a message broker
        """
        # sets credentials to connect to MB
        if self._message_client.set_credentials("MB", None):
            self._log.error("Not enough information for Message Broker Client.")
            return
        self._log.debug('Credentials for Message Broker has been set.')

        # sets the queue to exchange messages between
        # broker and coordinator
        self._message_client.set_queue(self._queue)
        # sets credentials to DB's connection
        self._db_client.set_credentials("DB", None)
        self._log.debug('Credentials for Database Client has been set.')

        self._db_runner = RunnerDB(self._db_client, self._log)
        self._db_jobs = JobDB(self._db_client, self._log)

        # before starting pooling we need to check DB
        # for new jobs
        self._log.debug('Checking DB for new jobs and process them if it is needed.')
        self.process_reclada_message(None)

        # start the client to receive messages in a separate process
        try:
            self._log.debug('Starts waiting for new notifications.')
            self._message_client.start()
        except Exception as ex:
            self._log.error(format(ex))
            raise ex

        while True:
            message = self._queue.get(block=True)
            if type(message) is int and int(message) == 0:
                self._log.debug('Received an idle event.')
                # check for new jobs in DB
                self.process_reclada_message(0)
                # we need to log this message only once
                # so if the flag block_awaiting is not set to False
                # then we log this message otherwise just skip it
                self._log.info("Awaiting for notifications...")
            elif type(message) is int and int(message) == 1:
                # there is a problem with DB connection and
                # application should be restarted
                self._log.debug('Received a kill message and Coordinator is going to be restarted.')
                self._log.debug(f'Current folder for starting Coordinator cwd={os.getenv("RECLADA_REPO_PATH")}')
                subprocess.Popen("./run_coordinator.sh", cwd=os.getenv("RECLADA_REPO_PATH"), shell=True, executable='/bin/bash')
                return
            elif type(message) is int and int(message) == 2:
                # there is a problem with the Notification Manager and
                # MB client needs to be recreated
                self._log.debug("Message Client needs to be recreated.")
                self._message_client = mbclient.get_client(self._message_client_name)
                self._log.debug("Setting up parameters for Message Client.")
                self._message_client.set_credentials("MB", None)
                self._message_client.set_queue(self._queue)
                self._log.debug("Starting the Message Broker.")
                self._message_client.start()
            else:
                self._log.info(f"A new notification was received.")
                # return the flag block_awaiting to the initial state
                self.process_reclada_message(message)

        self._message_client.join()

    def process_reclada_message(self, reclada_message):
        """
            This method processing all new jobs found in DB
            :param message: message that was received from PostgreSQL
        """

        # get all runners in different statuses
        # change statuses of runners with Idle state to
        # Down if last_update happened more than 5
        # minutes ago
        self._log.debug(f'Reading Runners from DB.')
        self.pre_process_runners()

        self._log.debug(f'Processing reclada messages.')
        # start the loop for job processing
        while True:
            # read new jobs from the database
            self._jobs_to_process = self._db_jobs.get_new()
            self._log.info(f"Reading new jobs from DB")
            # if no jobs were found then stop the loop
            if not self._jobs_to_process[0][0]:
                self._log.info(f"No new jobs found in DB")
                # here we need to empty the Queue with the messages
                # since the multiple entries in the queue might be due
                # to the fact that lambda function triggers on every file added
                # to the S3 bucket.
                self._log.debug('Cleaning the queue.')
                while(not self._queue.empty()):
                    self._queue.get_nowait()
                self._log.debug('The queue is empty.')
                break

            # process found new jobs
            for job in self._jobs_to_process[0][0]:
                # finding the type of the staging
                type_of_staging = job["attributes"]["type"]
                type_of_staging = type_of_staging.strip()
                self._log.info(f"New jobs found for resource {job['attributes']['type']}")
                # find in DB all runners for the specified platform with status DOWN
                runners = self._db_runner.get_all(type_of_staging)
                # if no stages of the specified type were found then
                # we need to create that platform
                if not self._stages.get(type_of_staging, None):
                    # creating stage on the specified platform
                    ref_stage = self._stage.create_stage(type_of_staging)
                    self._log.debug(f"The new resource {type_of_staging} was created.")
                    # adding stage to the coordinator's dictionary
                    self._stages[type_of_staging] = Stage(type_of_staging, ref_stage, [])
                # if runners found in DB then add them to the dictionary
                if runners[0][0]:
                    runners_found = [Runner(run["GUID"], 0, run["attributes"]["status"]) for run in runners[0][0]]
                    self._stages[type_of_staging].runners.clear()
                    self._stages[type_of_staging].runners.extend(runners_found)
                    self._log.info(f"Found {len(runners_found)} runners")

                # find the suitable runner for the job in the dictionary
                runner = self.find_runner(type_of_staging)
                # if no idle runners were found then find the runner with the status down
                if not runner:
                    runners_down = [runner for runner in self._stages[type_of_staging].runners if runner.state == "down"]
                    if runners_down:
                        # select the first found runner which is in DOWN state
                        runner = runners_down[0]
                        # create the runner of the platform
                        self._stage.create_runner(type_of_staging, runner.id, self._database_type)
                        self._log.info(f"Runner with id {runner.id} was created.")
                        # updating the status for the runner to save it to DB
                        self.update_runner_status(runners, runner)
                        self._log.debug(f"The status for runner {runner.id} was changed to 'up'")
                    else:
                        self._log.debug(f"No idle or down runners were found.")
                        jobs_pending = self._db_jobs.get_pending(type_of_staging)
                        runner = self.find_runner_minimum_jobs(type_of_staging, jobs_pending)
                        self._log.debug(f"Trying to find runners with minimum jobs")
                else:
                    self.update_runner_status(runners, runner)
                    self._log.debug(f"The status for runner {runner.id} was changed to 'up'")

                # here we need to update reclada jobs with the runner id if runner exists
                if runner:
                    job["attributes"]["runner"] = runner.id
                    job["attributes"]["status"] = "pending"
                    self._db_jobs.save(job)
                    self._log.info(f"The job with id {job['GUID']} was assigned to the runner {runner.id}")
                else:
                    job["attributes"]["status"] = "failed"
                    self._db_jobs.save(job)
                    self._log.info(f"No runners were found for resource {type_of_staging}")
        self._log.debug('Reclada messages have been processed.')

    def find_runner(self, type_of_staging):
        """
            This method returns the first idle runner and if there is no such runner it returns None
        """
        # check if we have runners associated with the specified stage
        if self._stages[type_of_staging].runners:
            # finds the idle or newly created runner
            # on the specified stage if it is found then return its id
            for runner in self._stages[type_of_staging].runners:
                if runner.state == RunnerState.IDLE.value:
                    return runner
        # if there are no idle or new runners then returns None
        return None

    def update_runner_status(self, runners, runner):
        """
            This method saves the status of the runner in DB and changes the status of the runner
            to "up"
        """
        runner_to_save = [run for run in runners[0][0] if run["GUID"] == runner.id]
        runner_to_save[0]["attributes"]["status"] = "up"
        self._db_runner.save(runner_to_save)

    def find_runner_minimum_jobs(self, type_of_staging, jobs_pending):
        """
            This method return the runner with the minimum jobs assigned to it
        :param type_of_staging:
        :return: runner
        """

        # from jobs found in DB determine runner id for
        # the minimum jobs were assigned
        if jobs_pending[0][0]:
            jobs_for_runner = [job["attributes"]["runner"] for job in jobs_pending[0][0]]
            jobs_count = Counter(jobs_for_runner)
            jobs_count = jobs_count.most_common()
            runner = [ runner for runner in self._stages[type_of_staging].runners if runner.id == jobs_count[-1][0]]
            return runner[0]

    def update_runner(self, type_of_staging, runner):
        """
            This method updates the list of runneres in the dictionary
        """
        # since attribute of a named tuple can't be changed
        # we need to create a new named tuple and replace the old one with the new named tuple
        new_runners =[Runner(runner.id, runner.number_of_jobs, runner.state)
                      if run.id == runner.id else run for run in self._stages[type_of_staging].runners]
        # creating the new Stage named tupled
        stage = Stage(self._stages[type_of_staging].type,
                      self._stages[type_of_staging].reference,
                      new_runners)
        # updating the dictionary with the new Stage
        self._stages[type_of_staging] = stage

    def pre_process_runners(self):
        """
            This method checks for runners in Idle state with last_update more
            than 5 minutes ago and return status of this runner to down
        """
        runners = self._db_runner.get_all()
        if runners[0][0]:
            for runner in runners[0][0]:
                last_update = runner.get("attributes").get("last_update", None)
                if last_update and runner["attributes"]["status"] == RunnerState.IDLE.value:
                    # converting last_update datetime to time format
                    last_time = time.strptime(last_update, "%Y/%m/%d %H:%M:%S")
                    last_time = time.mktime(last_time)

                    # if the difference between last_update time and current time more than 5 minutes
                    # then we need to changes status of the runner to Down
                    if runner["attributes"]["status"] == RunnerState.IDLE.value and time.time() - last_time > 300:
                        runner["attributes"]["status"] = RunnerState.DOWN.value
                        self._log.info(f"The state of runner {runner['GUID']} was restored to DOWN.")
                        self._db_runner.save([runner])


class RunnerDB():
    """
        This class organize the work with DB for reclada runner objects
    """
    def __init__(self, db_connection, log):
        self._db_connection = db_connection
        self._log = log

    def get_all(self, type_staging=None):
        """
            This method selects runner objects from DB with status DOWN
        :param type_staging: defines the platform for which runners are looked for
        :return: the list of named tuple Runners
        """
        try:
            # forming json structure for searching runner that is not running now
            if type_staging:
                select_json = {'class': 'Runner', 'attributes': {'type': type_staging}}
            else:
                select_json = {'class': 'Runner'}

            # sending request to DB to select runner objects from DB
            runners = self._db_connection.send_request("list", json.dumps(select_json))
        except Exception as ex:
            self._log.error(format(ex))
            raise ex
        return runners


    def save(self, runner):
        """
            This method creates the reclada object for runner
        :param runner: named tuple with the information for runner
        """
        try:
            # sending request to DB to create reclada runner object
            self._db_connection.send_request("update", json.dumps(runner[0]))
        except Exception as ex:
            self._log.error(format(ex))
            raise ex


class JobDB():
    """
        This class organize the work with DB for job objects
    """
    def __init__(self, db_connection, log):
        self._db_connection = db_connection
        self._log = log

    def get_new(self):
        """
            This method selects all new job objects from DB
        :return: the list of Job objects
        """
        try:
            # creating json structure for a query
            jobs_new = {"class": "Job", "attributes": {"status": "new"}}
            # sending request to DB to select all new jobs
            jobs_new = self._db_connection.send_request("list", json.dumps(jobs_new))
        except Exception as ex:
            self._log.error(format(ex))
            raise ex
        return jobs_new

    def get_pending(self, type_of_staging):
        """
            This method selects all pending jobs from DB
        :return: the list of Job objects
        """
        try:
            # creating json structure for a query
            jobs_pending = {"class": "Job", "attributes": {"status": "pending", "type": type_of_staging }}
            # sending request to DB to select all new jobs
            jobs_pending = self._db_connection.send_request("list", json.dumps(jobs_pending))
        except Exception as ex:
            self._log.error(format(ex))
            raise ex
        return jobs_pending

    def save(self, job):
        """
            This method saves the job object to DB
        :param job: job object
        """
        try:
            # sending a request to create an updated version of the job
            self._db_connection.send_request("update", json.dumps(job))
        except Exception as ex:
            self._log.error(format(ex))
            raise ex


@click.command()
@click.option('-version', count=True)
@click.option('-platform', default='K8S', type=str)
@click.option('-database', default='POSTGRESQL', type=str)
@click.option('-messenger', default='POSTGRESQL', type=str)
@click.option('-verbose', count=True)
def run(platform, database, messenger, verbose, version):

    # if version option is specified then
    # print version number and quit the app
    if version:
        print(f"Coordinator version {__version__}")
        return

    # checking if verbose option was specified and
    # if it was then create the logger for debugging otherwise
    # the logger would save only INFO messages
    if verbose:
        lg = log.get_logger("coordinator", logging.DEBUG, "/mnt/output/coordinator.log")
    else:
        lg = log.get_logger('coordinator', logging.INFO, "/mnt/output/coordinator.log")

    lg.info(f"Coordinator v{__version__} started")
    # starting coordinator
    coordinator = Coordinator(platform, messenger, database, lg)
    coordinator.start()


if __name__ == "__main__":
    run()