#!/bin/sh

host=$1
port=$2
database=$3
user=$4

if [ -z $host ]; then
	echo "usage: install-rds.sh <host> [<port>] [<database>] [<user>]"
	exit 1
fi;

if [ -z $port ]; then
	port=5432
fi;

if [ -z $database ]; then
    database="reclada";
fi;
if [ -z $user ]; then
    user=$database;
fi;

cd objects
echo 'Installing objects'
psql --host=$host --port=$port --dbname=$database --username=$user -f install_objects.sql