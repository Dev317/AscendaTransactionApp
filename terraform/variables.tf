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

variable "key_id" {
  description = "AWS key id"
  type        = string
  sensitive   = true
}

variable "secret" {
  description = "AWS secret"
  type        = string
  sensitive   = true
}
