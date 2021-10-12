import os
import requests
from srv.coordinator.stage.stage import Stage
from domino import Domino



class DominoPlatform(Stage):
    def create_stage(self, type_of_stage):
        pass

    def is_stage_active(self, type_of_stage):
        pass

    def create_runner(self, ref_to_stage, runner_id, db_type, hw_tier=None):
        owner = os.getenv('DOMINO_PROJECT_OWNER')  # defines automatically
        project = os.getenv('DOMINO_PROJECT_TO_RUN')  # defines manually
        repo_path = os.getenv('RECLADA_REPO_PATH')  # defines manually
        command = [f'{repo_path}/run_runner.sh', repo_path, runner_id]
        self.api_key = os.getenv('DOMINO_USER_API_KEY')  # defines automatically
        self.base_url = os.getenv('DOMINO_URL') or 'https://try.dominodatalab.com/'  # defines manually

        domino = Domino("andreylr/Coordinator", api_key=None, host=self.base_url)

        domino_run = domino.runs_start(command, title=("Runner",))
        print(domino_run)

    def get_idle_runner(self, ref_to_stage):
        pass

    def get_job_status(self, job_id):
        pass


class RecladaDomino:
    def __init__(self, api_key=None, base_url='https://try.dominodatalab.com/v1/', session=None):
        self.session = session or requests.Session()

    def _request(self, path, method, params=None, json=None, stream=False, data=None):
        if not path.startswith('https://'):
            path = self.base_url + path

        try:
            headers = {
                'X-Domino-Api-Key': self.api_key,
            }

            print(f'Json before sending request {json} and data before sending {data} and params {params}')
            resp = self.session.request(
                method,
                path,
                params=params, json=json, data=data,
                headers=headers, stream=stream
            )
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            raise DominoException from e

    def run(self, user, project, command, title='from api', commit='', hw_tier=None, is_direct=False):
        data = {
            'command': command,
            'isDirect': is_direct,
            'title': 'Runner',
            'publishApiEndpoint': False,
        }

        # if the hardware tier is specified then we need to add it to the body of the request
        if hw_tier:
            data["tier"] = hw_tier

        if commit:
            data['commitId'] = commit
        print(f'Json data for starting runner {data}')
        return self._request(f'projects/{user}/{project}/runs', 'POST', json=data).json()


class DominoException(Exception):
    pass
