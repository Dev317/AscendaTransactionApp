variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "lambda_role" {
  description = "Name of IAM lambda role"
  type        = string
  default     = "iam-lambda-role"
}

variable "force_destroy" {
  description = "Force deleting a resource"
  type = bool
  default = true
}