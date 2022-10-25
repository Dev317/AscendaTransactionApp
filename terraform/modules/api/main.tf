terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

data "aws_region" "current" {}


# ------------------------------------------------------
# S3 Bucket
# ------------------------------------------------------

# S3 bucket to store the zip files of lambda codes
resource "aws_s3_bucket" "lambda_function_bucket" {
  bucket        = var.lambda_archive_s3_bucket
  force_destroy = var.force_destroy
}




# ------------------------------------------------------
# Lambda function
# ------------------------------------------------------

# Create S3 object that is zip file of Lambda code
resource "aws_s3_object" "campaign_code" {
  bucket = aws_s3_bucket.lambda_function_bucket.id
  key    = "campaign_service.zip"
  source = var.campaign_service_zip
}

# Create campaign Lambda function
resource "aws_lambda_function" "campaign_lambda" {
  function_name = "campaign_service_posting"
  role          = var.lambda_role
  handler       = "campaign_service.lambda_handler"
  s3_bucket = aws_s3_bucket.lambda_function_bucket.id
  s3_key    = aws_s3_object.campaign_code.key
  source_code_hash = filebase64sha256(var.campaign_service_zip)
  runtime = "python3.8"
}

