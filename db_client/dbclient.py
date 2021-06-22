from abc import ABC, abstractmethod


class DBClient(ABC):

    @abstractmethod
    def send_request(self, function_name, body):
        """
            This method send selects to DB to call a store procedure
        :param function_name: a name of a store procedure to call
        :param body: json object with needed parameters
        :return: json object with results
        """
        pass

    @abstractmethod
    def connect(self):
        """
            This method connects to the DB
        :return:
        """
        pass

    @abstractmethod
    def set_credentials(self, *args, **kwargs):
        """
            This method saves credentials for a message broker
        :return:
        """
        pass