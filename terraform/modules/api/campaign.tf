resource "aws_dynamodb_table" "exclusions" {
  name           = "exclusions"
  hash_key       = "exclusion_id"
  read_capacity  = 30
  write_capacity = 30
  attribute {
    name = "exclusion_id"
    type = "S"
  }
}