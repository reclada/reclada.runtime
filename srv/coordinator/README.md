##### **RUN Coordinator**
To run coordinator:
```bash
python3 -m srv.coordinator.coordinator -platform <platform> -database <database> -messenger <messenger> -verbose
```
This command needs to be run in the reclada_runtime project folder

_platform_ parameter defines platform on which coordinator runs.

Currently coordinator supports the following platforms:
- DUMMY to run runners in plain linux environment
- DOMINO to run runners in Domino environment
- K8S to run runners in Kubernetes environment

_database_ parameter specifies the database client.
Currently coordinator supports only PostgreSQL database.
- POSTGRESQL

_messenger_ parameter specifies the message broker client.
Currently coordinator uses PostgreSQL notification mechanism to exchange messages
- POSTGRESQL

_verbose_ optional parameter specifies the type of logging. If this parameter is specified then all debugging information would be logged.

All credentials for connecting to DB are taken from the environment variable DB_URI

The parameter with channel name for messenger needs to be specified in the environment variable POSTGRES_NOTIFY_CHANNEL. The default name for the channel that is supposed to notify about arriving new jobs is _job_created_.

For manual launch in Domino use:

```bash
<path_to_mounted_repo>/run_coordinator.sh <path_to_mounted_repo> 
```
Example:
```bash
/mnt/reclada_runtime/run_coordinator.sh /mnt/reclada_runtime
```
