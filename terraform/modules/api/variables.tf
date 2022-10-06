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

variable "campaign_service_zip" {
  description = "Location of Campaign Service Code"
  type        = string
  default     = "../build/campaign_service.zip"
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