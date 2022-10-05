# Configure AWS Provider
provider "aws" {
  alias  = "singapore"
  region = "ap-southeast-1"
}

provider "aws" {
  alias  = "northvirginia"
  region = "us-east-1"
}

# -----------------------------------
# Route 53 
# -----------------------------------

# resource "aws_route53_zone" "primary" {
#   name    = "itsag1t1.com"
#   comment = "Bradley"
# }

# -----------------------------------
# Global Configuration
# -----------------------------------
module "iam" {
  source = "./modules/iam"
}

module "frontend" {
  source       = "./modules/frontend"
  github_token = var.github_token
}

# -----------------------------------
# Singapore Configuration
# -----------------------------------
module "api_sg" {
  source = "./modules/api"
  providers = {
    aws = aws.singapore
  }
  lambda_archive_s3_bucket = "lambda-archive-g1t1-singapore"
  lambda_role               = module.iam.iam_lambda_role_arn
}

module "file_processor_sg" {
  source = "./modules/file-processor"
  providers = {
    aws = aws.singapore
  }
  file_upload_s3_bucket     = "file-upload-g1t1-singapore"
  lambda_role               = module.iam.iam_lambda_role_arn
  stepfunction_trigger_role = module.iam.iam_stepfunction_role_arn
}

# -----------------------------------
# North Virginia Configuration
# -----------------------------------
module "api_north_virginia" {
  source = "./modules/api"
  providers = {
    aws = aws.northvirginia
  }
  lambda_archive_s3_bucket = "lambda-archive-g1t1-north-virginia"
  lambda_role               = module.iam.iam_lambda_role_arn

}

module "file_processor_north_virginia" {
  source = "./modules/file-processor"
  providers = {
    aws = aws.northvirginia
  }
  file_upload_s3_bucket     = "file-upload-g1t1-north-virginia"
  lambda_role               = module.iam.iam_lambda_role_arn
  stepfunction_trigger_role = module.iam.iam_stepfunction_role_arn
}

# -----------------------------------
# Refactoring Blocks
# -----------------------------------
