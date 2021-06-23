##### **RUN Coordinator**
To run coordinator:

python -m srv.coordinator.coordinator -platform <platform> -database <database> -messenger <messenger>

Currently there are two platforms supported:
- DUMMY 
- DOMINO

For database and messenger parameters there is only one option now:
- POSTGRESQL