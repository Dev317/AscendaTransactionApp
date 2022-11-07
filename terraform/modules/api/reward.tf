# Endpoint with path "/reward" for reward lambda
resource "aws_api_gateway_resource" "reward" {
  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id
  parent_id   = aws_api_gateway_rest_api.orchestrator_apigw.root_resource_id
  path_part   = "reward"
}

# Create S3 object that is zip file of Lambda code
resource "aws_s3_object" "reward_code" {
  bucket = aws_s3_bucket.lambda_function_bucket.id
  key    = "reward_service.zip"
  source = var.reward_service_zip
}

# Create reward Lambda function
resource "aws_lambda_function" "reward_lambda" {
  function_name    = "reward_service"
  role             = var.lambda_role
  handler          = "reward_service.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda_function_bucket.id
  s3_key           = aws_s3_object.reward_code.key
  source_code_hash = filebase64sha256(var.reward_service_zip)
  runtime          = "python3.7"
  timeout          = 180

  environment {
    variables = {
      APIG_URL = "https://${aws_api_gateway_rest_api.orchestrator_apigw.id}.execute-api.${var.apigw_region}.amazonaws.com/prod/"
      AWS_KEY_ID = "${var.key_id}"
      AWS_SECRET = "${var.secret}"
      SRC_EMAIL_ADDRESS="test@marcu.sg"
    }
  }

  lifecycle {
    ignore_changes = [source_code_hash]
  }
}

# /POST for /reward
resource "aws_api_gateway_method" "create_reward" {
  rest_api_id   = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id   = aws_api_gateway_resource.reward.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integrate with API Gateway with Lambda function
resource "aws_api_gateway_integration" "create_reward_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.orchestrator_apigw.id
  resource_id             = aws_api_gateway_resource.reward.id
  http_method             = aws_api_gateway_method.create_reward.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.reward_lambda.invoke_arn
}

# Permission to allow invoke Lambda function
resource "aws_lambda_permission" "apigw-create-reward" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reward_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orchestrator_apigw.execution_arn}/*/POST/reward"
}


# Deploy the endpoint as /prod/${resource}
resource "aws_api_gateway_deployment" "reward_api_deployment" {
  depends_on = [aws_api_gateway_integration.create_reward_lambda]

  rest_api_id = aws_api_gateway_rest_api.orchestrator_apigw.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.reward.id,
      aws_api_gateway_method.create_reward.id,
      aws_api_gateway_integration.create_reward_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  stage_name = "prod"
}
