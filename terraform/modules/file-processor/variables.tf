variable "lambda_role" {
  description = "ARN of IAM lambda role"
  type        = string
  default     = "iam-lambda-role"
}

variable "stepfunction_trigger_role" {
  description = "Step Function Trigger IAM Role"
  type        = string
}

variable "force_destroy" {
  description = "Force deleting a resource"
  type        = bool
  default     = true
}

variable "file_upload_s3_bucket" {
  description = "S3 Bucket Name for File Uploads"
  type        = string
  default     = "file-upload-g1t1"
}

variable "csv_processor_zip" {
  description = "Location of CSV Processor Code"
  type        = string
  default     = "../build/csv_processor.zip"
}

variable "stepfunction_trigger_zip" {
  description = "Location of Step Function Trigger Code"
  type        = string
  default     = "../build/stepfunction_trigger.zip"
}



