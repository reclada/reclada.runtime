import base64
import os

from cryptography.fernet import Fernet
import boto3


class KMS :
    """
        This class is supposed to serve as KMS for Reclada Project. It allows working
        with encrypted data with the help of KMS AWS
    """

    def __init__(self, master_key_name):
        """
           Initializer of KMS class stores the name of the master key and creates
           a client to work with AWS
        """
        self.master_key_name = master_key_name
        self._kms_client = boto3.client("kms")

    def get_master_key(self):
        """
           The function requests the master keys from AWS and chooses the master key which
           name is the name of the master key saved during initialization of the class
        """
        response = self._kms_client.list_keys()

        # check all found master key for name matching
        for cmk in response["Keys"]:
            key_info = self._kms_client.describe_key(KeyId=cmk["KeyArn"])
            # if master key is found then return it
            if key_info["KeyMetadata"]["Description"] == self.master_key_name:
                self._cmk_id = cmk["KeyId"]
                self.create_data_key()
                return cmk["KeyId"], cmk["KeyArn"]

        # If no master key is found then create it
        response = self.create_master_key()
        self.create_data_key()
        return response

    def create_master_key(self):
        """
           This function creates a new master key
        """
        response = self._kms_client.create_key(Description=self.master_key_name)

        self._cmk_id = response["KeyMetadata"]["KeyId"]
        # return the key ID and ARN
        return response["KeyMetadata"]["KeyId"], response["KeyMetadata"]["Arn"]

    def create_data_key(self, key_spec="AES_256"):
        """
           This function creates data key for the specified master key and saves it in the class
        """
        response = self._kms_client.generate_data_key(KeyId=self._cmk_id, KeySpec=key_spec)

        # saving data key to the class
        self._data_encrypted = response["CiphertextBlob"]
        self._data_plain = base64.b64encode(response["Plaintext"])
        # return data key
        return response["CiphertextBlob"], base64.b64encode(response["Plaintext"])

    def encrypt_data(self, data):
        """
           This functions encrypts the data and returns its encrypted version
        """
        # check if the encrypted part of the key is present
        if not self._data_encrypted :
            return
        # encrypt the data
        f = Fernet(self._data_plain)
        encrypted_data = f.encrypt(data)
        # return the encrypted data
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        """
           This function decrypt the data and return its original version
        """

        # checks if there is plaint text part of the key is present
        if not self._data_plain:
            return

        # decrypt the data
        f = Fernet(self._data_plain)
        plain_data = f.decrypt(encrypted_data)

        return plain_data


if __name__ == "__main__":
    kms = KMS("dev1_environment")
    kms.get_master_key()

    encrypt_hello = kms.encrypt_data(bytes("Hello World!"))
    print (f'Encrypted version:"{encrypt_hello}"')
    decrypt_hello = kms.decrypt_data(encrypt_hello)
    print(f'Plaint Text:"{decrypt_hello}"')