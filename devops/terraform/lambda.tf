data "terraform_remote_state" "vpc" {
    backend = "s3" 
    workspace = "default"
    config = {
        bucket     = "reclada-tf"
        key        = "reclada.tfstate"
        region     = "eu-west-1"   
    }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "s3_create_datasource_in_db_role_${var.STAGE}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
inline_policy {
    name = "AWSLambdaS3ExecutionRole-_${var.STAGE}"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::*"
        }
    ]
}
  )
}

inline_policy {
    name = "lambda_stream_logs__${var.STAGE}"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:eu-west-1:588200329560:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:eu-west-1:588200329560:log-group:/aws/lambda/s3_create_datasource_in_db_${var.STAGE}:*"
            ]
        }
    ]
}
  )
}


inline_policy {
    name = "VPC_policy_${var.STAGE}"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
          {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeNetworkInterfaces",
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeInstances",
                "ec2:AttachNetworkInterface"
            ],
            "Resource": "*"
          }
      ]
    }
  )
}
}

  resource "aws_lambda_function" "s3_create_datasource_in_db" {

    function_name = "s3_create_datasource_in_db_${var.STAGE}"
    description   = "Creates an object of class file when the file appears in S3"
    handler       = "s3_create_datasource_in_db.lambda_handler"
    runtime       = "python3.8"

    # create_package         = false
    filename = "./s3_create_datasource_in_db.zip"
    role = aws_iam_role.iam_for_lambda.arn
    # ignore_source_code_hash = true

    vpc_config {
      subnet_ids         = data.terraform_remote_state.vpc.outputs.rds_subnets
      security_group_ids = [data.terraform_remote_state.vpc.outputs.default_security_group]
    }

    environment {
      variables = {
        PG_DATABASE = var.pgdatabase,
        PG_HOST     = var.pghost,
        PG_PASSWORD = var.pgpassword,
        PG_USER     = var.pguser
      }
    }


    tags = var.shared_tags
}

  module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "s3_get_presigned_url_${var.STAGE}"
  description   = "Generates a presigned url for upload to S3 or download from S3 file"
  handler       = "s3_get_presigned_url.lambda_handler"
  runtime       = "python3.8"

  create_package         = false
  local_existing_package = "./s3_get_presigned_url.zip"
  ignore_source_code_hash = true

  vpc_subnet_ids         = data.terraform_remote_state.vpc.outputs.rds_subnets
  vpc_security_group_ids = [data.terraform_remote_state.vpc.outputs.default_security_group]
  attach_network_policy  = true
    
  attach_policy_jsons = true
  number_of_policy_jsons = 3
  policy_jsons = [
    data.template_file.AWSLambdaBasicExecutionRole.rendered,
    data.template_file.S3-presigned-post-data.rendered,
    data.template_file.AWSLambdaVPCAccessExecutionRole.rendered
  ]

  environment_variables = {
    DEFAULT_S3_BUCKET = "${var.STAGE}-reclada-bucket"
  }

  tags = var.shared_tags
}