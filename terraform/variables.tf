variable "github_token" {
  description = "Github access token"
  type        = string
  sensitive   = true
}

variable "route53_hosted_zone_id" {
  description = "Route 53 Hosted Zone ID"
  type        = string
  default     = "Z089272719LULOG2M18OT"
}
