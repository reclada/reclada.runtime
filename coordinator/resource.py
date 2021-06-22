import json as js
import pathlib as pl
import os


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
        if self._type == "DB":
            if self._resource:
                    self.__setattr__("host", self._resource["host"])
                    self.__setattr__("user", self._resource["user"])
                    self.__setattr__("database", self._resource["database"])
                    self.__setattr__("password", self._resource["password"])
                    return self
            else:
                self.__setattr__("host", os.getenv("POSTGRES-HOST", "localhost"))
                self.__setattr__("database", os.getenv("POSTGRES-DB", "database"))
                self.__setattr__("user", os.getenv("POSTGRES-USER", "user"))
                self.__setattr__("password", os.getenv("POSTGRES-PASSWORD"))
                return self
        elif self._type == "MB":
            if self._resource:
                self.__setattr__("host", self._resource["host"])
                self.__setattr__("user", self._resource["user"])
                self.__setattr__("database", self._resource["database"])
                self.__setattr__("password", self._resource["password"])
                self.__setattr__("channel", self._resource["channel"])
                return self
            else:
                self.__setattr__("host", os.getenv("POSTGRES-HOST", "localhost"))
                self.__setattr__("database", os.getenv("POSTGRES-DB", "database"))
                self.__setattr__("user", os.getenv("POSTGRES-USER", "user"))
                self.__setattr__("password", os.getenv("POSTGRES-PASSWORD"))
                self.__setattr__("channel", os.getenv("POSTGRES-NOTIFY-CHANNEL"))
                return self


