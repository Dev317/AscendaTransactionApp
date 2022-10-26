output "base_url_campaign" {
  description = "Base URL for API Gateway for Campaign."
  value = aws_api_gateway_deployment.campaign_api_deployment.invoke_url
}

output "base_url_calculation" {
  description = "Base URL for API Gateway for Calculation."
  value = aws_api_gateway_deployment.calculation_api_deployment.invoke_url
}

output "base_url_exclusion" {
  description = "Base URL for API Gateway for Exclusion."
  value = aws_api_gateway_deployment.exclusion_api_deployment.invoke_url
}
