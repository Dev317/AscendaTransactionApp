output "base_url_campaign" {
  description = "Base URL for API Gateway for Campaign."
  value       = "${aws_api_gateway_deployment.campaign_api_deployment.invoke_url}/calculation"
}

output "base_url_calculation" {
  description = "Base URL for API Gateway for Calculation."
  value       = "${aws_api_gateway_deployment.calculation_api_deployment.invoke_url}/campaign"
}

output "base_url_exclusion" {
  description = "Base URL for API Gateway for Exclusion."
  value       = "${aws_api_gateway_deployment.exclusion_api_deployment.invoke_url}/exclusion"
}

output "base_url_health_check" {
  description = "Base URL for API Gateway for Health Check"
  value       = "${aws_api_gateway_deployment.health_api_deployment.invoke_url}/health"
}

output "base_url_user" {
  description = "Base URL for API Gateway for User"
  value       = "${aws_api_gateway_deployment.user_api_deployment.invoke_url}/user"
}

output "base_url_reward" {
  description = "Base URL for API Gateway for Reward"
  value       = "${aws_api_gateway_deployment.reward_api_deployment.invoke_url}/reward"
}

output "base_url_transaction" {
  description = "Base URL for API Gateway for Transaction"
  value       = "${aws_api_gateway_deployment.transaction_api_deployment.invoke_url}/transaction"
}

output "apigw_domain_name" {
  description = "APIGW Domain Cloudfront Distribution Domain Name"
  value       = aws_api_gateway_domain_name.apigw_domain.regional_domain_name
}

output "apigw_zone_id" {
  description = "APIGW Domain Cloudfront Distribution Zone ID"
  value       = aws_api_gateway_domain_name.apigw_domain.regional_zone_id
}
