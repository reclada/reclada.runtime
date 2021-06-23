##### **RUN Coordinator**
To run coordinator:

_python3 -m srv.coordinator.coordinator -platform <platform> -database <database> -messenger <messenger>_

This command needs to be run in the reclada_runtime project folder

Currently there are two platforms supported:
- DUMMY 
- DOMINO

For database and messenger parameters there is only one database client available now:
- POSTGRESQL

All credential for connecting to DB are taken from the environment variable DB_URI