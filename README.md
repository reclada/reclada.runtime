## Kubernetes deployment and launch

TBD

## Domino deployment and launch
### Coordinator and badgerdoc runner deployment in Domino:

1. Create a new environment using Dockerfile.domino.

2. Create a single project for the coordinator and badgerdoc runner.

3. In project settings select a newly created environment.

4. In project files connect [reclada runtime repository](https://github.com/reclada/reclada.runtime).

5. In project files connect [artifactory repository](https://github.com/reclada/artifactory).

6. In project files connect [deployments repository](https://github.com/reclada/deployments).

7. In project files connect [SciNLP repository](https://github.com/reclada/SciNLP).

8. In project files connect [badgerdoc repository](https://github.com/badgerdoc/badgerdoc).

9. In project files connect custom repository (if needed).

10. In project settings fill environment variables according to table:

| Variable | Description |
| :------------- | :------------- |
| AWS_ACCESS_KEY_ID | AWS credential |
| AWS_SECRET_ACCESS_KEY | AWS credential |
| AWS_DEFAULT_REGION | AWS credential |
| AWS_REGION_NAME | AWS credential |
| AWS_S3_BUCKET_NAME | S3 bucket name where to place results e.g. reclada-bucket. Files will be placed to `s3://reclada-bucket/output/<job_id>/` |
| BADGERDOC_REPO_PATH | Path where badgerdoc repo is mounted e.g. `/repos/badgerdoc_badgerdoc` |
| CUSTOM_REPO_PATH | Path where custom repo is mounted e.g. `/repos/custom` (if needed) |
| CUSTOM_TASK | Path where custom task is located e.g. `/repos/custom/custom_task.sh` (if needed) |
| DB_URI | Connection string in format `postgresql://user:password@host:port/database` |
| DOMINO_PROJECT_TO_RUN | The name of current Domino project |
| DOMINO_URL | Domino API URL e.g. `https://try.dominodatalab.com/v1/` |
| ENVIRONMENT_NAME | Environment where the project is supposed to be run e.g. `DOMINO` |
| LAMBDA_NAME | name of AWS Lambda function for generating presigned URLs e.g. `s3_get_presigned_url` |
| POSTGRES_NOTIFY_CHANNEL | Notification channel name e.g. `job_created` |
| RECLADA_REPO_PATH | Path where reclada runtime repo is mounted e.g. `/repos/reclada_reclada_runtime` |
| SCINLP_REPO_PATH | Path where reclada SciNLP repo is mounted plus directory to SciNLP executable file e.g. `/repos/reclada_SciNLP/src/srv/lite` |

11. In project settings in `Results` tab select `To isolated branches` option.

12. In the project create a launcher for DB deploy. For the command to run use:
```bash
<deployments_repo_mount_path>/db/install.sh
```

13. In the project create a launcher for the coordinator. For the command to run use:
```bash
<reclada_runtime_repo_mount_path>/run_coordinator.sh <reclada_runtime_repo_mount_path>
```

### DB deploy:

1. Run the launcher created in item 12 of the deployment section. It will deploy the database.

### Coordinator launch:

1. Run the launcher created in item 13 of the deployment section. It will launch the coordinator.
