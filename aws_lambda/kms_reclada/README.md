#kms-reclada lambda function 

##Description

kms-reclada function provides functionality of encrypting and decrypting text messages. It uses AWS KMS services for working with master and data keys.

In order to encrypt a text message the following payload needs to be formed:
```
{
  'type': - the type of actions [encrypt]
  'data': - the text message for which the encryption needs to be executed
  'masterKey': - the name of the master key
  'aws_access_key': - user's AWS key
  'aws_access_secret_key': - user's AWS secret key
}
```
In order to decrypt a text message
```
{
  'type': - the type of actions [decrypt]
  'data': - the encypted text message which needs to be decrypted
  'masterKey': - the name of the master key
  'aws_access_key': - user's AWS key
  'aws_access_secret_key': - user's AWS secret key
}
```

Encryption and Decryption operations have to be executed for the same master key. AWS access key and AWS access secret key can be specified in three ways:
- In pyaload. AWS access keys specified in environment would be ignored.
- In environment variables AWS_ACCESS_KEY_RECLADA and AWS_SECRET_KEY_RECLADA. If there are no secrets keys in payload then these variables would be used. 
- In default environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. These variables would be used if there are no other variables provided.

##Installation

The installation process for kms-reclada lambda function consists of several steps:
- Prepare a layer with packages on which the function depended on. This layer needs to include _**cryptography**_ python package. This layer has been created and put in installation folder in file _**kms-lambda-layer.zip**_. In AWS after creating the fuction this layer needs to be added.
- Upload the source code for the function. The function and kms module is zipped in lambda-kms.zip file and can be found in _**installation**_ folder.
- Attach the needed permissions to the function. In order for the function to work properly the following permission needs to be set: AWSKeyManagementServicePowerUser and an additional permission that can be set inline. The text of the permission is present below:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:GenerateDataKey",
                "kms:DescribeKey",
                "kms:Decrypt",
                "kms:Encrypt"
            ],
            "Resource": "*"
        }
    ]
}
```
- Set environment variables AWS_ACCESS_KEY_RECLADA and AWS_SECRET_KEY_RECLADA that is going to use if there are no security variables specified in payload.

        