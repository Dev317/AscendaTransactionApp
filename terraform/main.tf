# Configure AWS Provider
provider "aws" {
  region = var.aws_region
}
# Route 53
resource "aws_route53_record" "waffle" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "itsag1t1.com"
  type    = "CNAME"
  alias {
    name                   = "itsag1t1.com"
    zone_id                = "Z3AQBSTGFYJSTF"
    evaluate_target_health = false
  }
}

resource "aws_route53_zone" "primary" {
  name = "itsag1t1.com"
}

resource "aws_amplify_branch" "master" {
  app_id      = aws_amplify_app.Waftech.id
  branch_name = "master"
  # Enable SNS notifications.
  enable_notification = true
}

resource "aws_amplify_domain_association" "g1t1" {
  app_id      = aws_amplify_app.Waftech.id
  domain_name = "itsag1t1.com"

  # https://example.com
  sub_domain {
    branch_name = aws_amplify_branch.master.branch_name
    prefix      = ""
  }

  # https://www.example.com
  sub_domain {
    branch_name = aws_amplify_branch.master.branch_name
    prefix      = "www"
  }
}

resource "aws_cognito_user_pool_domain" "itsag1t1" {
  domain       = "g1t1userdomain"
  user_pool_id = aws_cognito_user_pool.fe_userpool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name = "client"

  user_pool_id = aws_cognito_user_pool.fe_userpool.id
}

resource "aws_cognito_user_pool" "fe_userpool" {
  name = "fe_userpool"

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }

    recovery_mechanism {
      name     = "verified_phone_number"
      priority = 2
    }
  }
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["amplify.amazonaws.com"]
    }
  }
}

# resource "aws_amplify_branch" "fe" {
#   app_id      = aws_amplify_app.Waftech.id
#   branch_name = "fe"
# }

# resource "aws_amplify_domain_association" "g1t1" {
#   app_id      = aws_amplify_app.Waftech.id
#   domain_name = "itsag1t1.com"

#   sub_domain {
#     branch_name = aws_amplify_branch.fe.branch_name
#     prefix      = ""
#   }

#   # https://www.example.com
#   sub_domain {
#     branch_name = aws_amplify_branch.fe.branch_name
#     prefix      = "www"
#   }
# }

resource "aws_iam_role" "amplify-github" {
  name                = "AmplifyGithub"
  assume_role_policy  = join("", data.aws_iam_policy_document.assume_role.*.json)
  managed_policy_arns = ["arn:aws:iam::aws:policy/AWSCodeCommitReadOnly"]
}

resource "aws_amplify_app" "Waftech" {
  name                        = "Waftech"
  description                 = "frontend for Waftech"
  repository                  = "https://github.com/cs301-itsa/project-2022-23t1-g1-t1-waffles"
  access_token                = var.github_token
  iam_service_role_arn        = aws_iam_role.amplify-github.arn
  enable_auto_branch_creation = true
  enable_branch_auto_build    = true

  build_spec = <<-EOT
    version: 0.1
    frontend:
      phases:
        preBuild:
          commands:
            - npm install
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: build
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
  EOT

  custom_rule {
    source = "/<*>"
    status = "404"
    target = "/index.html"
  }

  environment_variables = {
    ENV = "test"
  }
}

# resource "aws_budgets_budget" "under_10_USD" {
#   name         = "Under 10 USD"
#   budget_type  = "COST"
#   limit_amount = "10"
#   limit_unit   = "USD"
#   time_unit    = "MONTHLY"
# }

# Create an archive file for the Python lambda package
# data "archive_file" "python_lambda_package" {
#   type        = "zip"
#   source_file = "/code/handler.py"
#   output_path = "/build/handler.zip"
# }

# resource "aws_iam_group" "developers" {
#   name = "developers"
# }
# resource "aws_iam_group_membership" "team" {
#   name = "developers"
#   users = [aws_iam_user.bradley.name,
#     aws_iam_user.marcus.name,
#     aws_iam_user.minh.name,
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

# resource "aws_iam_user" "minh" {
#   name = "minh"
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
#   policy      = data.aws_iam_policy_document.developer_policy.json
# }

# resource "aws_iam_group_policy_attachment" "for-developers" {
#   group      = aws_iam_group.developers.name
#   policy_arn = aws_iam_policy.policy.arn
# }

# ------------------------------------------------------
# File Upload Resources
# ------------------------------------------------------

# # Create AWS IAM Role for Lambda Function
# resource "aws_iam_role" "iam_lambda_role" {
#   name = var.lambda_role

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Sid    = ""
#       Principal = {
#         Service = "lambda.amazonaws.com"
#       }
#     }]
#   })
# }

# resource "aws_iam_role_policy" "lambda_policy" {
#   name   = "lambda-role-policy"
#   role   = aws_iam_role.iam_lambda_role.id
#   policy = data.aws_iam_policy_document.lambda_policy.json
# }

# # Create S3 Bucket to store different versions of the code
# resource "aws_s3_bucket" "lambda_function_bucket" {
#   bucket        = "lambda-archive-g1t1"
#   force_destroy = var.force_destroy
# }

# # Create S3 Bucket that accepts files
# resource "aws_s3_bucket" "file_upload_bucket" {
#   bucket        = "file-upload-g1t1"
#   force_destroy = var.force_destroy
# }

# # Create DynamoDB to store records
# resource "aws_dynamodb_table" "transactions_records_table" {
#   name           = "transaction-records-table"
#   billing_mode   = "PROVISIONED"
#   read_capacity  = "30"
#   write_capacity = "30"
#   hash_key       = "id"

#   attribute {
#     name = "id"
#     type = "S"
#   }

#   ttl {
#     enabled        = true
#     attribute_name = "expiryPeriod"
#   }
#   point_in_time_recovery { enabled = true }
#   server_side_encryption { enabled = true }
#   lifecycle { ignore_changes = [write_capacity, read_capacity] }
# }

# # Create AWS Lambda Function for File Upload

# resource "aws_lambda_function" "file_upload" {
#   function_name    = "file-upload"
#   role             = aws_iam_role.iam_lambda_role.arn
#   filename         = "../build/csv_processor.zip"                   #data.archive_file.python_lambda_package.output_path
#   source_code_hash = filebase64sha256("../build/csv_processor.zip") #data.archive_file.python_lambda_package.output_base64sha256
#   runtime          = "python3.9"
#   memory_size      = 512
#   publish          = true
#   handler          = "csv_processor.handler"
#   timeout          = 180

#   environment {
#     variables = {
#       DB_TABLE_NAME = aws_dynamodb_table.transactions_records_table.name
#       CHUNK_SIZE    = 100000
#     }
#   }

#   lifecycle {
#     ignore_changes = [
#       source_code_hash
#     ]
#   }
# }

# resource "aws_lambda_alias" "file_upload_alias" {
#   name             = "production"
#   function_name    = aws_lambda_function.file_upload.arn
#   function_version = "$LATEST"

#   lifecycle {
#     ignore_changes = [
#       function_version
#     ]
#   }
# }

# # Create Lambda function to trigger execution of Step Function

# resource "aws_lambda_function" "stepfunction_trigger" {
#   function_name    = "stepfunction-trigger"
#   role             = aws_iam_role.iam_lambda_role.arn
#   filename         = "../build/stepfunction_trigger.zip"
#   source_code_hash = filebase64sha256("../build/stepfunction_trigger.zip")
#   runtime          = "python3.9"
#   memory_size      = 512
#   publish          = true
#   handler          = "stepfunction_trigger.handler"
#   timeout          = 5

#   environment {
#     variables = {
#       STATE_MACHINE_ARN = aws_sfn_state_machine.stepfunction_file_processor.arn
#     }
#   }


#   lifecycle {
#     ignore_changes = [
#       source_code_hash,
#       environment
#     ]
#   }
# }

# resource "aws_lambda_alias" "stepfunction_trigger_alias" {
#   name             = "production"
#   function_name    = aws_lambda_function.stepfunction_trigger.arn
#   function_version = "$LATEST"

#   lifecycle {
#     ignore_changes = [
#       function_version
#     ]
#   }
# }

# # Create S3 bucket upload trigger for lambda function

# resource "aws_s3_bucket_notification" "file_upload_trigger" {
#   bucket = aws_s3_bucket.file_upload_bucket.id

#   lambda_function {
#     lambda_function_arn = aws_lambda_function.stepfunction_trigger.arn
#     events              = ["s3:ObjectCreated:*"]
#     #filter_prefix       = "foldername"
#     filter_suffix = ".csv"
#   }

#   depends_on = [aws_lambda_permission.s3_permission_to_trigger_lambda]
# }

# resource "aws_lambda_permission" "s3_permission_to_trigger_lambda" {
#   statement_id  = "AllowExecutionFromS3Bucket"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.stepfunction_trigger.arn
#   principal     = "s3.amazonaws.com"
#   source_arn    = aws_s3_bucket.file_upload_bucket.arn
# }

# # Create AWS Step Function

# resource "aws_sfn_state_machine" "stepfunction_file_processor" {
#   name     = "stepfunction_file_processor"
#   role_arn = aws_iam_role.iam_stepfunction_role.arn

#   definition = jsonencode({
#     "Comment" : "Orchestrates processing of CSV file.",
#     "StartAt" : "Import",
#     "States" : {
#       "Import" : {
#         "Type" : "Task",
#         "Resource" : "${aws_lambda_function.file_upload.arn}",
#         "Next" : "CheckResults"
#       },
#       "CheckResults" : {
#         "Type" : "Choice",
#         "Choices" : [{
#           "And" : [
#             {
#               "Variable" : "$.handler.results.finished",
#               "BooleanEquals" : false
#             }
#           ],
#           "Next" : "Import" },
#           {
#             "And" : [
#               {
#                 "Variable" : "$.handler.results.finished",
#                 "BooleanEquals" : true
#               }
#             ],
#         "Next" : "SuccessState" }],
#         "Default" : "FailState"
#       },
#       "SuccessState" : {
#         "Type" : "Succeed"
#       },
#       "FailState" : {
#         "Type" : "Fail",
#         "Cause" : "$.handler.results.errors"
#       }
#     }
#   })

#   depends_on = [
#     aws_lambda_function.file_upload
#   ]

# }

# Create AWS IAM Role for AWS Step Function

# resource "aws_iam_role" "iam_stepfunction_role" {
#   name = "iam-stepfunction-role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Sid    = ""
#       Principal = {
#         Service = "states.amazonaws.com"
#       }
#     }]
#   })
# }

# resource "aws_iam_role_policy" "stepfunction_policy" {
#   name = "stepfunction-role-policy"
#   role = aws_iam_role.iam_stepfunction_role.id

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow",
#         Action = [
#           "lambda:InvokeFunction",
#           "lambda:InvokeAsync"
#         ],
#         Resource = "${aws_lambda_function.file_upload.arn}"
#       }
#     ]
#   })
# }
