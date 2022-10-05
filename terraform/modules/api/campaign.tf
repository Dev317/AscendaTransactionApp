# ------------------------------------------------------
# DynamoDB Table
# ------------------------------------------------------

resource "aws_dynamodb_table" "exclusions" {
  name           = "exclusions"
  hash_key       = "exclusion_id"
  read_capacity  = 30
  write_capacity = 30
  attribute {
    name = "exclusion_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "campaign_service_table" {
  name           = "campaign_service_table"
  hash_key       = "campaign_id"
  read_capacity  = 30
  write_capacity = 30
  attribute {
    name = "campaign_id"
    type = "S"
  }
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



# ------------------------------------------------------
# API Gateway Endpoint
# ------------------------------------------------------

# /POST for /campaign
resource "aws_api_gateway_method" "create_campaign" {
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id   = aws_api_gateway_resource.campaign.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integrate with API Gateway with Lambda function
resource "aws_api_gateway_integration" "create_campaign_lambda" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id = aws_api_gateway_method.create_campaign.resource_id
  http_method = aws_api_gateway_method.create_campaign.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.campaign_lambda.invoke_arn
}

# Permission to allow invoke Lambda function
resource "aws_lambda_permission" "apigw-create-campaign" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.campaign_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.orchestrator_apigw.execution_arn}/*/POST/campaign"
}

# Deploy the endpoint as /prod/${resource}
resource "aws_api_gateway_deployment" "campaign_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.create_campaign_lambda
  ]

  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.campaign.id,
      aws_api_gateway_method.create_campaign.id,
      aws_api_gateway_integration.create_campaign_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "campaign_prod_stage" {
  deployment_id = aws_api_gateway_deployment.campaign_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  stage_name    = "prod"
}
