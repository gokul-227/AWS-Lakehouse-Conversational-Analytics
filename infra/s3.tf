# Dataset Storage
resource "aws_s3_bucket" "datasets" {
  bucket        = "${var.project_prefix}-datasets-${var.environment}"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_versioning" "datasets" {
  bucket = aws_s3_bucket.datasets.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datasets" {
  bucket = aws_s3_bucket.datasets.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# Frontend Hosting
resource "aws_s3_bucket" "frontend" {
  bucket        = "${var.project_prefix}-frontend-${var.environment}"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowCloudFrontServicePrincipalReadOnly"
      Effect = "Allow"
      Principal = {
        Service = "cloudfront.amazonaws.com"
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.frontend.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
        }
      }
    }]
  })
}

# Athena Results
resource "aws_s3_bucket" "athena_results" {
  bucket        = "${var.project_prefix}-athena-results-${var.environment}"
  force_destroy = true
  tags          = local.tags
}
