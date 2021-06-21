from multiprocessing import Queue
from stage.stage_factory import stage
from mb.mbclient_factory import mbclient
from db.dbclient_factory import dbclient
from collections import namedtuple
from enum import Enum
import json

Stage = namedtuple("Stage", "type reference runners")
Runner = namedtuple("Runner", "id number_of_jobs, state")

class RunnerState(Enum):
    NEW = 1
    BUSI = 2
    DOWN = 3
    IDLE = 4

class Coordinator():

    def __init__(self, platform, message_client, database_client):
        self._stage = stage.get_stage(platform)
        self._message_client = mbclient.get_client(message_client)
        self._db_client = dbclient.get_client(database_client)
        self._queue = Queue()
        self._stages = {}
        self._database_type = database_client

    def start(self):
        """
            This method starts processing messages from a message broker
        """
        # sets credentials to connect to MB
        self._message_client.set_credentials("MB", None)
        self._message_client.set_queue(self._queue)
        self._db_client.set_credentials("DB", None)
        self._db_client.connect()
        self._db_runner = RunnerDB(self._db_client)
        self._db_jobs = JobDB(self._db_client)

        # start the client to receive messages in a separate process
        self._message_client.start()
        while True:
            message = self._queue.get(block=True)
            self.process_reclada_message(message)

        self._message_client.join()


    def process_reclada_message(self, reclada_message):
        """
            This method processing all new jobs found in DB
            :param message: message that was received from PostgreSQL
        """

        # start the loop for job processing
        while True:
            # read new jobs from the database
            self._jobs_to_process = self._db_jobs.get_new()
            # if no jobs were found then stop the loop
            if not self._jobs_to_process:
                break

            # process found new jobs
            for job in self._jobs_to_process[0][0]:
                # finding the type of the staging
                type_of_staging = job["attrs"]["type"]
                # if no stages of the specified type were found then
                # we need to create that platform
                if not self._stages.get(type_of_staging, None):
                    ref_stage = self._stage.create_stage(type_of_staging)
                    self._stages[type_of_staging] = Stage(type_of_staging, ref_stage, [])
                    runners = self._db_runner.get_all_down(type_of_staging)
                    if runners[0][0]:
                        runners_found = [Runner(run["id"], 0, run["attrs"]["status"]) for run in runners[0][0]]
                        self._stages[type_of_staging].runners.extend(runners_found)

                # find the suitable runner for the job
                runner = self.find_runner(type_of_staging)
                # if no idle runners were found then find the runner with the minimum jobs
                if not runner:
                    runners_down = list(filter(lambda x : x.state == "DOWN", self._stages[type_of_staging].runners))
                    if runners_down:
                        # select the first found runner which is in DOWN state
                        runner = runners_down[0]
                        # create the runner of the platform
                        self._stage.create_runner(type_of_staging, runner.id, self._database_type)
                        # updating the state and number of jobs for the runner
                        runner.state="NEW"
                        runner.number_of_jobs = 1
                        # saving the new state of runner in DB
                        self._db_runner.save(runner)
                    else:
                        runner = self.find_runner_minimum_jobs(type_of_staging)
                        if runner:
                            runner.number_of_jobs += 1
                            self._db_runner.save(runner)

                # here we need to update reclada jobs with the runner id if runner exists
                if runner:
                    job["attrs"]["runner"] = runner["id"]
                    self._db_jobs.save(job)
                else:
                    job["attrs"]["status"] = "failed"
                    self._db_jobs.save(job)

    def find_runner(self, type_of_staging):
        """
            This method returns the first idle runner and if there is no such runner it returns None
        """
        # check if we have runners associated with the specified stage
        if self._stages[type_of_staging].runners:
            # finds the idle or newly created runner
            # on the specified stage if it is found then return its id
            for runner in self._stages[type_of_staging].runners:
                if runner.state == RunnerState.IDLE or runner.state == RunnerState.NEW or RunnerState.DOWN:
                    return runner.id
        # if there are no idle or new runners then returns None
        return None

    def find_runner_minimum_jobs(self, type_of_staging):
        """
            This method return the runner with the minimum jobs assigned to it
        :param type_of_staging:
        :return: runner
        """
        # check if we have runners associated with the specified stage
        runner = None
        if self._stages[type_of_staging].runners:
            # find runner with the minimum number of jobs assigned to it
           runner = min(self._stages[type_of_staging].runners, key=lambda x : x.number_of_jobs)
        return runner


class RunnerDB():
    """
        This class organize the work with DB for reclada runner objects
    """
    def __init__(self, db_connection):
        self._db_connection = db_connection

    def get_all_down(self, type_staging):
        """
            This method selects runner objects from DB with status DOWN
        :param type_staging: defines the platform for which runners are looked for
        :return: the list of named tuple Runners
        """
        try:
            # forming json structure for searching runner object
            select_json = { 'class': 'Runner', 'attrs': {'status': 'down', 'type': type_staging}}
            # sending request to DB to select runner objects from DB
            runners = self._db_connection.send_request("list", json.dumps(select_json))
        except Exception as ex:
            print(format(ex))
            raise ex
        return runners


    def save(self, runner):
        """
            This method creates the reclada object for runner
        :param runner: named tuple with the information for runner
        """
        try:
            # forming json structure for runner
            runner_json = {'id': runner.id, 'class': 'Runner', 'attrs': {'state': runner.state}}
            # sending request to DB to create reclada runner object
            self._db_connection.send_request("create", json.dumps(runner_json))
        except Exception as ex:
            print(format(ex))
            raise ex


class JobDB():
    """
        This class organize the work with DB for job objects
    """
    def __init__(self, db_connection):
        self._db_connection = db_connection

    def get_new(self):
        """
            This method selects all new job objects from DB
        :return: the list of Job objects
        """
        try:
            # creating json structure for a query
            jobs_new = {"class": "Job", "attrs": {"status": "new"}}
            # sending request to DB to select all new jobs
            jobs_new = self._db_connection.send_request("list", json.dumps(jobs_new))
        except Exception as ex:
            print(format(ex))
            raise ex

        return jobs_new

    def save(self, job):
        """
            This method saves the job object to DB
        :param job: job object
        """
        try:
            # sending a request to create an updated version of the job
            self._db_connection.send_request("create", json.dumps(job))
        except Exception as ex:
            print(format(ex))
            raise ex



if __name__ == "__main__":

    coordinator = Coordinator("DUMMY", "POSTGRESQL", "POSTGRESQL")
    coordinator.start()

