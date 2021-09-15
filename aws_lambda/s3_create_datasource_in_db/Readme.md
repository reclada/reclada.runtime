# s3_create_datasource_in_db AWS Lambda function 

## Description

_s3_create_datasource_in_db_ AWS Lambda function triggers by S3 put event and creates ab object off class File (subclass of DataSource) in DB.


## Installation

- Upload the source code of the function. The source code is zipped in _s3_create_datasource_in_db.zip_ file and can be found in _installation_ folder.
- Add environment variables (_PG_HOST, PG_DATABASE, PG_USER, PG_PASSWORD_) in Lambda settings.
