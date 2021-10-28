terraform {
  backend "s3" {
    bucket     = "reclada-tf"
    key        = "reclada.tfstate"
    encrypt    = true
    kms_key_id = "arn:aws:kms:eu-west-1:588200329560:alias/aws/s3"
    region     = "eu-west-1"
  }
}
