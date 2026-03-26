variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "lakechat"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "alert_email" {
  description = "Email address for SNS notifications"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for Lambda"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for Lambda"
  type        = list(string)
  default     = []
}

