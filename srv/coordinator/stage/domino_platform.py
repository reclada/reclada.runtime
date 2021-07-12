import os
import requests
from srv.coordinator.stage.stage import Stage


class DominoPlatform(Stage):
    def create_stage(self, type_of_stage):
        pass

    def is_stage_active(self, type_of_stage):
        pass

    def create_runner(self, ref_to_stage, runner_id, db_type, hw_tier=None):
        domino = Domino()
        owner = os.getenv('DOMINO_PROJECT_OWNER')  # defines automatically
        project = os.getenv('DOMINO_PROJECT_TO_RUN')  # defines manually
        repo_path = os.getenv('RECLADA_REPO_PATH')  # defines manually
        command = [f'{repo_path}/run_runner.sh', repo_path, runner_id]

        domino.run(
            owner, project, command, hw_tier=hw_tier, is_direct=False,
            title=f'{project}:{runner_id}',
        )

    def get_idle_runner(self, ref_to_stage):
        pass

    def get_job_status(self, job_id):
        pass


class Domino:
    def __init__(self, api_key=None, base_url='https://try.dominodatalab.com/v1/', session=None):
        self.api_key = api_key or os.getenv('DOMINO_USER_API_KEY')  # defines automatically
        self.base_url = base_url or os.getenv('DOMINO_URL')  # defines manually
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

    def run(self, user, project, command, title='from api', commit='', hw_tier=None, is_direct=False):
        data = {
            'isDirect': is_direct,
            'command': command,
            'title': title,
        }

        # if the hardware tier is specified then we need to add it to the body of the request
        if hw_tier:
            data["tier"] = hw_tier

        if commit:
            data['commitId'] = commit
        return self._request(f'projects/{user}/{project}/runs', 'POST', json=data).json()


class DominoException(Exception):
    pass
