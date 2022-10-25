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
