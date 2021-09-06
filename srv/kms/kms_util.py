from kms import KMS

import click
from _version import __version__


@click.command()
@click.option('--version', count=True)
@click.option('--encrypt', count=True)
@click.option('--data', type=str)
@click.option('--decrypt', count=True)
@click.option('--key', type=str)
def main(version, encrypt, data, decrypt, key):

    # if version option is specified then
    # print version number and quit the app
    if version:
        print(f"Coordinator version {__version__}")
        return

    # if operation type is encrypt and decrypt at the same time
    if encrypt and decrypt:
        print(f"Operation type is not clear.")
        return
    # check if the master key is specified
    if not key:
        print(f"The master key needs to be specified.")

    # if we need to encrypt data
    if encrypt:
        kms = KMS(key)
        response = kms.encrypt_data(data)
        print(f'{response}')
        return

    # if we need to decrypt data
    if decrypt:
        kms = KMS(key)
        response = kms.decrypt_data(data)
        print(f'{response}')


if __name__ == "__main__":
    main()
