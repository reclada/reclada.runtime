import os

import pykube
from pykube import HTTPClient, KubeConfig, Job

from srv.coordinator.stage.stage import Stage

K8S_ENV_KEYS = [
    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET_NAME',
    'S3_REGION', 'S3_DEFAULT_REGION', 'DB_URI', 'CUSTOM_TASK', 'CLIENT_USER',
    'CLIENT_URL', 'CUSTOM_REPO_PATH', 'CLIENT_PASSWORD', 'PYTHONPATH', 'RECLADA_REPO_PATH',
    'PREPROCESS_COMMAND', 'POSTPROCESS_COMMAND',
]


class K8sPlatform(Stage):
    def __init__(self):
        self._k8s = None

    def create_stage(self, type_of_stage):
        pass

    def is_stage_active(self, type_of_stage):
        pass

    def create_runner(self, ref_to_stage, runner_id, db_type):
        image = 'badgerdoc'
        self._k8s = K8s(image)

        command = f'python3 -m srv.runner.runner --runner-id={runner_id} --db-client={db_type}'
        labels = {
            'image': image,
            'runner-id': runner_id,
            'db-client': db_type,
        }

        return self._k8s.run(command, labels)

    def get_idle_runner(self, ref_to_stage):
        pass

    def get_job_status(self, job_id):
        """
            This method check for existence of the specified job on the platform and
            if the job is not active then it returns 1 otherwise it returns 0
        """
        api = HTTPClient(KubeConfig.from_service_account())
        # extract namespace and name from job_id
        # this job_id is supposed to be created in K8S environment
        namespace, name = job_id.split(":")
        # find job by namespace and name
        job = pykube.Job.objects(api).filter(namespace=namespace).get(name=name)
        # Check the status of the job. If the job is still running then
        # we consider it as a normal processing and return 0. If the job is finished
        # by whatever reason we need to return 1. For us it doesn't matter the reason since
        # we only check if this job is alive or not.
        job_status  = job.obj["status"]
        job_active = job_status.get("active", None)
        if not job_active :
            # if the job is not active then returns 1
            return 1
        return 0


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

    def run(self, command, labels):
        job = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'generateName': f'{self.image}-',
                'labels': labels,
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
                            },
                            {
                                'name': os.getenv('PV2_NAME'),
                                'persistentVolumeClaim': {
                                    'claimName': os.getenv('PVC2_NAME')
                                }
                            }
                        ],
                        'containers': [{
                            'name': self.image,
                            'image': self.image_repo,
                            'imagePullPolicy': 'Always',
                            'command': command.split(),
                            'volumeMounts': [{
                                'name': os.getenv('PV_NAME'),
                                'mountPath': '/repos'
                            },
                            {
                                'name': os.getenv('PV2_NAME'),
                                'mountPath': '/mnt'
                            },],
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

        job_k8s = Job(self._api, job)
        job_k8s.create()
        return f'{job_k8s.obj["metadata"]["namespace"]}:{job_k8s.obj["metadata"]["name"]}'

