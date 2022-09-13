terraform {
  # Declares providers, so that Terraform can install and use them
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}