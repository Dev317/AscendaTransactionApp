terraform {
  # Declares providers, so that Terraform can install and use them
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.28"
    }

    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.2.0"
    }
  }

  # Where Terraform stores its state to keep track of resources it manages
  backend "s3" {
    bucket = "<unique_bucket_name>"
    key    = "terraform.tfstate"
    region = "ap-southeast-1"
  }
}

# Create an archive file for the Python lambda package
# data "archive_file" "python_lambda_package" {
#   type        = "zip"
#   source_file = "/code/handler.py"
#   output_path = "/build/handler.zip"
# }

# Configure AWS Provider
provider "aws" {
  region = "ap-southeast-1"
}

# resource "aws_iam_group" "developers" {
#   name = "developers"
# }
# resource "aws_iam_group_membership" "team" {
#   name = "developers"
#   users = [aws_iam_user.bradley.name,
#     aws_iam_user.marcus.name,
#     aws_iam_user.minh_vu.name,
#     aws_iam_user.michelle.name,
#     aws_iam_user.jennifer.name,
#   aws_iam_user.elizabeth.name]

#   group = aws_iam_group.developers.name
# }

# resource "aws_iam_user" "bradley" {
#   name = "bradley"
# }

# resource "aws_iam_user" "marcus" {
#   name = "marcus"
# }

# resource "aws_iam_user" "minh_vu" {
#   name = "minh_vu"
# }
# resource "aws_iam_user" "michelle" {
#   name = "michelle"
# }
# resource "aws_iam_user" "jennifer" {
#   name = "jennifer"
# }
# resource "aws_iam_user" "elizabeth" {
#   name = "elizabeth"
# }

# resource "aws_iam_policy" "policy" {
#   name        = "developer-policy"
#   description = "Policy for all developers in g1t1"
#   policy      = jsonencode(
#     {
#       "Version" : "2012-10-17",
#       "Statement" : [
#         {
#           "Sid" : "VisualEditor0",
#           "Effect" : "Allow",
#           "Action" : [
#             "rds:*",
#             "cloudtrail:*",
#             "dynamodb:*",
#             "sqs:*",
#             "rolesanywhere:*",
#             "cloudfront:*",
#             "access-analyzer:*",
#             "kms:*",
#             "kinesis:*",
#             "events:*",
#             "sns:*",
#             "states:*",
#             "rds-db:*",
#             "cognito-identity:*",
#             "dax:*",
#             "s3:*",
#             "apigateway:*",
#             "rds-data:*",
#             "amplifybackend:*",
#             "appsync:*",
#             "sts:*",
#             "iam:*",
#             "cloudwatch:*",
#             "sso:*",
#             "lambda:*",
#             "route53:*",
#             "cognito-idp:*"
#           ],
#           "Resource" : "*"
#         }
#       ]
#     }
#   )
# }

# resource "aws_iam_group_policy_attachment" "for-developers" {
#   group      = aws_iam_group.developers.name
#   policy_arn = aws_iam_policy.policy.arn
# }


# Create AWS IAM Role for Lambda Function
resource "aws_iam_role" "iam_lambda_role" {
  name = "iam-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-role-policy"
  role = aws_iam_role.iam_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          # S3 policies
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:HeadObject",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          # add DynamoDB policies
          "dynamodb:BatchGetItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ],
        Resource = "*"
      }
    ]
  })
}

# Create S3 Bucket to store different versions of the code
resource "aws_s3_bucket" "lambda_function_bucket" {
  bucket        = "<unique_bucket_name>"
  force_destroy = true
}

# Create S3 Bucket that accepts files
resource "aws_s3_bucket" "file_upload_bucket" {
  bucket        = "<unique_bucket_name>"
  force_destroy = true
}

# Create DynamoDB to store records
resource "aws_dynamodb_table" "transactions_records_table" {
  name           = "transaction-records-table"
  billing_mode   = "PROVISIONED"
  read_capacity  = "30"
  write_capacity = "30"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    enabled        = true
    attribute_name = "expiryPeriod"
  }
  point_in_time_recovery { enabled = true }
  server_side_encryption { enabled = true }
  lifecycle { ignore_changes = [write_capacity, read_capacity] }
}

# Create AWS Lambda Function

resource "aws_lambda_function" "file_upload" {
  function_name    = "test-file-upload"
  role             = aws_iam_role.iam_lambda_role.arn
  filename         = "build/handler.zip"                   #data.archive_file.python_lambda_package.output_path
  source_code_hash = filebase64sha256("build/handler.zip") #data.archive_file.python_lambda_package.output_base64sha256
  runtime          = "python3.9"
  memory_size      = 128
  publish          = true
  handler          = "handler.handler"


  lifecycle {
    ignore_changes = [
      source_code_hash,
      environment
    ]
  }
}

resource "aws_lambda_alias" "file_upload_alias" {
  name             = "production"
  function_name    = aws_lambda_function.file_upload.arn
  function_version = "$LATEST"

  lifecycle {
    ignore_changes = [
      function_version
    ]
  }
}

# Create S3 bucket upload trigger for lambda function

resource "aws_s3_bucket_notification" "file_upload_trigger" {
  bucket = aws_s3_bucket.file_upload_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.file_upload.arn
    events              = ["s3:ObjectCreated:*"]
    #filter_prefix       = "foldername"
    #filter_suffix       = ".csv"
  }

  depends_on = [aws_lambda_permission.s3_permission_to_trigger_lambda]
}

resource "aws_lambda_permission" "s3_permission_to_trigger_lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.file_upload.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.file_upload_bucket.arn
}

