output "route53_apigw_health_check" {
  description = "Route 53 API Gateway Health Check"
  value       = aws_route53_health_check.apigw_health_check.id
}
