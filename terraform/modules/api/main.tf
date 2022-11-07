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
