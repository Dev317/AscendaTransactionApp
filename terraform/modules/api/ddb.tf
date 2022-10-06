resource "aws_dynamodb_table" "campaign_service_table" {
  name           = "campaign_service_table"
  hash_key       = "campaign_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "campaign_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "exclusion_service_table" {
  name           = "exclusion_service_table"
  hash_key       = "exclusion_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "exclusion_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "calculation_service_table" {
  name           = "calculation_service_table"
  hash_key       = "policy_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "policy_id"
    type = "S"
  }
}


resource "aws_dynamodb_table" "transaction_service_table" {
  name           = "transaction_service_table"
  hash_key       = "transaction_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "transaction_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "reward_service_table" {
  name           = "reward_service_table"
  hash_key       = "reward_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "reward_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "card_service_table" {
  name           = "card_service_table"
  hash_key       = "card_type_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "card_type_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "user_card_service_table" {
  name           = "user_card_service_table"
  hash_key       = "card_id"
  read_capacity  = var.read_capactiy
  write_capacity = var.write_capactiy
  attribute {
    name = "card_id"
    type = "S"
  }
}
