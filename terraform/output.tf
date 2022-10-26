output "s3_bucket_arn" {
  value       = aws_s3_bucket.terraform_state.arn
  description = "The ARN of the S3 bucket"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "The name of the DynamoDB table"
}

output "base_url_campaign_sg" {
  description = "Base URL for API Gateway for Campaign in SG."
  value = module.api_sg.base_url_campaign
}

output "base_url_campaign_us" {
  description = "Base URL for API Gateway for Campaign in US."
  value = module.api_north_virginia.base_url_campaign
}

output "base_url_calculation_sg" {
  description = "Base URL for API Gateway for Calculation in SG."
  value = module.api_sg.calculation_api_deployment
}

output "base_url_calculation_us" {
  description = "Base URL for API Gateway for Calculation in US."
  value = module.api_north_virginia.calculation_api_deployment
}