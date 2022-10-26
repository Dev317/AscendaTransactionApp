# Endpoint with path "/exclusion" for exclusion lambda
resource "aws_api_gateway_resource" "exclusion" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  parent_id   = aws_api_gateway_rest_api.orchestrator_apigw.root_resource_id
  path_part   = "exclusion"
}

# Create S3 object that is zip file of Lambda code
resource "aws_s3_object" "exclusion_code" {
  bucket = aws_s3_bucket.lambda_function_bucket.id
  key    = "exclusion_service.zip"
  source = var.exclusion_service_zip
}

# Create exclusion Lambda function
resource "aws_lambda_function" "exclusion_lambda" {
  function_name    = "exclusion_service_posting"
  role             = var.lambda_role
  handler          = "exclusion_service.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda_function_bucket.id
  s3_key           = aws_s3_object.exclusion_code.key
  source_code_hash = filebase64sha256(var.exclusion_service_zip)
  runtime          = "python3.7"

  environment {
    variables = {
      APIG_URL = "https://${aws_api_gateway_rest_api.orchestrator_apigw.id}.execute-api.${var.apigw_region}.amazonaws.com/prod"
    }
  }
}

# /POST for /campaign
resource "aws_api_gateway_method" "create_exclusion" {
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id   = aws_api_gateway_resource.exclusion.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integrate with API Gateway with Lambda function
resource "aws_api_gateway_integration" "create_exclusion_lambda" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id = aws_api_gateway_method.create_exclusion.resource_id
  http_method = aws_api_gateway_method.create_exclusion.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.exclusion_lambda.invoke_arn
}

# Permission to allow invoke Lambda function
resource "aws_lambda_permission" "apigw-create-exclusion" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.exclusion_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.orchestrator_apigw.execution_arn}/*/POST/exclusion"
}


# Deploy the endpoint as /prod/${resource}
resource "aws_api_gateway_deployment" "exclusion_api_deployment" {
  depends_on = [ aws_api_gateway_integration.create_exclusion_lambda ]

  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.campaign.id,
      aws_api_gateway_method.create_exclusion.id,
      aws_api_gateway_integration.create_exclusion_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  stage_name = "prod"
}
