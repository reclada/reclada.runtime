##### **RUN Coordinator**
To run coordinator:

_python3 -m srv.coordinator.coordinator -platform `<platform>` -database `<database>` -messenger `<messenger>`_

This command needs to be run in the reclada_runtime project folder

Currently coordinator supports the following platforms:
- DUMMY to run runners in plain linux environment
- DOMINO to run runners in Domino environment
- KS8 to run runners in Kubernetes environment

Database and Messenger clients use DB for storing data and getting notifications. There is only one available
client now:
- POSTGRESQL

All credentials for connecting to DB are taken from the environment variable DB_URI

The parameter with channel name for messenger needs to be specified 
in the environment variable POSTGRES_NOTIFY_CHANNEL.