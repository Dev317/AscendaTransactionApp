resource "aws_dynamodb_table" "campaign_service_table" {
  name           = "campaign_service_table"
  hash_key       = "campaign_id"
  read_capacity  = 30
  write_capacity = 30
  attribute {
    name = "campaign_id"
    type = "S"
  }
}


