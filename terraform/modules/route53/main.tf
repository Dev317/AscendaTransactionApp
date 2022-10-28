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

# Create Route 53 Health Check
resource "aws_route53_health_check" "apigw_health_check" {
  failure_threshold = "5"
  fqdn              = "api.itsag1t1.com"
  port              = 443
  request_interval  = "30"
  resource_path     = "/health"
  search_string     = "ok"
  type              = "HTTPS_STR_MATCH"
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

  health_check_id = aws_route53_health_check.apigw_health_check.id
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

  health_check_id = aws_route53_health_check.apigw_health_check.id
}
