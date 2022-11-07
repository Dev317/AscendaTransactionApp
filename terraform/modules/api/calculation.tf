# Endpoint with path "/calculation" for calculation lambda
resource "aws_api_gateway_resource" "calculation" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  parent_id   = aws_api_gateway_rest_api.orchestrator_apigw.root_resource_id
  path_part   = "calculation"
}

# Create S3 object that is zip file of Lambda code
resource "aws_s3_object" "calculation_code" {
  bucket = aws_s3_bucket.lambda_function_bucket.id
  key    = "calculation_service.zip"
  source = var.calculation_service_zip
}

# Create calculation Lambda function
resource "aws_lambda_function" "calculation_lambda" {
  function_name    = "calculation_service"
  role             = var.lambda_role
  handler          = "calculation_service.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda_function_bucket.id
  s3_key           = aws_s3_object.calculation_code.key
  source_code_hash = filebase64sha256(var.calculation_service_zip)
  runtime          = "python3.7"

  environment {
    variables = {
      APIG_URL = "https://${aws_api_gateway_rest_api.orchestrator_apigw.id}.execute-api.${var.apigw_region}.amazonaws.com/prod/"
    }
  }

  lifecycle {
    ignore_changes = [source_code_hash]
  }
}

# /POST for /calculation
resource "aws_api_gateway_method" "post_calculation" {
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id   = aws_api_gateway_resource.calculation.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integrate with API Gateway with Lambda function
resource "aws_api_gateway_integration" "post_calculation_lambda" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id = aws_api_gateway_resource.calculation.id
  http_method = aws_api_gateway_method.post_calculation.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.calculation_lambda.invoke_arn
}

# Permission to allow invoke Lambda function
resource "aws_lambda_permission" "apigw-post-calculation" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.calculation_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orchestrator_apigw.execution_arn}/*/POST/calculation"
}

# Deploy the endpoint as /prod/${resource}
resource "aws_api_gateway_deployment" "calculation_api_deployment" {
  depends_on = [ aws_api_gateway_integration.post_calculation_lambda ]

  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.calculation.id,
      aws_api_gateway_method.post_calculation.id,
      aws_api_gateway_integration.post_calculation_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  stage_name = "prod"
}
