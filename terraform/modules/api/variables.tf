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