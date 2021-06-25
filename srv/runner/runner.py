import argparse
import json
import subprocess
import time
from enum import Enum

from srv.db_client.dbclient_factory import dbclient
from srv.job.job import JobStatus, JobDB
from srv.s3.s3 import S3


class Runner:
    """
    Gets jobs from DB and runs them
    """
    def __init__(self, _id, status, command, _type, task, environment, runner_db, job_db, s3):
        self.id = _id
        self._status = status
        self.command = command
        self.type = _type
        self.task = task
        self.environment = environment
        self.__runner_db = runner_db
        self.__job_db = job_db
        self.__s3 = s3

        self.__jobs = []

    def __repr__(self):
        return f'Runner id={self.id} with status={self.status} having {len(self.jobs)} jobs'

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
            raise ValueError(f'Runner status {new_status.value} is not allowed')

        self._status = new_status

    @property
    def jobs(self):
        """
        Gets list of jobs

        """
        return self.__jobs

    def get_new_jobs(self):
        """
        Gets new jobs from DB

        """
        self.__jobs = self.__job_db.get_runner_jobs(self.id)

    def run_job(self, job):
        """
        Runs job

        """
        # Updates job status in DB to "running"
        job.status = JobStatus.RUNNING
        self.__job_db.save_job(job)

        # TODO: resolve all input parameters
        s3_uri = job.input_parameters[0]['uri']
        command = job.command.split()
        job_result = subprocess.run(command + [s3_uri, job.id], cwd='/app')

        # Updates job status in DB depending on the job return code
        if job_result.returncode == 0:
            job.status = JobStatus.SUCCESS
        else:
            job.status = JobStatus.FAILED
        self.__job_db.save_job(job)

        return job_result

    def run(self):
        """
        Gets jobs from DB and runs them

        """
        while True:
            try:
                self.get_new_jobs()

                if self.jobs:
                    # Updates runner status in DB to "busy" before running jobs
                    # TODO: change schema for runner adding status busy
                    # self.status = RunnerStatus.BUSY
                    # self.__runner_db.save_runner(self)

                    for job in self.jobs:
                        job_result = self.run_job(job)
                        job_stdout = job_result.stdout
                        job_stderr = job_result.stderr
                        job_returncode = job_result.returncode

                    # Updates runner status in DB to "up" when all jobs finished
                    # TODO: uncomment after runner schema change
                    # self.status = RunnerStatus.UP
                    # self.__runner_db.save_runner(self)
                else:
                    time.sleep(10)
            except Exception:
                time.sleep(10)


class RunnerStatus(Enum):
    UP = 'up'
    BUSY = 'busy'
    DOWN = 'down'


class RunnerError(Exception):
    pass


class RunnerDB:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_runner(self, _id, runner_db, job_db, s3):
        """
        Gets runner from DB and returns Runner instance

        """
        data = {
            'class': 'Runner',
            'id': _id,
            'attrs': {},
        }
        runners = self.db_client.send_request('list', json.dumps(data))[0][0]

        if runners is None:
            raise RunnerError(f'There is no runner with id {id}')
        else:
            runner = runners[0]
            return Runner(
                _id=runner['id'],
                status=runner['attrs']['status'],
                command=runner['attrs']['command'],
                _type=runner['attrs']['type'],
                task=runner['attrs']['task'],
                environment=runner['attrs']['environment'],
                runner_db=runner_db,
                job_db=job_db,
                s3=s3,
            )

    def save_runner(self, runner):
        """
        Updates runner in DB (only updates status now)

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
            },
        }
        self.db_client.send_request('update', json.dumps(data))


def init_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runner-id')
    parser.add_argument('--db-client')
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    db_client = dbclient.get_client(args.db_client)
    db_client.set_credentials('DB', None)

    db_client.connect()

    runner_db = RunnerDB(db_client)
    job_db = JobDB(db_client)
    s3 = S3

    runner = runner_db.get_runner(args.runner_id, runner_db, job_db, s3)
    runner.run()


if __name__ == '__main__':
    main()
