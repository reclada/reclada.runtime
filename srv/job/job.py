import json
from enum import Enum


class JobError(Exception):
    pass


class JobStatus(Enum):
    NEW = 'new'
    PENDING = 'pending'
    RUNNING = 'running'
    FAILED = 'failed'
    SUCCESS = 'success'


class Job:
    def __init__(self, id_, type_, task, command, input_parameters, status, runner_id, job_logger):
        self.id = id_
        self.type = type_
        self.task = task
        self.command = command
        self.input_parameters = input_parameters
        self._status = status
        self.runner_id = runner_id
        self._logger = job_logger

    def __repr__(self):
        return f'Job id={self.id} with status={self.status} is appointed to runner id={self.runner_id}'

    @property
    def status(self):
        """
        Gets job status

        """
        return self._status

    @status.setter
    def status(self, new_status):
        """
        Sets job status

        """
        if new_status not in JobStatus:
            error = ValueError(f'Job status {new_status.value} is not allowed')
            self._logger.error(error)
            raise error

        self._status = new_status


class JobDB:
    def __init__(self, db_client, job_db_logger):
        self.db_client = db_client
        self._logger = job_db_logger

    def get_job(self, _id):
        """
        Gets job from DB and returns Job instance

        """
        data = {
            'class': 'Job',
            'GUID': _id,
            'attributes': {},
        }
        job = self.db_client.send_request('list', json.dumps(data))

        return Job(
            id_=job['GUID'],
            type_=job['type'],
            task=job['task'],
            command=job['command'],
            input_parameters=job['inputParameters'],
            status=job['status'],
            runner_id=job['runner'],
            job_logger=self._logger,
        )

    def get_jobs(self, runner_id, status):
        """
        Gets new jobs from DB that are assigned to runner and returns list of Job instances

        """

        data = {
            'class': 'Job',
            'attributes': {
                'runner': runner_id,
                'status': status
            },
        }
        jobs = self.db_client.send_request('list', json.dumps(data))[0][0]

        if jobs is None:
            return []
        else:
            return [Job(
                id_=job['GUID'],
                type_=job['attributes']['type'],
                task=job['attributes']['task'],
                command=job['attributes']['command'],
                input_parameters=job['attributes']['inputParameters'],
                status=JobStatus.NEW,
                runner_id=job['attributes']['runner'],
                job_logger=self._logger,
            ) for job in jobs if job.get('attributes').get('inputParameters')]  # TODO: proper inputParameters check

    def save_job(self, job):
        """
        Updates job in DB (only updates status now, but needed to specify all required attributes)

        """
        data = {
            'class': 'Job',
            'GUID': job.id,
            'attributes': {
                'type': job.type,
                'task': job.task,
                'command': job.command,
                'inputParameters': job.input_parameters,
                'status': job.status.value,
                'runner': job.runner_id,
            },
        }
        self.db_client.send_request('update', json.dumps(data))
