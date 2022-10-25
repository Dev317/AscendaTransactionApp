output "base_url_campaign" {
  description = "Base URL for API Gateway for Campaign."
  value = aws_api_gateway_stage.campaign_prod_stage.invoke_url
}

output "base_url_calculation" {
  description = "Base URL for API Gateway for Calculation."
  value = aws_api_gateway_stage.calculation_prod_stage.invoke_url
}
