resource "aws_lambda_function" "api" {
  function_name    = "${var.project_prefix}-api"
  role             = aws_iam_role.lambda.arn
  package_type     = "Image"
  image_uri        = var.lambda_image_uri
  architectures    = ["arm64"]
  timeout          = 60
  memory_size      = 512

  dynamic "vpc_config" {
    for_each = var.vpc_id != "" ? [1] : []
    content {
      subnet_ids         = var.subnet_ids
      security_group_ids = [aws_security_group.lambda[0].id]
    }
  }

  environment {
    variables = {
      ENVIRONMENT          = var.environment
      S3_BUCKET_NAME       = aws_s3_bucket.datasets.id
      ATHENA_DATABASE      = aws_athena_database.main.name
      ATHENA_WORKGROUP     = aws_athena_workgroup.main.name
      ATHENA_RESULTS_BUCKET = aws_s3_bucket.athena_results.id
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
      COGNITO_CLIENT_ID     = aws_cognito_user_pool_client.main.id
      DYNAMODB_LOG_TABLE    = aws_dynamodb_table.logs.name
      SNS_TOPIC_ARN         = aws_sns_topic.alerts.arn
      CORS_ORIGINS          = "https://${aws_cloudfront_distribution.frontend.domain_name}"
    }
  }

  tags = local.tags
}

resource "aws_security_group" "lambda" {
  count       = var.vpc_id != "" ? 1 : 0
  name        = "${var.project_prefix}-lambda-sg"
  description = "Security group for Lakehouse Lambda"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

variable "lambda_image_uri" {
  description = "ECR image URI for Lambda"
  type        = string
}
