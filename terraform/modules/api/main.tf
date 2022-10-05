terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# ------------------------------------------------------
# Lambda Archive
# ------------------------------------------------------
# Create S3 Bucket to store different versions of the code
resource "aws_s3_bucket" "lambda_function_bucket" {
  bucket        = var.lambda_archive_s3_bucket
  force_destroy = var.force_destroy
}

# resource "aws_apigatewayv2_api" "example" {
#   name          = "bank-microservices-api"
#   protocol_type = "HTTP"
# }