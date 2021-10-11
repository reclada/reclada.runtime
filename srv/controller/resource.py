import json as js
import pathlib as pl
import os
from urllib.parse import urlparse


class Resource():

    def __init__(self):
        self._type = None
        self._json_file = None

    def get(self, resource_type, json_file):
        """
            This method returns Resource object with attributes for all types of connection
        :return: Resource object
        """
        self._type = resource_type
        self._json_file = json_file
        self._resource = None

        # check existence of the json file and load data from it
        if self._json_file and pl.Path(self._json_file).is_file():
            with open(self._json_file, 'r') as f:
                self._resource = js.load(f)

        # based on the resource type create credentials for
        # different type of connections

        self.__setattr__("host", "host")
        self.__setattr__("user", "user")
        self.__setattr__("database", "database")
        self.__setattr__("password", "password")

        if self._type == "DB":
            self.set_for_db()
            return self
        elif self._type == "MB":
            self.set_for_mb()

        return self

    def set_for_db(self):
        if self._resource:
            self.set_from_resource()
        else:
            self.set_from_uri()

    def set_from_uri(self):
        database_url = os.getenv("DB_URI", None)
        if database_url:
            creds = urlparse(database_url)
            self.__setattr__("host", creds.hostname)
            self.__setattr__("database", creds.path[1:])
            self.__setattr__("user", creds.username)
            self.__setattr__("password", creds.password)

    def set_from_resource(self):
        if self._resource:
            self.__setattr__("host", self._resource["host"])
            self.__setattr__("user", self._resource["user"])
            self.__setattr__("database", self._resource["database"])
            self.__setattr__("password", self._resource["password"])

    def set_for_mb(self):
        if self._resource:
            self.set_from_resource()
            self.__setattr__("channel", self._resource["channel"])
        else:
            self.set_from_uri()
            self.__setattr__("channel", os.getenv("POSTGRES_NOTIFY_CHANNEL"))
