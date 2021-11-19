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

        response = domino.run(
                        owner, project, command, hw_tier=hw_tier, is_direct=False,
                        title=f'{project}:{runner_id}',
                        )
        # This method returns the platform runner id
        return response["runId"]

    def get_idle_runner(self, ref_to_stage):
        pass

    def get_job_status(self, job_id):
        # create domino object for communicating with Domino API
        domino = Domino()
        # gets parameters from environments variable
        owner = os.getenv('DOMINO_PROJECT_OWNER')  # defines automatically
        project = os.getenv('DOMINO_PROJECT_TO_RUN')  # defines manually
        # get the status of the specified job
        return domino.get_job_status(owner, project, job_id)


class Domino:
    def __init__(self, api_key=None, base_url='https://try.dominodatalab.com/v1/', session=None):
        self.api_key = api_key or os.getenv('DOMINO_USER_API_KEY')  # defines automatically
        self.base_url = os.getenv('DOMINO_URL') or base_url  # defines manually
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

    def get_job_status(self, user, project, job_id):
        # get the status or exit code of the specified job
        response = self._request(f'projects/{user}/{project}/runs/{job_id}',"GET").json()
        # check response. If isCompleted is true then we need to return 1
        # otherwise the method should return 0
        if response["isCompleted"] == True:
            return 1
        return 0

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
