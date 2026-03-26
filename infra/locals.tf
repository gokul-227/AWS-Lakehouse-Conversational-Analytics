locals {
  tags = {
    Project     = var.project_prefix
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
