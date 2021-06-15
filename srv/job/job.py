import json
from enum import Enum


class Job:
    def __init__(self, _id, command, status, runner_id, db_client):
        self.id = _id
        self.command = command
        self._status = status
        self.runner_id = runner_id

        self.__db_client = db_client  # TODO: remove from Job instance definition?

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
        Sets job status, also updates status in DB

        """
        if new_status not in JobStatus:
            raise ValueError(f'Job status {new_status.value} is not allowed')

        self._status = new_status

        data = {
            'class': 'Job',
            'id': self.id,
            'attrs': {
                'status': self._status.value,
            },
        }
        self.__db_client.send_request('update', json.dumps(data))


class JobStatus(Enum):
    NEW = 'new'
    PENDING = 'pending'
    RUNNING = 'running'
    FAILED = 'failed'
    SUCCESS = 'success'
