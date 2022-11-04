resource "aws_budgets_budget" "under_10_USD" {
  name         = "Under 10 USD"
  budget_type  = "COST"
  limit_amount = "10"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
}

resource "aws_iam_group" "developers" {
  name = "developers"
}
resource "aws_iam_group_membership" "team" {
  name = "developers"
  users = [aws_iam_user.bradley.name,
    aws_iam_user.marcus.name,
    aws_iam_user.minh.name,
    aws_iam_user.michelle.name,
    aws_iam_user.jennifer.name,
  aws_iam_user.elizabeth.name]

  group = aws_iam_group.developers.name
}

resource "aws_iam_user" "bradley" {
  name = "bradley"
}

resource "aws_iam_user" "marcus" {
  name = "marcus"
}

resource "aws_iam_user" "minh" {
  name = "minh"
}
resource "aws_iam_user" "michelle" {
  name = "michelle"
}
resource "aws_iam_user" "jennifer" {
  name = "jennifer"
}
resource "aws_iam_user" "elizabeth" {
  name = "elizabeth"
}

resource "aws_iam_policy" "policy" {
  name        = "developer-policy"
  description = "Policy for all developers in g1t1"
  policy      = data.aws_iam_policy_document.developer_policy.json
}

resource "aws_iam_group_policy_attachment" "for-developers" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.policy.arn
}