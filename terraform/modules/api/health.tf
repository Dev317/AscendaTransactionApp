# Endpoint with path "/health" for health lambda
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  parent_id   = aws_api_gateway_rest_api.orchestrator_apigw.root_resource_id
  path_part   = "health"
}

# Create S3 object that is zip file of Lambda code
resource "aws_s3_object" "health_code" {
  bucket = aws_s3_bucket.lambda_function_bucket.id
  key    = "health_check.zip"
  source = var.health_check_zip
}

# Create health check Lambda function
resource "aws_lambda_function" "health_lambda" {
  function_name    = "health_check"
  role             = var.lambda_role
  handler          = "health_check.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda_function_bucket.id
  s3_key           = aws_s3_object.health_code.key
  source_code_hash = filebase64sha256(var.health_check_zip)
  runtime          = "python3.7"

  environment {
    variables = {
      STATUS = "ok"
    }
  }

  lifecycle {
    ignore_changes = [
      source_code_hash
    ]
  }
}

# /GET for /health
resource "aws_api_gateway_method" "health_check" {
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

# Integrate with API Gateway with Lambda function
resource "aws_api_gateway_integration" "health_check_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id             = aws_api_gateway_method.health_check.resource_id
  http_method             = aws_api_gateway_method.health_check.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.health_lambda.invoke_arn
}

# Permission to allow invoke Lambda function
resource "aws_lambda_permission" "apigw-health-check" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orchestrator_apigw.execution_arn}/*/GET/health"
}


# Deploy the endpoint as /prod/${resource}
resource "aws_api_gateway_deployment" "health_api_deployment" {
  depends_on = [aws_api_gateway_integration.health_check_lambda]

  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.health.id,
      aws_api_gateway_method.health_check.id,
      aws_api_gateway_integration.health_check_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  stage_name = "prod"
}
