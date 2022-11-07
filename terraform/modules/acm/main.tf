terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# ------------------------------------------------------
# Certificate
# ------------------------------------------------------

# Certificate
resource "aws_acm_certificate" "cert" {
  domain_name               = "itsag1t1.com"
  subject_alternative_names = ["www.itsag1t1.com", "api.itsag1t1.com"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# CNAME records for DNS Validation
resource "aws_route53_record" "cert_validation_record" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.route53_hosted_zone_id
}

# AWS certificate validation
resource "aws_acm_certificate_validation" "cert_validation" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation_record : record.fqdn]
}
