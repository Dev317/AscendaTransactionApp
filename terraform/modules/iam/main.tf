terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# ----------------------------------------------
# General Users
# ----------------------------------------------
resource "aws_budgets_budget" "under_10_USD" {
  name         = "Under 10 USD"
  budget_type  = "COST"
  limit_amount = "10"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
}

resource "aws_iam_group" "developers" {
  name = "developers"
}
resource "aws_iam_group_membership" "team" {
  name = "developers"
  users = [aws_iam_user.bradley.name,
    aws_iam_user.marcus.name,
    aws_iam_user.minh.name,
    aws_iam_user.michelle.name,
    aws_iam_user.jennifer.name,
  aws_iam_user.elizabeth.name]

  group = aws_iam_group.developers.name
}

resource "aws_iam_user" "bradley" {
  name = "bradley"
}

resource "aws_iam_user" "marcus" {
  name = "marcus"
}

resource "aws_iam_user" "minh" {
  name = "minh"
}
resource "aws_iam_user" "michelle" {
  name = "michelle"
}
resource "aws_iam_user" "jennifer" {
  name = "jennifer"
}
resource "aws_iam_user" "elizabeth" {
  name = "elizabeth"
}

resource "aws_iam_policy" "policy" {
  name        = "developer-policy"
  description = "Policy for all developers in g1t1"
  policy      = data.aws_iam_policy_document.developer_policy.json
}

resource "aws_iam_group_policy_attachment" "for-developers" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.policy.arn
}

# ------------------------------------------
# File Upload IAM Stuff
# ------------------------------------------
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
  name   = "lambda-role-policy"
  role   = aws_iam_role.iam_lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

# Create AWS IAM Role for AWS Step Function
resource "aws_iam_role" "iam_stepfunction_role" {
  name = "iam-stepfunction-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "stepfunction_policy" {
  name = "stepfunction-role-policy"
  role = aws_iam_role.iam_stepfunction_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync"
        ],
        Resource = [
          "arn:aws:lambda:us-east-1:*",
          "arn:aws:lambda:ap-southeast-1:*"
        ]
      }
    ]
  })
}
