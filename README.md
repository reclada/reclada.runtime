## Kubernetes deployment and launch

TBD

## Domino deployment and launch
### Coordinator and badgerdoc runner deployment in Domino:

1. Create a new environment using Dockerfile.domino.

2. Create a single project for the coordinator and badgerdoc runner.

3. In project settings select a newly created environment.

4. In project files connect [reclada runtime repository](https://github.com/reclada/reclada.runtime).

5. In project files connect [SciNLP repository](https://github.com/reclada/SciNLP).

6. In project files connect [badgerdoc repository](https://github.com/badgerdoc/badgerdoc).

7. In project settings fill environment variables according to table:

| Variable | Description |
| :------------- | :------------- |
| AWS_ACCESS_KEY_ID | AWS credential |
| AWS_SECRET_ACCESS_KEY | AWS credential |
| AWS_DEFAULT_REGION | AWS credential |
| AWS_REGION_NAME | AWS credential |
| AWS_S3_BUCKET_NAME | S3 bucket name where to place results e.g. reclada-bucket. Files will be placed to `s3://reclada-bucket/output/<job_id>/` |
| DB_URI | Connection string in format `postgresql://user:password@host:port/database` |
| DOMINO_PROJECT_TO_RUN | The name of current Domino project |
| DOMINO_URL | Domino API URL e.g. `https://try.dominodatalab.com/v1/` |
| POSTGRES_NOTIFY_CHANNEL | Notification channel name (`job_created`) |
| RECLADA_REPO_PATH | Path where reclada runtime repo is mounted e.g. `/repos/reclada_reclada_runtime` |
| SCINLP_REPO_PATH | Path where reclada SciNLP repo is mounted plus directory to SciNLP executable file e.g. `/repos/reclada_SciNLP/src/srv/lite` |
| BD2RECLADA_REPO_PATH | Path where reclada SciNLP repo is mounted plus directory to bd2reclada executable file e.g. `/repos/reclada_SciNLP/src/srv/bd2reclada` |
| BADGERDOC_REPO_PATH | Path where badgerdoc repo is mounted e.g. `/repos/badgerdoc_badgerdoc` |

8. In project settings in `Results` tab select `To isolated branches` option.

9. In the project create a launcher to create runners in DB. For the command to run use:
```bash
<reclada_runtime_repo_mount_path>/srv/runner/create_runners.py --type=DOMINO --number=5
```
Number parameter is optional (default 5).

10. In the project create a launcher for the coordinator. For the command to run use:
```bash
<reclada_runtime_repo_mount_path>/run_coordinator.sh <reclada_runtime_repo_mount_path>
```

11. In the project create a launcher to manually assign jobs to the runner. For the command to run use:
```bash
<reclada_runtime_repo_mount_path>/srv/runner/assign_jobs_to_runner.py --type=DOMINO --runner-id=<runner_id>
```
12. In the project create a launcher to manually launch badgerdoc runner. For the command to run use:
```bash
<reclada_runtime_repo_mount_path>/run_runner.sh <reclada_runtime_repo_mount_path> <runner_id>
```

### Coordinator launch:

1. Run the launcher created in item 8 of deployment. It will create 5 runners in DB with status down. In normal conditions, it should be run once.

2. Run the launcher created in item 9 of deployment. It will launch the coordinator.

3. If there are problems running coordinator: run the launcher created in item 10 of deployment. It will change all jobs with status new to status pending and assign them to the specified runner id. It won't run coordinator but allows to run runner manually.

### Badgerdoc runner launch:

1. In normal conditions, it’s not necessary to launch badgerdoc runner manually. But if you want to, run the launcher created in item 11 of deployment.
