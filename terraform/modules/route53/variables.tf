variable "route53_hosted_zone_id" {
  description = "Route 53 Hosted Zone ID"
  type        = string
}

# variable "amplify_endpoint" {
#   description = "Amplify Endpoint"
#   type        = string
# }

variable "apigw_domain_name_primary" {
  description = "Primary APIGW Domain Cloudfront Distribution Domain Name"
  type        = string
}

variable "apigw_zone_id_primary" {
  description = "Primary APIGW Domain Cloudfront Distribution Zone ID"
  type        = string
}

variable "apigw_endpoint_primary" {
  description = "Primary APIGW Invoke URL"
  type        = string
}

variable "apigw_domain_name_secondary" {
  description = "Secondary APIGW Domain Cloudfront Distribution Domain Name"
  type        = string
}

variable "apigw_zone_id_secondary" {
  description = "Secondary APIGW Domain Cloudfront Distribution Zone ID"
  type        = string
}

variable "apigw_endpoint_secondary" {
  description = "Secondary APIGW Invoke URL"
  type        = string
}