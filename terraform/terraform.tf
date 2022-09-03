terraform {
  # Declares providers, so that Terraform can install and use them
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.28"
    }

    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.2.0"
    }
  }

  # Where Terraform stores its state to keep track of resources it manages
  backend "s3" {
    bucket = "<unique_bucket_name>"
    key    = "terraform.tfstate"
    region = "ap-southeast-1"
  }
}