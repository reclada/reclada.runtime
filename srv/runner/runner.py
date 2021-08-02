import json
import logging
import os
import subprocess
import sys
import time
from enum import Enum
from datetime import datetime

import click

from srv.db_client.dbclient_factory import dbclient
from srv.job.job import JobStatus, JobDB
from srv.logger import logger
from srv.s3.s3 import S3
from srv.runner._version import __version__


class RunnerError(Exception):
    pass


class RunnerStatus(Enum):
    UP = 'up'
    IDLE = 'idle'
    DOWN = 'down'


class Runner:
    """
    Gets jobs from DB and runs them
    """
    def __init__(self, id_, status, command, type_, task, environment, runner_db, job_db, s3, runner_logger):
        self.id = id_
        self._status = status
        self.command = command
        self.type = type_
        self.task = task
        self.environment = environment
        self._runner_db = runner_db
        self._job_db = job_db
        self._s3 = s3
        self._logger = runner_logger

        self._jobs = []

    def __repr__(self):
        return f'Runner {self.id} with status {self.status} having {len(self.jobs)} jobs'

    @property
    def status(self):
        """
        Gets runner status

        """
        return self._status

    @status.setter
    def status(self, new_status):
        """
        Sets runner status

        """
        if new_status not in RunnerStatus:
            error = ValueError(f'Runner status {new_status.value} is not allowed')
            self._logger.error(error)
            raise error

        self._status = new_status

    @property
    def jobs(self):
        """
        Gets list of jobs

        """
        return self._jobs

    def get_new_jobs(self):
        """
        Gets new jobs from DB

        """
        self._jobs = self._job_db.get_jobs(self.id, JobStatus.PENDING.value)
        if len(self._jobs) > 1:
            self._logger.info(f'Runner {self.id} received {len(self._jobs)} jobs')
        elif len(self._jobs) == 1:
            self._logger.info(f'Runner {self.id} received {len(self._jobs)} job')
        else:
            self._logger.info(f'No jobs for runner {self.id}')

    def run_job(self, job):
        """
        Runs job

        """
        # updates job status in DB to "running"
        job.status = JobStatus.RUNNING
        self._job_db.save_job(job)
        self._logger.info(f'Runner {self.id} changed job {job.id} status to {job.status.value}')

        # runs job
        # TODO: resolve all input parameters
        s3_uri = job.input_parameters[0]['uri']
        file_id = job.input_parameters[1]['dataSourceId']
        command = job.command.split()
        self._logger.info(f'Runner {self.id} is launching job {job.id} with command {job.command} '
                          f'and parameters {job.input_parameters}')

        # Here we need to check if CUSTOM_TASK environment is defined
        # if yes then we need to add extra parameter for run_pipeline.sh
        custom_task = os.getenv('CUSTOM_TASK', None)
        # prepare folder's names for S3 bucket
        s3_output_dir = datetime.now().strftime("%Y/%m/%d/%H:%M:%S:%f/")
        s3_output_dir += job.id
        params = [s3_uri, file_id, job.id, s3_output_dir]
        if custom_task:
            params.append(custom_task)

        job_result = subprocess.run(command + params, cwd=os.getenv('RECLADA_REPO_PATH'))

        # updates job status in DB depending on the job return code
        if job_result.returncode == 0:
            job.status = JobStatus.SUCCESS
        else:
            job.status = JobStatus.FAILED
        self._job_db.save_job(job)
        self._logger.info(f'Runner {self.id} changed job {job.id} status to {job.status.value}')

        return job_result

    def run(self):
        """
        Gets jobs from DB and runs them

        """
        start = time.time()

        # Before processing new jobs we need to check
        # if there are jobs in Running state. If yes then
        # we need to change there statuses to Pending
        self.pre_process()

        while True:
            self.get_new_jobs()

            if self.jobs:
                # updates runner status in DB to "up" when all jobs finished
                self.status = RunnerStatus.UP
                self._runner_db.save_runner(self)
                self._logger.info(f'Runner {self.id} changed its status to {self.status.value}')

                # process all new jobs found in DB
                for job in self.jobs:
                    job_result = self.run_job(job)
                    job_stdout = job_result.stdout
                    job_stderr = job_result.stderr
                    job_returncode = job_result.returncode

                # updates runner status in DB to "idle" when all jobs finished
                self.status = RunnerStatus.IDLE
                self._runner_db.save_runner(self)
                self._logger.info(f'Runner {self.id} changed its status to {self.status.value}')
                start = time.time()
            else:
                self._logger.info(f'Runner {self.id} is waiting for new jobs')
                # update runner object in reclada DB with last_update
                self._runner_db.save_runner(self)
                time.sleep(10)

            stop = time.time()
            if stop - start > 300:
                # updates runner status in DB to "down" and
                # shutdowns runner if there was no jobs for 5 mins
                self.status = RunnerStatus.DOWN
                self._runner_db.save_runner(self)
                self._logger.info(f'Runner {self.id} is shutting down due to no jobs')
                self._logger.info(f'Runner {self.id} changed his status to {self.status.value}')
                sys.exit(0)

    def pre_process(self):
        """
            This method checks for unfinished jobs and returns their
            statuses to PENDING
        """
        # Check if there are jobs in Running status
        running_jobs = self._job_db.get_jobs(self.id, JobStatus.RUNNING.value)
        self._logger.info(f"Checking for unfinished jobs.")
        # if there are some jobs in Running state then
        # we need to change the status of these jobs to Pending
        if running_jobs:
            for running_job in running_jobs:
                running_job.status = JobStatus.PENDING
                self._logger.info(f"The status of job {running_job.id} was restored to PENDING.")
                self._job_db.save_job(running_job)
        else:
            self._logger.info(f"No unfinished jobs were found.")


class RunnerDB:
    def __init__(self, db_client, runner_db_logger):
        self.db_client = db_client
        self._logger = runner_db_logger

    def get_runner(self, id_, runner_db, job_db, s3, runner_logger):
        """
        Gets runner from DB and returns Runner instance

        """
        data = {
            'class': 'Runner',
            'id': id_,
            'attrs': {},
        }
        runners = self.db_client.send_request('list', json.dumps(data))[0][0]

        if runners is None:
            error = RunnerError(f'There is no runner in DB with id {id_}')
            self._logger.error(error)
            raise error
        else:
            runner = runners[0]
            return Runner(
                id_=runner['id'],
                status=runner['attrs']['status'],
                command=runner['attrs']['command'],
                type_=runner['attrs']['type'],
                task=runner['attrs']['task'],
                environment=runner['attrs']['environment'],
                runner_db=runner_db,
                job_db=job_db,
                s3=s3,
                runner_logger=runner_logger,
            )

    def save_runner(self, runner):
        """
        Updates runner in DB

        """
        data = {
            'class': 'Runner',
            'id': runner.id,
            'attrs': {
                'status': runner.status.value,
                'command': runner.command,
                'type': runner.type,
                'task': runner.task,
                'environment': runner.environment,
                'last_update': datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            },
        }
        self.db_client.send_request('update', json.dumps(data))
        self._logger.info(f'Runner {runner.id} saved in DB')

    def send_notification(self, runner):
        """
           Send a notification to the coordinator
        """

        data = {
            'class': 'Runner',
            'id': runner.id,
            'attrs': {
                'status': runner.status.value
            },
        }

        self.db_client.send_request('')


@click.command()
@click.option('--version', count=True)
@click.option('--runner-id', default='0', type=str)
@click.option('--db-client', default='POSTGRESQL', type=str)
@click.option('--verbose', count=True)
def main(version, runner_id, db_client, verbose):
    # if parameter version is specified then
    # the version number is supposed to be printed
    if version:
        print(f'Runner version {__version__}.')
        return

    # set the logging level based on the specified parameter --verbose
    if verbose:
        runner_logger = logger.get_logger('runner', logging.DEBUG, 'runner.log')
    else:
        runner_logger = logger.get_logger('runner', logging.INFO, 'runner.log')

    # create a connection to DB based on the credentials
    # provided by Resource class
    db_client = dbclient.get_client(db_client)
    db_client.set_credentials('DB', None)
    db_client.connect()

    # create an instance of RunnerDB class that is used
    # to work with Runner objects in DB
    runner_db = RunnerDB(db_client, runner_logger)
    # create an instance of JobDB class that is used
    # to work with Job objects in DB
    job_db = JobDB(db_client, runner_logger)
    # create an instance of S3 class that is used
    # to copy files to/from S3 bucket
    s3 = S3

    runner_logger.info(f'Runner v{__version__} started.')

    # reads Runner from DB by runner_id
    runner = runner_db.get_runner(runner_id, runner_db, job_db, s3, runner_logger)
    # start processing a job object by runner
    runner.run()


if __name__ == '__main__':
    main()
