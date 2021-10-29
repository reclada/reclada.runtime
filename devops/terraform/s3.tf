resource "aws_iam_user" "bucket_editor" {
  name = "${var.env}-reclada-bucket-editor"
  tags = var.shared_tags
}

resource "aws_iam_policy" "bucket_policy" {
  name = "${var.STAGE}-reclada-bucket-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetBucketLocation",
          "s3:ListAllMyBuckets"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : ["s3:ListBucket"],
        "Resource" : ["arn:aws:s3:::${var.STAGE }"]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ],
        "Resource" : ["arn:aws:s3:::${var.STAGE }/*"]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "bucket_policy_attachment" {
  user       = aws_iam_user.bucket_editor.name
  policy_arn = aws_iam_policy.bucket_policy.arn
}

resource "aws_s3_bucket" "bucket" {
  bucket  = "${var.STAGE}-reclada-bucket"
  acl     = "public-read"
  force_destroy = true
  versioning {
            enabled = true
        }
  tags    = var.shared_tags

  cors_rule {
    allowed_methods = ["PUT", "POST", "GET", "DELETE", "HEAD"]
    allowed_origins = ["https://${var.STAGE}.reclada.com", "https://${var.STAGE}.reclada.com"]
    allowed_headers = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
    }
                        
  }

resource "aws_s3_bucket_policy" "AllowPublicRead" {
  bucket = "${aws_s3_bucket.bucket.id}"
  policy = jsonencode({
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "AllowPublicRead",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${var.STAGE}-reclada-bucket/*"
        }
                ]       
    }
  )
}

resource "aws_s3_bucket_object" "inbox_folder" {
    bucket  = "${var.STAGE}-reclada-bucket"
    acl     = "public-read"
    key     =  "inbox/"
    content_type = "application/x-directory"
}

resource "aws_s3_bucket_object" "output_folder" {
    bucket  = "${var.STAGE}-reclada-bucket"
    acl     = "public-read"
    key     =  "output/"
    content_type = "application/x-directory"
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_create_datasource_in_db.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = "${aws_s3_bucket.bucket.id}"

  lambda_function {
    lambda_function_arn = "${aws_lambda_function.s3_create_datasource_in_db.arn}"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "inbox/"
  }

}