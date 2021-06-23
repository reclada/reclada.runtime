from abc import ABC, abstractmethod


class MBClient(ABC):

    @abstractmethod
    def handle_request(self, body):
        """
            This method handles requests that comes from a message broker
        :param body: parameter that was extracted from the message
        :return:
        """
        pass

    @abstractmethod
    def run(self):
        """
            This method starts the poling loop to get notifications from a message broker
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