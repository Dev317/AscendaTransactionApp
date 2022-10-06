terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# ------------------------------------------------------
# File Upload Resources
# ------------------------------------------------------
# Create an archive file for the Python lambda package
# data "archive_file" "python_lambda_package" {
#   type        = "zip"
#   source_file = "code/handler.py"
#   output_path = "build/handler.zip"
# }

# Create S3 Bucket that accepts files
resource "aws_s3_bucket" "file_upload_bucket" {
  bucket        = var.file_upload_s3_bucket
  force_destroy = var.force_destroy
}

# Create DynamoDB to store records -- TO DELETE
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

# Create AWS Lambda Function for File Upload

resource "aws_lambda_function" "file_upload" {
  function_name    = "file-upload"
  role             = var.lambda_role
  filename         = var.csv_processor_zip                   #data.archive_file.python_lambda_package.output_path
  source_code_hash = filebase64sha256(var.csv_processor_zip) #data.archive_file.python_lambda_package.output_base64sha256
  runtime          = "python3.9"
  memory_size      = 512
  publish          = true
  handler          = "csv_processor.handler"
  timeout          = 180

  environment {
    variables = {
      DB_TABLE_NAME = aws_dynamodb_table.transactions_records_table.name
      CHUNK_SIZE    = 100000
    }
  }

  lifecycle {
    ignore_changes = [
      source_code_hash
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

# Create Lambda function to trigger execution of Step Function

resource "aws_lambda_function" "stepfunction_trigger" {
  function_name    = "stepfunction-trigger"
  role             = var.lambda_role
  filename         = var.stepfunction_trigger_zip
  source_code_hash = filebase64sha256(var.stepfunction_trigger_zip)
  runtime          = "python3.9"
  memory_size      = 512
  publish          = true
  handler          = "stepfunction_trigger.handler"
  timeout          = 5

  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.stepfunction_file_processor.arn
    }
  }


  lifecycle {
    ignore_changes = [
      source_code_hash,
      environment
    ]
  }
}

resource "aws_lambda_alias" "stepfunction_trigger_alias" {
  name             = "production"
  function_name    = aws_lambda_function.stepfunction_trigger.arn
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
    lambda_function_arn = aws_lambda_function.stepfunction_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    #filter_prefix       = "foldername"
    filter_suffix = ".csv"
  }

  depends_on = [aws_lambda_permission.s3_permission_to_trigger_lambda]
}

resource "aws_lambda_permission" "s3_permission_to_trigger_lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stepfunction_trigger.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.file_upload_bucket.arn
}

# Create AWS Step Function

resource "aws_sfn_state_machine" "stepfunction_file_processor" {
  name     = "stepfunction_file_processor"
  role_arn = var.stepfunction_trigger_role

  definition = jsonencode({
    "Comment" : "Orchestrates processing of CSV file.",
    "StartAt" : "Import",
    "States" : {
      "Import" : {
        "Type" : "Task",
        "Resource" : "${aws_lambda_function.file_upload.arn}",
        "Next" : "CheckResults"
      },
      "CheckResults" : {
        "Type" : "Choice",
        "Choices" : [{
          "And" : [
            {
              "Variable" : "$.handler.results.finished",
              "BooleanEquals" : false
            }
          ],
          "Next" : "Import" },
          {
            "And" : [
              {
                "Variable" : "$.handler.results.finished",
                "BooleanEquals" : true
              }
            ],
        "Next" : "SuccessState" }],
        "Default" : "FailState"
      },
      "SuccessState" : {
        "Type" : "Succeed"
      },
      "FailState" : {
        "Type" : "Fail",
        "Cause" : "$.handler.results.errors"
      }
    }
  })

  depends_on = [
    aws_lambda_function.file_upload
  ]

}
