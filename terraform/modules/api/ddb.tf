resource "aws_dynamodb_table" "campaign_service_table" {
  name      = "campaign_service_table"
  hash_key  = "card_type"
  range_key = "campaign_name"
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  billing_mode           = "PAY_PER_REQUEST"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true
  attribute {
    name = "card_type"
    type = "S"
  }

  attribute {
    name = "campaign_name"
    type = "S"
  }

  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "exclusion_service_table" {
  name         = "exclusion_service_table"
  hash_key     = "card_type"
  range_key    = "exclusion_name"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true

  attribute {
    name = "card_type"
    type = "S"
  }

  attribute {
    name = "exclusion_name"
    type = "S"
  }

  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "calculation_service_table" {
  name         = "calculation_service_table"
  hash_key     = "card_type"
  range_key    = "policy_date"
  billing_mode = "PAY_PER_REQUEST"
  
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true

  attribute {
    name = "card_type"
    type = "S"
  }

  attribute {
    name = "policy_date"
    type = "S"
  }

  replica {
    region_name = var.us_region
  }
}


resource "aws_dynamodb_table" "transaction_service_table" {
  name         = "transaction_service_table"
  hash_key     = "card_id"
  range_key    = "transaction_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true

  attribute {
    name = "card_id"
    type = "S"
  }

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
  hash_key     = "card_id"
  range_key    = "reward_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true

  attribute {
    name = "card_id"
    type = "S"
  }

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
  hash_key     = "card_group"
  range_key    = "card_type"
  billing_mode = "PAY_PER_REQUEST"
  table_class  = "STANDARD"
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true

  attribute {
    name = "card_group"
    type = "S"
  }

  attribute {
    name = "card_type"
    type = "S"
  }

  global_secondary_index {
    name               = "card_type-index"
    hash_key           = "card_type"
    projection_type    = "ALL"
  }

  replica {
    region_name = var.us_region
  }
}

resource "aws_dynamodb_table" "user_card_service_table" {
  name         = "user_service_table"
  hash_key     = "user_id"
  range_key    = "card_id"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery {
    enabled = true
  }
  restore_to_latest_time = true
  stream_view_type       = "KEYS_ONLY"
  count                  = data.aws_region.current.name == var.default_region ? 1 : 0
  stream_enabled         = true

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "card_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  global_secondary_index {
    name               = "email-index"
    hash_key           = "email"
    projection_type    = "ALL"
  }

  replica {
    region_name = var.us_region
  }
}



# resource "aws_dynamodb_table" "exclusion_index_table" {
#   name         = "exclusion_index_table"
#   hash_key     = "exclusion_index_id"
#   billing_mode = "PAY_PER_REQUEST"
#   # point_in_time_recovery = true
#   restore_to_latest_time = true
#   stream_view_type = "KEYS_ONLY"
#   count        = data.aws_region.current.name == var.default_region ? 1 : 0
#   stream_enabled = true

#   attribute {
#     name = "exclusion_index_id"
#     type = "S"
#   }
#   replica {
#     region_name = var.us_region
#   }
# }

# resource "aws_dynamodb_table" "campaign_index_table" {
#   name         = "campaign_index_table"
#   hash_key     = "campaign_index_id"
#   billing_mode = "PAY_PER_REQUEST"
#   # point_in_time_recovery = true
#   restore_to_latest_time = true
#   stream_view_type = "KEYS_ONLY"
#   count        = data.aws_region.current.name == var.default_region ? 1 : 0
#   stream_enabled = true

#   attribute {
#     name = "campaign_index_id"
#     type = "S"
#   }
#   replica {
#     region_name = var.us_region
#   }
# }
