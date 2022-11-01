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
  value = module.api_sg.base_url_calculation
}

output "base_url_calculation_us" {
  description = "Base URL for API Gateway for Calculation in US."
  value = module.api_north_virginia.base_url_calculation
}

output "base_url_exclusion_sg" {
  description = "Base URL for API Gateway for Exclusion in SG."
  value = module.api_sg.base_url_exclusion
}

output "base_url_exclusion_us" {
  description = "Base URL for API Gateway for Exclusion in US."
  value = module.api_north_virginia.base_url_exclusion
}

output "base_url_user_sg" {
  description = "Base URL for API Gateway for User in SG."
  value = module.api_sg.base_url_user
}

output "base_url_reward_sg" {
  description = "Base URL for API Gateway for Reward in SG."
  value = module.api_sg.base_url_reward
}

output "base_url_transaction_sg" {
  description = "Base URL for API Gateway for Transaction in SG."
  value = module.api_sg.base_url_transaction
}

output "base_url_user_us" {
  description = "Base URL for API Gateway for User in US."
  value = module.api_north_virginia.base_url_user
}

output "base_url_reward_us" {
  description = "Base URL for API Gateway for Reward in US."
  value = module.api_north_virginia.base_url_reward
}

output "base_url_transaction_us" {
  description = "Base URL for API Gateway for Transaction in US."
  value = module.api_north_virginia.base_url_transaction
}