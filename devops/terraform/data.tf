# data "aws_s3_bucket" "s3_bucket" {
#     bucket = "${var.STAGE}-reclada-bucket"
# }

data "template_file" "AWSLambdaBasicExecutionRole" {
  template = file("AWSLambdaBasicExecutionRole.json.tpl")
  vars = {
    presigned_url_stage = "${var.STAGE}"
  }
}

data "template_file" "S3-presigned-post-data" {
  template = file("S3-presigned-post-data.json.tpl")
  vars = {
    presigned_url_bucket = "${var.STAGE}"
  }
}

data "template_file" "AWSLambdaVPCAccessExecutionRole" {
  template = file("AWSLambdaVPCAccessExecutionRole.json.tpl")
  vars = {
    presigned_url_bucket_logs = "${var.STAGE}"
  }
}


data "aws_ami" "official_ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

data "aws_availability_zones" "azs" {
  state = "available"
}
