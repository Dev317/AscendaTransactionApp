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
