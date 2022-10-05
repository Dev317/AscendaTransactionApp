terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# ------------------------------------------------------
# S3 Bucket
# ------------------------------------------------------

# S3 bucket to store the zip files of lambda codes
resource "aws_s3_bucket" "lambda_function_bucket" {
  bucket        = var.lambda_archive_s3_bucket
  force_destroy = var.force_destroy
}


# ------------------------------------------------------
# API Gateway
# ------------------------------------------------------

# Orchestrator API Gateway
resource "aws_api_gateway_rest_api" "orchestrator_apigw" {
  name        = "orchestrator_apigw"
  description = "Orchestrator API Gateway"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Endpoint with path "/campaign" for campaign lambda
resource "aws_api_gateway_resource" "campaign" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  parent_id   = aws_api_gateway_rest_api.orchestrator_apigw.root_resource_id
  path_part   = "campaign"
}
