#kms-reclada lambda function 

##Description

kms-reclada function provides functionality of encrypting and decrypting text messages. It uses AWS KMS services for working with master and data keys.

In order to encrypt a text message the following payload needs to be formed:
```
{
  'type' - the type of actions [encrypt]
  'data' - the text message for which the encryption needs to be executed
  'masterKey' - the name of the master key
  'aws_access_key' - user's AWS key
  'aws_access_secret_key' - user's AWS secret key
}
```
In order to decrypt a text message
```
{
  'type' - the type of actions [decrypt]
  'data' - the encypted text message which needs to be decrypted
  'masterKey' - the name of the master key
  'aws_access_key' - user's AWS key
  'aws_access_secret_key' - user's AWS secret key
}
```

Encryption and Decryption operations have to be executed for the same master key. AWS access key and AWS access secret key can be specified in three ways:
- In pyaload. AWS access keys specified in environment would be ignored.
- In environment variables AWS_ACCESS_KEY_RECLADA and AWS_SECRET_KEY_RECLADA. If there are no secrets keys in payload then these variables would be used. 
- 