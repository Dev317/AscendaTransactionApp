output "certificate_arn" {
  description = "Certificate ARN"
  value       = aws_acm_certificate.cert.arn
}
