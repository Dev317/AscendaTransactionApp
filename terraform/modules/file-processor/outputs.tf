output "transactions_queue_url" {
  description = "URL of Transactions SQS Queue"
  value       = aws_sqs_queue.transactions_queue.url
}

output "transactions_queue_arn" {
  description = "ARN of Transactions SQS Queue"
  value       = aws_sqs_queue.transactions_queue.arn
}
