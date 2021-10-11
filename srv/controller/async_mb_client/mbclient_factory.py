from srv.mb_client.pg_mbclient import PgMBClient


class MBClientFactory:
    """
        This class creates a client for the given type of Message Broker
    """
    def __init__(self):
        self._clients = {}

    def client_register(self, client_type, client):
        """
            This method registers the given type of the MB client
        :param client_type: type of the Message Broker
        :param client: the client
        """
        self._clients[client_type] = client

    def get_client(self, client_type):
        """
            This method returns the client by the given type
        :param client_type: type of the client
        :return: the client
        """
        stage = self._clients.get(client_type)
        if not stage:
            raise ValueError(client_type)
        return stage()

mbclient = MBClientFactory()
mbclient.client_register('POSTGRESQL', PgMBClient)
