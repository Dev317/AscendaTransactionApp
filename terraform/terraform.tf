terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket         = "waftech-terraform-state"
    key            = "terraform.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "Waftech-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
    alias = "jakarta"
  region = "ap-southeast-3"
}