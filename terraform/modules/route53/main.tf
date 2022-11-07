terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Primary zone
# resource "aws_route53_zone" "primary" {
#   name    = "itsag1t1.com"
#   comment = "Primary hosted zone"
# }

# ------------------------------------------------------
# Primary Resources - ap-southeast-1
# ------------------------------------------------------

# Primary health check
resource "aws_route53_health_check" "apigw_health_check_primary" {
  failure_threshold = "5"
  fqdn              = replace(var.apigw_endpoint_primary, "/(https://)|(/prod)/", "")
  port              = 443
  request_interval  = "30"
  resource_path     = "/prod/health"
  search_string     = "ok"
  type              = "HTTPS_STR_MATCH"

  tags = {
    Name = "apigw-primary-health-check"
  }
}

# Primary APIGW Domain Record
resource "aws_route53_record" "api_primary" {
  zone_id        = var.route53_hosted_zone_id
  name           = "api.itsag1t1.com"
  type           = "A"
  set_identifier = "primary"

  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = var.apigw_domain_name_primary
    zone_id                = var.apigw_zone_id_primary
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.apigw_health_check_primary.id
}


# ------------------------------------------------------
# Secondary Resources - us-east-1
# ------------------------------------------------------
# Secondary health check
resource "aws_route53_health_check" "apigw_health_check_secondary" {
  failure_threshold = "5"
  fqdn              = replace(var.apigw_endpoint_secondary, "/(https://)|(/prod)/", "")
  port              = 443
  request_interval  = "30"
  resource_path     = "/prod/health"
  search_string     = "ok"
  type              = "HTTPS_STR_MATCH"

  tags = {
    Name = "apigw-secondary-health-check"
  }
}

# Secondary APIGW Domain Record
resource "aws_route53_record" "api_secondary" {
  zone_id        = var.route53_hosted_zone_id
  name           = "api.itsag1t1.com"
  type           = "A"
  set_identifier = "secondary"

  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = var.apigw_domain_name_secondary
    zone_id                = var.apigw_zone_id_secondary
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.apigw_health_check_secondary.id
}
