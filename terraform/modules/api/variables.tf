variable "default_region" {
  description = "The region to deploy the DynamoDB global main table to"
  type        = string
  default     = "ap-southeast-1"
}

variable "us_region" {
  description = "The region to deploy the DynamoDB global table replicas to"
  type        = string
  default     = "us-east-1"
}

variable "apigw_region" {
  description = "The name of region that the api gateway is hosted"
  type        = string
  default     = ""
}

variable "lambda_archive_s3_bucket" {
  description = "S3 Bucket Name for Lambda ZIP Files"
  type        = string
  default     = "lambda-archive-g1t1"
}

variable "force_destroy" {
  description = "Force deleting a resource"
  type        = bool
  default     = true
}

variable "lambda_role" {
  description = "ARN of IAM lambda role"
  type        = string
  default     = "iam-lambda-role"
}


variable "read_capactiy" {
  description = "Read Capacity for DynamoDB"
  type        = number
  default     = 30
}


variable "write_capactiy" {
  description = "Write Capacity for DynamoDB"
  type        = number
  default     = 30
}


variable "campaign_service_zip" {
  description = "Location of Campaign Service Code"
  type        = string
  default     = "../build/campaign_service.zip"
}

variable "calculation_service_zip" {
  description = "Location of Calculation Service Code"
  type        = string
  default     = "../build/calculation_service.zip"
}

variable "exclusion_service_zip" {
  description = "Location of Exclusion Service Code"
  type        = string
  default     = "../build/exclusion_service.zip"
}

variable "health_check_zip" {
  description = "Location of Health Check Code"
  type        = string
  default     = "../build/health_check.zip"
}

variable "user_service_zip" {
  description = "Location of User Service Code"
  type        = string
  default     = "../build/user_service.zip"
}

variable "reward_service_zip" {
  description = "Location of Reward Service Code"
  type        = string
  default     = "../build/reward_service.zip"
}

variable "transaction_service_zip" {
  description = "Location of Transaction Service Code"
  type        = string
  default     = "../build/transaction_service.zip"
}

variable "certificate_arn" {
  description = "ACM Certificate ARN"
  type        = string
}

variable "route53_hosted_zone_id" {
  description = "Route 53 Hosted Zone ID"
  type        = string
}

variable "transactions_queue_arn" {
  description = "Transactions Queue ARN"
  type        = string
}

variable "key_id" {
  description = "AWS key id"
  type        = string
}

variable "secret" {
  description = "AWS secret"
  type        = string
}
