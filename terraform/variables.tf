variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "lambda_role" {
  description = "Name of IAM lambda role"
  type        = string
  default     = "iam-lambda-role"
}

variable "force_destroy" {
  description = "Force deleting a resource"
  type        = bool
  default     = true
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = [
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
    ]
    resources = ["arn:aws:s3:::*", "arn:aws:dynamodb:::*", "arn:aws:logs:::*"]
    effect    = "Allow"
  }
}

data "iam_policy_document" "developer_policy" {
  statement {
    actions = ["rds:*",
      "cloudtrail:*",
      "dynamodb:*",
      "sqs:*",
      "rolesanywhere:*",
      "cloudfront:*",
      "access-analyzer:*",
      "kms:*",
      "kinesis:*",
      "events:*",
      "sns:*",
      "states:*",
      "rds-db:*",
      "cognito-identity:*",
      "dax:*",
      "s3:*",
      "apigateway:*",
      "rds-data:*",
      "amplifybackend:*",
      "appsync:*",
      "sts:*",
      "iam:*",
      "cloudwatch:*",
      "sso:*",
      "lambda:*",
      "route53:*",
    "cognito-idp:*"]
    resources = "*"
    effect    = "Allow"
  }
}