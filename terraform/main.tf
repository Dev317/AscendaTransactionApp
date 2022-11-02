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


module "route53" {
  source                      = "./modules/route53"
  route53_hosted_zone_id      = var.route53_hosted_zone_id
  apigw_domain_name_primary   = module.api_sg.apigw_domain_name
  apigw_zone_id_primary       = module.api_sg.apigw_zone_id
  apigw_endpoint_primary      = module.api_sg.apigw_base_url
  apigw_domain_name_secondary = module.api_north_virginia.apigw_domain_name
  apigw_zone_id_secondary     = module.api_north_virginia.apigw_zone_id
  apigw_endpoint_secondary    = module.api_north_virginia.apigw_base_url
}

# -----------------------------------
# Singapore Configuration
# -----------------------------------

module "acm_sg" {
  source = "./modules/acm"
  providers = {
    aws = aws.singapore
  }
  route53_hosted_zone_id = var.route53_hosted_zone_id
}


module "api_sg" {
  source = "./modules/api"
  providers = {
    aws = aws.singapore
  }
  lambda_archive_s3_bucket = "lambda-archive-g1t1-singapore"
  lambda_role              = module.iam.iam_lambda_role_arn
  apigw_region             = "ap-southeast-1"
  certificate_arn          = module.acm_sg.certificate_arn
  route53_hosted_zone_id   = var.route53_hosted_zone_id
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

module "frontend_sg" {
  source = "./modules/frontend"
  providers = {
    aws = aws.singapore
  }
  github_token   = var.github_token
  waftech_region = "ap-southeast-1"
  waftech_branch = "fe-ap-se-1"
}

# -----------------------------------
# North Virginia Configuration
# -----------------------------------
module "acm_north_virginia" {
  source = "./modules/acm"
  providers = {
    aws = aws.northvirginia
  }
  route53_hosted_zone_id = var.route53_hosted_zone_id
}

module "api_north_virginia" {
  source = "./modules/api"
  providers = {
    aws = aws.northvirginia
  }
  lambda_archive_s3_bucket = "lambda-archive-g1t1-north-virginia"
  lambda_role              = module.iam.iam_lambda_role_arn
  apigw_region             = "us-east-1"
  certificate_arn          = module.acm_north_virginia.certificate_arn
  route53_hosted_zone_id   = var.route53_hosted_zone_id
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

module "frontend_north_virginia" {
  source = "./modules/frontend"
  providers = {
    aws = aws.northvirginia
  }
  github_token   = var.github_token
  waftech_region = "us-east-1"
  waftech_branch = "fe-us-east-1"
}


# -----------------------------------
# Refactoring Blocks
# -----------------------------------
# 27/10/2022 - split ACM into a separate module
moved {
  from = module.route53.aws_acm_certificate.cert
  to   = module.acm_sg.aws_acm_certificate.cert
}

moved {
  from = module.route53.aws_route53_record.cert_validation_record
  to   = module.acm_sg.aws_route53_record.cert_validation_record
}

moved {
  from = module.route53.aws_acm_certificate_validation.cert_validation
  to   = module.acm_sg.aws_acm_certificate_validation.cert_validation
}
