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
}