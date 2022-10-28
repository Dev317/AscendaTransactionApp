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

resource "aws_api_gateway_base_path_mapping" "apigw_path_mapping" {
  api_id      = aws_api_gateway_rest_api.orchestrator_apigw.id
  stage_name  = "prod"
  domain_name = aws_api_gateway_domain_name.apigw_domain.domain_name
}


# API Gateway Domain
resource "aws_api_gateway_domain_name" "apigw_domain" {
  regional_certificate_arn = var.certificate_arn
  domain_name              = "api.itsag1t1.com"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
