##### **RUN Runner**
To run runner manually:

_python3 -m srv.runner.runner --runner-id <runner_id> --db-client <database client>_

This command needs to be run in the reclada_runtime project folder

<runner_id> - parameter that defines runner and which is supposed to be the same with runner id of the runner 
              recldada object in DB. Coordinator uses this runner id to attach jobs to a specific runner. The runner
              uses this id to select all jobs assigned to it. 

Currently there is only one database client is supported:
- POSTGRESQL 

The credentials for connecting to DB is taken from the environment variable DB_URI