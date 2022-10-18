resource "aws_dynamodb_table" "campaign_service_table" {
  name     = "campaign_service_table"
  hash_key = "campaign_id"
  point_in_time_recovery = true
  restore_to_latest_time = true
  billing_mode = "PAY_PER_REQUEST"
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true
  attribute {
    name = "campaign_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "exclusion_service_table" {
  name         = "exclusion_service_table"
  hash_key     = "exclusion_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery = true
  restore_to_latest_time = true
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true

  attribute {
    name = "exclusion_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "calculation_service_table" {
  name         = "calculation_service_table"
  hash_key     = "policy_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery = true
  restore_to_latest_time = true
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true

  attribute {
    name = "policy_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}


resource "aws_dynamodb_table" "transaction_service_table" {
  name         = "transaction_service_table"
  hash_key     = "transaction_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery = true
  restore_to_latest_time = true
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true

  attribute {
    name = "transaction_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "reward_service_table" {
  name         = "reward_service_table"
  hash_key     = "reward_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery = true
  restore_to_latest_time = true
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true

  attribute {
    name = "reward_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "card_service_table" {
  name         = "card_service_table"
  hash_key     = "card_type_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery = true
  restore_to_latest_time = true
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true

  attribute {
    name = "card_type_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "user_card_service_table" {
  name         = "user_card_service_table"
  hash_key     = "card_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery = true
  restore_to_latest_time = true
  count        = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled = true

  attribute {
    name = "card_id"
    type = "S"
  }
  replica {
    region_name = var.us_region
  }
}
