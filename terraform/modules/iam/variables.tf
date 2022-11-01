data "aws_iam_policy_document" "developer_policy" {
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
      "cognito-idp:*",
      "aws-portal:*",
    "billingconductor:*"]
    resources = ["*"]
    effect    = "Allow"
  }
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
      "dynamodb:UpdateItem",
      # AWS Step Function policy
      "states:StartExecution",
      # AWS SQS policy
      "sqs:SendMessage",
      "sqs:ReceiveMessage"
    ]

    // arn:aws:dynamodb:ap-southeast-1:717942231127:table/campaign_service_table
    resources = ["arn:aws:states:*:*:*",
      "arn:aws:s3:::*",
      "arn:aws:logs:*:*:*",
      "arn:aws:dynamodb:*:*:*",
    "arn:aws:sqs:*:*:*"]
    effect = "Allow"
  }
}
