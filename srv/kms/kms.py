import base64

from cryptography.fernet import Fernet
import boto3


class KMS :
    """
        This class is supposed to serve as KMS for Reclada Project. It allows working
        with encrypted data with the help of KMS AWS
    """

    def __init__(self, master_key_name, aws_access_key, aws_secret_key):
        """
           Initializer of KMS class stores the name of the master key and creates
           a client to work with AWS
        """
        self.master_key_name = master_key_name
        self._kms_client = boto3.client("kms", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        self._get_master_key()

    def _get_master_key(self):
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
                self._create_data_key()
                return cmk["KeyId"], cmk["KeyArn"]

        # If no master key is found then create it
        response = self._create_master_key()
        self._create_data_key()
        return response

    def _create_master_key(self):
        """
           This function creates a new master key
        """
        response = self._kms_client.create_key(Description=self.master_key_name)

        self._cmk_id = response["KeyMetadata"]["KeyId"]
        # return the key ID and ARN
        return response["KeyMetadata"]["KeyId"], response["KeyMetadata"]["Arn"]

    def _create_data_key(self, key_spec="AES_256"):
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

        # if the input data is str then we need to conver to bytes
        if type(data) is str:
            data = bytes(data, "utf-8")

        # encrypt the data
        f = Fernet(self._data_plain)
        encrypted_data = f.encrypt(data)
        # now we need to include the encrypted part of the key to the encrypted data
        # calculating the length of the encrypted data key
        len_encrypted_key = f'{len(str(base64.b64encode(self._data_encrypted), "utf-8")):04}'

        # saving the encrypted data key to the encypted data
        encrypted_data = len_encrypted_key + \
                         str(base64.b64encode(self._data_encrypted), "utf-8") + \
                         str(encrypted_data,"utf-8")
        # return the encrypted data
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        """
           This function decrypt the data and return its original version
        """

        # checks if there is plaint text part of the key is present
        if not self._data_plain:
            return

        # extracting the encrypted data key from the encrypted data
        len_encrypted_key = int(encrypted_data[:4]) + 4
        data_key_encrypted = encrypted_data[4:len_encrypted_key]
        data_key_encrypted = bytes(data_key_encrypted, "utf-8")
        data_key_encrypted = base64.b64decode(data_key_encrypted)
        response = self._kms_client.decrypt(CiphertextBlob=data_key_encrypted)
        data_plain_key = base64.b64encode((response["Plaintext"]))

        # decrypt the data
        f = Fernet(data_plain_key)
        plain_data = f.decrypt(bytes(encrypted_data[len_encrypted_key:], "utf-8"))
        return str(plain_data, "utf-8")



