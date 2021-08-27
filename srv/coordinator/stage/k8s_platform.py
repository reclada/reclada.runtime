import os

from pykube import HTTPClient, KubeConfig, Job

from srv.coordinator.stage.stage import Stage

K8S_ENV_KEYS = [
    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET_NAME',
    'S3_REGION', 'S3_DEFAULT_REGION', 'DB_URI', 'CUSTOM_TASK', 'CLIENT_USER',
    'CLIENT_URL', 'CUSTOM_REPO_PATH', 'CLIENT_PASSWORD', 'PYTHONPATH', 'RECLADA_REPO_PATH',
]


class K8sPlatform(Stage):
    def create_stage(self, type_of_stage):
        pass

    def is_stage_active(self, type_of_stage):
        pass

    def create_runner(self, ref_to_stage, runner_id, db_type):
        image = 'badgerdoc'
        k8s = K8s(image)
        command = f'python3 -m srv.runner.runner --runner-id={runner_id} --db-client={db_type}'
        k8s.run(command, f'{image}-{runner_id}')

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

    @staticmethod
    def k8s_envs():
        return [
            {'name': k, 'value': os.getenv(k)}
            for k in K8S_ENV_KEYS
            if k in os.environ
        ]

    def run(self, command, job_id):
        job = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'generateName': f'{self.image}-',
                'labels': {
                    'job_id': job_id,
                },
            },
            'spec': {
                'backoffLimit': 0,
                'ttlSecondsAfterFinished': 100,
                'template': {
                    'spec': {
                        'serviceAccountName': os.getenv('K8S_SERVICE_ACCOUNT_NAME'),
                        'restartPolicy': 'Never',
                        'volumes': [
                            {
                                'name': os.getenv('PV_NAME'),
                                'persistentVolumeClaim': {
                                    'claimName': os.getenv('PVC_NAME')
                                }
                            }
                        ],
                        'containers': [{
                            'name': self.image,
                            'image': self.image_repo,
                            'imagePullPolicy': 'Always',
                            'command': command.split(),
                            'volumeMounts':[{
                                'name': os.getenv('PV_NAME'),
                                'mountPath': '/data'
                            }, ],
                            'env': self.k8s_envs(),
                            'resources': {
                                'limits': {
                                    'memory': '4Gi',
                                    'cpu': '2000m',
                                },
                                'requests': {
                                    'memory': '1Gi',
                                    'cpu': '500m',
                                },
                            },
                        }],
                        
                    },
                },
            },
        }

        Job(self._api, job).create()
