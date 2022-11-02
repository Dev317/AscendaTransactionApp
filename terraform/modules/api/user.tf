# Endpoint with path "/user" for user lambda
resource "aws_api_gateway_resource" "user" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  parent_id   = aws_api_gateway_rest_api.orchestrator_apigw.root_resource_id
  path_part   = "user"
}

# Create S3 object that is zip file of Lambda code
resource "aws_s3_object" "user_code" {
  bucket = aws_s3_bucket.lambda_function_bucket.id
  key    = "user_service.zip"
  source = var.user_service_zip
}

# Create user Lambda function
resource "aws_lambda_function" "user_lambda" {
  function_name    = "user_service"
  role             = var.lambda_role
  handler          = "user_service.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda_function_bucket.id
  s3_key           = aws_s3_object.user_code.key
  source_code_hash = filebase64sha256(var.user_service_zip)
  runtime          = "python3.7"

  environment {
    variables = {
      APIG_URL = "https://${aws_api_gateway_rest_api.orchestrator_apigw.id}.execute-api.${var.apigw_region}.amazonaws.com/prod"
    }
  }

  lifecycle {
    ignore_changes = [source_code_hash]
  }
}

# /POST for /user
resource "aws_api_gateway_method" "create_user" {
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id   = aws_api_gateway_resource.user.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integrate with API Gateway with Lambda function
resource "aws_api_gateway_integration" "create_user_lambda" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id = aws_api_gateway_resource.user.id
  http_method = aws_api_gateway_method.create_user.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.user_lambda.invoke_arn
}

# Permission to allow invoke Lambda function
resource "aws_lambda_permission" "apigw-create-user" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.user_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.orchestrator_apigw.execution_arn}/*/POST/user"
}


# Deploy the endpoint as /prod/${resource}
resource "aws_api_gateway_deployment" "user_api_deployment" {
  depends_on = [ aws_api_gateway_integration.create_user_lambda ]

  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.user.id,
      aws_api_gateway_method.create_user.id,
      aws_api_gateway_integration.create_user_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  stage_name = "prod"
}
