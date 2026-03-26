resource "aws_dynamodb_table" "logs" {
  name         = "${var.project_prefix}-logs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "log_id"
  range_key    = "timestamp"

  attribute {
    name = "log_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  ttl {
    attribute_name = "expire_at"
    enabled        = true
  }

  tags = local.tags
}
