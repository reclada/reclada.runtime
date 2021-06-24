import os

from pykube import HTTPClient, KubeConfig, Job

from srv.coordinator.stage.stage import Stage


class K8sPlatform(Stage):
    def create_stage(self, type_of_stage):
        pass

    def is_stage_active(self, type_of_stage):
        pass

    def create_runner(self, ref_to_stage, runner_id, db_type):
        image = 'badgerdoc-runner'
        k8s = K8s(image)
        command = f'python3 -m apps.reclada_reclada_runtime.srv.runner.runner.py ' \
                  f'--runner-id={runner_id} --db-client={db_type}'
        k8s.run(command, f'{image}: {runner_id}')

    def get_idle_runner(self, ref_to_stage):
        pass

    def get_job_status(self, job_id):
        pass


class K8s:
    def __init__(self, image):
        self.image = image
        self._api = HTTPClient(KubeConfig.from_service_account())

    @property
    def image_repo(self):
        return os.getenv('K8S_IMAGE_REPO')

    def run(self, command, job_id):
        job_json = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': self.image,
                'labels': {
                    'job_id': job_id,
                },
            },
            'spec': {
                'backoffLimit': 5,
                'template': {
                    'metadata': {
                        'name': self.image,
                    },
                    'spec': {
                        'containers': [{
                            'name': self.image,
                            'image': self.image_repo,
                            'command': command,
                        }],
                    },
                },
            },
        }

        Job(self._api, job_json).create()
