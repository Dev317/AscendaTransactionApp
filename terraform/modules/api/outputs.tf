output "base_url" {
  description = "Base URL for API Gateway for Campaign."
  value = aws_api_gateway_stage.campaign_prod_stage.invoke_url
}
