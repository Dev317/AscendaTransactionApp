output "iam_stepfunction_role_arn" {
    value = aws_iam_role.iam_stepfunction_role.arn
    description = "ARN of Stepfunction Role"
}

output "iam_lambda_role_arn" {
    value = aws_iam_role.iam_lambda_role.arn
    description = "ARN of Lambda Role"
}