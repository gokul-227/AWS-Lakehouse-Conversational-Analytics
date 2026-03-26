resource "aws_athena_database" "main" {
  name   = "${replace(var.project_prefix, "-", "_")}_db"
  bucket = aws_s3_bucket.athena_results.id
}

resource "aws_athena_workgroup" "main" {
  name = "${var.project_prefix}-workgroup"
  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.id}/results/"
    }
    enforce_workgroup_configuration = false
  }
  force_destroy = true
  tags          = local.tags
}
