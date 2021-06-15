import argparse
import json
import subprocess
import time
from enum import Enum

from srv.dbclient.dbclient_factory import dbclient
from srv.job.job import Job, JobStatus


class Runner:
    """
    Gets jobs from DB and runs them
    """
    def __init__(self, _id, db_client):
        self.id = _id
        self._status = RunnerStatus.UP
        self.__jobs = []

        self.__db_client = dbclient.get_client(db_client)
        self.__db_client.set_credentials()
        self.__db_client.connect()
        self.status = self._status

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
        Sets runner status, also updates status in DB

        """
        if new_status not in RunnerStatus:
            raise ValueError(f'Runner status {new_status.value} is not allowed')

        self._status = new_status

        data = {
            'class': 'Runner',
            'id': self.id,
            'attrs': {
                'status': self._status.value,
            },
        }
        self.__db_client.send_request('update', json.dumps(data))

    @property
    def jobs(self):
        """
        Gets list of jobs

        :return:
        """
        return self.__jobs

    def get_new_jobs(self):
        """
        Gets new jobs from DB

        :return: None
        """
        data = {
            'class': 'Job',
            'attrs': {
                'status': JobStatus.NEW.value,
                'runner_id': self.id,
            },
        }
        new_jobs = self.__db_client.send_request('list', json.dumps(data))

        for job in new_jobs:
            self.__jobs.append(Job(
                _id=job['id'],
                command=job['command'],
                status=job['status'],
                runner_id=job['runner_id'],
                db_client=self.__db_client,  # TODO: remove from Job instance definition?
            ))

        for job in self.jobs:
            job.status = JobStatus.PENDING

    @classmethod
    def run_job(cls, job):
        """
        Runs job

        :return:
        """
        job.status = JobStatus.RUNNING
        job_result = subprocess.run(job.command.split())

        if job_result.returncode == 0:
            job.status = JobStatus.SUCCESS
        else:
            job.status = JobStatus.FAILED

        return job_result

    def run(self):
        """
        Gets jobs from DB and runs them

        """
        while True:
            self.get_new_jobs()

            if self.jobs:
                self.status = RunnerStatus.BUSY

                for job in self.jobs:
                    job_result = self.run_job(job)
                    job_stdout = job_result.stdout
                    job_stderr = job_result.stderr
                    job_returncode = job_result.returncode

                self.status = RunnerStatus.UP
            else:
                time.sleep(60)


class RunnerStatus(Enum):
    UP = 'up'
    BUSY = 'busy'
    DOWN = 'down'


def init_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runner-id')
    parser.add_argument('--db-client')
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()
    runner = Runner(args.runner_id, args.db_client)
    runner.run()


if __name__ == '__main__':
    main()
