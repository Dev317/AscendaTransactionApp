resource "aws_dynamodb_table" "scis-freedom-campaign" {
  name           = "scis-freedom-campaign"
  hash_key       = "campaign_id"
  read_capacity  = 30
  write_capacity = 30
  attribute {
    name = "campaign_id"
    type = "S"
  }
}

resource "aws_dynamodb_table_item" "test" {
  table_name = aws_dynamodb_table.scis-freedom-campaign.name
  hash_key   = aws_dynamodb_table.scis-freedom-campaign.hash_key

  item = <<ITEM
{ 
 "campaign_id": {"S": "scis-freedom-campaign-test"},
 "campaign_start_date": {"S": "01-01-2020"},
 "campaign_end_date": {"S": "31-12-2025"},
 "card_type": {"S": "scis_freedom"}
}
ITEM
}


