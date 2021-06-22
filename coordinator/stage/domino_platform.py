import os

import requests

from stage import Stage


class DominoPlatform(Stage):
    def create_stage(self, type_of_stage):
        pass

    def is_stage_active(self, type_of_stage):
        pass

    def create_runner(self, ref_to_stage, runner_id, db_type):
        domino = Domino()
        owner = os.getenv('DOMINO_PROJECT_OWNER')
        project = 'badgerdoc-runner'
        command = f'python3 /repos/reclada_reclada_runtime/srv/runner/runner.py ' \
                  f'--runner-id={runner_id} --db-client={db_type}'

        domino.run(
            owner, project, command, is_direct=True,
            title=f'{project}:{runner_id}',
        )

    def get_idle_runner(self, ref_to_stage):
        pass

    def get_job_status(self, job_id):
        pass


class Domino:
    def __init__(self, api_key=None, base_url='https://try.dominodatalab.com/v1/', session=None):
        self.api_key = api_key or os.getenv('DOMINO_USER_API_KEY')
        self.base_url = base_url or os.getenv('DOMINO_URL')
        self.session = session or requests.Session()

    def _request(self, path, method, params=None, json=None, stream=False, data=None):
        if not path.startswith('https://'):
            path = self.base_url + path

        try:
            headers = {
                'X-Domino-Api-Key': self.api_key,
            }
            resp = self.session.request(
                method,
                path,
                params=params, json=json, data=data,
                headers=headers, stream=stream,
            )
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            raise DominoException from e

    def run(self, user, project, command, title='from api', commit='', is_direct=False):
        data = {
            'isDirect': is_direct,
            'command': command,
            'title': title,
        }
        if commit:
            data['commitId'] = commit
        return self._request(f'projects/{user}/{project}/runs', 'POST', json=data).json()


class DominoException(Exception):
    pass
