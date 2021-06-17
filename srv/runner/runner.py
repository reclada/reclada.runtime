import argparse
import json
import subprocess
import time
from enum import Enum

from srv.dbclient.dbclient_factory import dbclient
from srv.job.job import JobStatus, JobDB


class Runner:
    """
    Gets jobs from DB and runs them
    """
    def __init__(self, _id, status, runner_db, job_db):
        self.id = _id
        self._status = status
        self.__runner_db = runner_db
        self.__job_db = job_db
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

        # Updates statuses of all jobs in DB to "pending"
        for job in self.__jobs:
            job.status = JobStatus.PENDING
            self.__job_db.save_job(job)

    def run_job(self, job):
        """
        Runs job

        """
        # Updates job status in DB to "running"
        job.status = JobStatus.RUNNING
        self.__job_db.save_job(job)

        job_result = subprocess.run(job.command.split())

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
            self.get_new_jobs()

            if self.jobs:
                # Updates runner status in DB to "busy" before running jobs
                self.status = RunnerStatus.BUSY
                self.__runner_db.save_runner(self)

                for job in self.jobs:
                    job_result = self.run_job(job)
                    job_stdout = job_result.stdout
                    job_stderr = job_result.stderr
                    job_returncode = job_result.returncode

                # Updates runner status in DB to "up" when all jobs finished
                self.status = RunnerStatus.UP
                self.__runner_db.save_runner(self)
            else:
                time.sleep(60)


class RunnerStatus(Enum):
    UP = 'up'
    BUSY = 'busy'
    DOWN = 'down'


class RunnerDB:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_runner(self, _id, runner_db, job_db):
        """
        Gets runner from DB and returns Runner instance

        """
        data = {
            'class': 'Runner',
            'id': _id,
            'attrs': {},
        }
        runner = self.db_client.send_request('list', json.dumps(data))

        return Runner(
            _id=runner['id'],
            status=runner['status'],
            runner_db=runner_db,
            job_db=job_db,
        )

    def save_runner(self, runner):
        """
        Updates runner in DB (only updates status now)

        """
        data = {
            'class': 'Job',
            'id': runner.id,
            'attrs': {
                'status': runner.status.value,
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
    db_client.set_credentials()
    db_client.connect()

    runner_db = RunnerDB(db_client)
    job_db = JobDB(db_client)

    runner = runner_db.get_runner(args.runner_id, runner_db, job_db)
    runner.run()


if __name__ == '__main__':
    main()
